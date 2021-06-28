import discord
import os
import random

import firebase_admin
from firebase_admin import credentials, firestore

from games import fantasi, rps

# Use a service account
cred = credentials.Certificate("firebase-adminsdk.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

client = discord.Client()


@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))
    await client.get_channel(int(os.getenv("DISCORD_CHANNEL_ID"))).send("I am backkkk!")


def roll(message):
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


def roll_rank():
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


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    messages = {
        "$hello": f"Hello {message.author.name}!",
        "$fuckoff": f"No no no. How would I dare?!",
    }

    if message.content in messages:
        await message.channel.send(messages[message.content])

    if message.content == "$roll":
        await message.channel.send(f"{message.author.name} got {roll(message)}")

    if message.content == "$roll-rank":
        top = roll_rank()

        for i in range(3):
            nm, vl = top[i]["name"], top[i]["value"]
            await message.channel.send(f"{i + 1}. {nm} {vl}")

    if message.content.startswith("$rps "):
        await rps.handle(db=db, message=message)

    if message.content.startswith("$f "):
        await fantasi.handle(db=db, message=message)

    if message.content == "$stop":
        await message.channel.send("I am leaving.. for now!")
        await client.close()

    print(message)


client.run(os.getenv("DISCORD_BOT_TOKEN"))
