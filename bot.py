import discord
import os
import random

import firebase_admin
from firebase_admin import credentials, firestore

from games import fantasi, rps, rolls, hi_lo

# Use a service account
cred = credentials.Certificate("firebase-adminsdk.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

client = discord.Client()


@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))
    await client.get_channel(int(os.getenv("DISCORD_CHANNEL_ID"))).send("I am backkkk!")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    messages = {
        "$hello": f"Hello {message.author.name}!",
        "$fuckoff": f"No no no. How would I dare?!",
    }

    # default messages
    if message.content in messages:
        await message.channel.send(messages[message.content])

    if message.content.startswith == "$roll":
        await rolls.handle(db=db, message=message)

    if message.content.startswith("$rps "):
        await rps.handle(db=db, message=message)

    if message.content.startswith("$f "):
        await fantasi.handle(db=db, message=message)

    if message.content.startswith("$hl "):
        await hi_lo.handle(db=db, message=message)

    if message.content == "$stop":
        await message.channel.send("I am leaving.. for now!")
        await client.close()

    print(message)


client.run(os.getenv("DISCORD_BOT_TOKEN"))
