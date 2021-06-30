import secrets
import string
import random
import json

from firebase_admin import firestore


async def handle(db, message):
    opt = message.content.split(" ")[1:]
    out = f"{message.author.name} | "

    if opt[0] == "init":
        out += init_status(db=db, id=message.author.id)
    elif opt[0] == "start":
        out += start_game(db=db, id=message.author.id)
    elif opt[0] in ["high", "low"]:
        out += play_game(db, message.author.id, opt[0])
    elif opt[0] == "exit":
        out += exit_game(db, message.author.id)
    elif opt[0] == "info":
        out += info_game()
    elif opt[0] == "status":
        out += status_game(db, message.author.id)
    else:
        out += "That command cannot be found"

    if out:
        await message.channel.send(out)


def check_if_user_in_game(db, id):
    """
    Tells whether a user is in-game or haven't started

    Returns:
        ([bool]: [ingame or not], [string]: [error message])
    """
    doc = db.collection(f"hi-lo/data/{id}").document("status").get()

    if doc.exists:
        doc = doc.to_dict()
        return ("ingame" in doc and doc["ingame"], "Game not started")
    else:
        return (False, "Account not created")


def create_status_doc(db, id):
    db.collection(f"hi-lo/data/{id}").document("status").set(
        {"ingame": False, "total_games": 0, "streak": {"best": 0, "last": 0},},
        merge=True,
    )


def init_status(db, id):
    doc = db.collection(f"hi-lo/data/{id}").document("status").get()

    if not doc.exists:
        create_status_doc(db, id)
        return "Account created"
    else:
        return "Account already exists"


def start_game(db, id):
    if check_if_user_in_game(db, id)[0]:
        return "Already in-game"

    new_card = Card.create()

    game_ref = db.collection(f"hi-lo/data/{id}").document()
    game_ref.set({"num_correct": 0, "moves": [new_card.to_dict()]})

    game_id = game_ref.id
    db.collection(f"hi-lo/data/{id}").document("status").update(
        {
            "ingame": True,
            "current_game": game_id,
            "games": firestore.ArrayUnion([game_id]),
        }
    )

    return f"Game created! Card: {new_card}"


def play_game(db, id, choice):
    ingame, err = check_if_user_in_game(db, id)

    if not ingame:
        return err

    game_id = find_game(db, id)

    doc = db.collection(f"hi-lo/data/{id}").document(game_id).get()

    if doc.exists:
        doc = doc.to_dict()
        new_card = Card.create()

        old_card = Card.from_dict(doc["moves"][-1])

        comparison = old_card.compare(new_card)
        choice = -1 if choice == "high" else 1
        if comparison == choice:
            db.collection(f"hi-lo/data/{id}").document(game_id).update(
                {
                    "num_correct": firestore.Increment(1),
                    "moves": firestore.ArrayUnion([new_card.to_dict()]),
                }
            )
            return f"Ding ding! You got it right! Card was {new_card}"
        else:

            transaction = db.transaction()
            status_ref = db.collection(f"hi-lo/data/{id}").document("status")

            @firestore.transactional
            def update_status_in_transaction(transaction, status_ref):
                snapshot = status_ref.get(transaction=transaction)
                transaction.update(
                    status_ref,
                    {
                        "ingame": False,
                        "streak.last": doc["num_correct"],
                        "streak.best": max(
                            doc["num_correct"], snapshot.get("streak.best")
                        ),
                        "total_games": firestore.Increment(1),
                    },
                )

            update_status_in_transaction(transaction, status_ref)

            return f"You got it wrong! You got a {doc['num_correct']} win-streak. Card was {new_card}"
    else:
        raise Exception("Game not found")


def find_game(db, id):
    doc = db.collection(f"hi-lo/data/{id}").document("status").get()

    if doc.exists:
        doc = doc.to_dict()
        if "current_game" in doc and "ingame" in doc and doc["ingame"]:
            return doc["current_game"]
        else:
            return "Current game not found"
    else:
        raise Exception(f"Status not found")


def exit_game(db, id):
    doc = db.collection(f"hi-lo/data/{id}").document("status").get()

    if doc.exists:
        doc = doc.to_dict()
        if "ingame" in doc:
            if doc["ingame"]:
                db.collection(f"hi-lo/data/{id}").document("status").update(
                    {"ingame": False}
                )
                return "Exited Game"
            else:
                return "Not in Game"
        else:
            raise Exception("InGame status not found")
    else:
        raise Exception("Status not found")


def status_game(db, id):
    doc = db.collection(f"hi-lo/data/{id}").document("status").get()

    if doc.exists:
        doc = doc.to_dict()
        return f"Best: {doc['streak']['best']} | Last: {doc['streak']['last']} | Total games: {doc['total_games']}"
    else:
        return "Account not created"


def info_game():
    output = "**Info**\n\n"

    output += "init: creates a new account\n"
    output += "start: start a game\n"
    output += "high/low: guess 'high' or 'low' for the next card \n"
    output += "status: see status\n"
    output += "info: shows this message\n"

    return output


class Card:
    hands = ["A", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    suites = ["♠️", "♣️", "♦️", "❤️"]

    def __init__(self, hand, suite):
        self.hand = hand
        self.suite = suite

    def to_dict(self):
        return {"hand": self.hand, "suite": self.suite}

    @classmethod
    def from_dict(cls, card_dict):
        return cls(card_dict["hand"], card_dict["suite"])

    def __repr__(self):
        return json.dumps(self.to_dict())

    def __str__(self):
        return f"{self.hand} {self.suite}"

    def compare(self, other):
        assert type(other) == Card, "The compared object is not of type Card"

        if Card.hands.index(self.hand) < Card.hands.index(other.hand):
            return -1
        elif Card.hands.index(self.hand) > Card.hands.index(other.hand):
            return 1
        else:
            if Card.suites.index(self.suite) < Card.suites.index(other.suite):
                return -1
            elif Card.suites.index(self.suite) > Card.suites.index(other.suite):
                return 1
            else:
                return 0

    @classmethod
    def create(cls):
        return cls(random.choice(Card.hands), random.choice(Card.suites))

