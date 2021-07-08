import random
from firebase_admin import firestore


async def handle(db, message):
    if message.content == "$roll":
        await message.channel.send(f"{message.author.name} got {roll(db, message)}")

    if message.content == "$roll-rank":
        top = roll_rank()

        for i in range(3):
            nm, vl = top[i]["name"], top[i]["value"]
            await message.channel.send(f"{i + 1}. {nm} {vl}")


def roll(db, message):
    val = random.randint(1, 100)

    roll_ref = db.collection("rolls").document()
    roll_ref.set(
        {
            "channel_id": message.channel.id,
            "author": {"id": message.author.id, "name": message.author.name,},
            "value": val,
        }
    )
    return val


def roll_rank(db):
    stream = (
        db.collection("rolls")
        .order_by("value", direction=firestore.Query.DESCENDING)
        .limit(3)
        .stream()
    )

    top = {}
    for i, s in enumerate(stream):
        d = s.to_dict()
        name = d["author"]["name"]
        val = d["value"]

        top[i] = {"name": name, "value": val}

    return top
