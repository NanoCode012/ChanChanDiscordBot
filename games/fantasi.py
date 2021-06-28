import json, random


async def handle(db, message):
    opt = message.content.split(" ")[1:]

    has_acc = has_account(db=db, id=message.author.id)
    out = f"{message.author.name} | "
    if opt[0] == "create":
        if not has_acc:
            db_ref = db.document("fantasi/data").collection("characters").document()
            db_ref.set(Character(message).to_dict())
            out += "Character created"
        else:
            out += "You already have an account!"
    elif opt[0] == "info":
        out += "**Info**\n\n"
        out += "create: creates a new account\n"
        out += "status: see status info\n"
        out += (
            "roll <amount>: roll amount. If win, get at least that amount in return.\n"
        )
    elif opt[0] in ["status", "roll"]:  # commands which require account permissions
        try:
            assert has_acc, "You do not have an account yet!"

            db_ref = next(
                db.document("fantasi/data")
                .collection("characters")
                .where("author.id", "==", message.author.id)
                .limit(1)
                .stream()
            )
            character = Character.from_dict(db_ref.to_dict())
            if opt[0] == "status":
                out += str(character)
            elif opt[0] == "roll":
                assert len(opt) > 1, "Missing roll value"

                val = int(opt[1])
                cutoff = 60
                roll_val, diff = character.roll(val, cutoff=cutoff)
                out += f"You rolled {roll_val}. "

                status = "won" if diff > 0 else "lost"
                out += f"You {status} {abs(diff)}."

                batch = db.batch()
                roll_ref = db.document("fantasi/data").collection("rolls").document()
                batch.set(
                    roll_ref,
                    {
                        "character_id": db_ref.id,
                        "author": {
                            "id": message.author.id,
                            "name": message.author.name,
                        },
                        "roll": roll_val,
                        "cutoff": cutoff,
                        "diff": diff,
                    },
                )

                gold_ref = db.document(f"fantasi/data/characters/{db_ref.id}")
                batch.update(gold_ref, {"gold": character.gold})

                batch.commit()

        except ValueError:
            out += "Incorrect input. Should be a value!"
        except Exception as e:
            out += str(e)

    else:
        out += "That command cannot be found"

    if out:
        await message.channel.send(out)


def has_account(db, id):
    try:
        db_ref = next(
            db.document("fantasi/data")
            .collection("characters")
            .where("author.id", "==", id)
            .limit(1)
            .stream()
        )
        return True
    except StopIteration:
        return False


class Character:
    def __init__(
        self,
        message=None,
        author=None,
        channel=None,
        content=None,
        gold=None,
        level=None,
    ):
        if message:
            author = User(user=message.author)
            channel = Channel(channel=message.channel)
            content = message.content

        assert author and channel and content, "Author, Channel, or content not set"

        self.author = author
        self.channel = channel
        self.content = content

        self.gold = gold if gold is not None else 10
        self.level = level if level is not None else 1

    def __repr__(self):
        return json.dumps(self.to_dict())

    def __str__(self):
        return f"{self.author.name}#{self.author.discriminator} | Level: {self.level} | Gold: {self.gold}"

    def to_dict(self):
        return {
            "author": self.author.to_dict(),
            "channel": self.channel.to_dict(),
            "content": self.content,
            "gold": self.gold,
            "level": self.level,
        }

    @staticmethod
    def from_dict(source):
        author = User.from_dict(source["author"])
        channel = Channel.from_dict(source["channel"])

        content = source["content"]
        gold = source["gold"]
        level = source["level"]
        return Character(
            author=author, channel=channel, content=content, gold=gold, level=level
        )

    def roll(self, amount, minimum=1, maximum=100, cutoff=70, winnings=20, cap=100):
        assert amount >= minimum, f"You need to bet at least {minimum} gold!"
        assert amount <= self.gold, "You do not have enough gold!"

        val = random.randint(minimum, maximum)

        if val >= cutoff:
            diff = (
                min(int(amount * (1 + (winnings / 100))), cap)
                if amount < cap
                else amount
            )
        else:
            diff = -amount

        self.gold += diff
        return val, diff


class User:
    def __init__(self, user=None, id=None, name=None, discriminator=None):
        if user:
            id = user.id
            name = user.name
            discriminator = user.discriminator

        assert id and name and discriminator, "Id, name, or discriminator not set"

        self.id = id
        self.name = name
        self.discriminator = discriminator

    def __repr__(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "discriminator": self.discriminator,
        }

    @staticmethod
    def from_dict(source):
        return User(
            id=source["id"], name=source["name"], discriminator=source["discriminator"]
        )


class Channel:
    def __init__(self, channel=None, id=None, name=None):
        if channel:
            id = channel.id
            name = channel.name

        assert id and name, "Id or name not set"

        self.id = id
        self.name = name

    def __repr__(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
        }

    @staticmethod
    def from_dict(source):
        return Channel(id=source["id"], name=source["name"])

