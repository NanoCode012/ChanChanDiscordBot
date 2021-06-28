import random


async def handle(db, message):
    choice = message.content.split(" ")[-1]

    if choice == "res":
        await message.channel.send(f"{message.author.name} | {rps_res(db, message)}")
        return

    try:
        v = calc_rps(choice)
        if v == 1:
            await message.channel.send(f"How could you win, {message.author.name}?? ")
        elif v == 0:
            await message.channel.send(
                f"We are a draw, so I take it as my win, {message.author.name}"
            )
        elif v == -1:
            await message.channel.send(
                f"I won against you, {message.author.name}! Pathetic!"
            )

        db_ref = db.collection("rps").document()
        db_ref.set(
            {
                "channel_id": message.channel.id,
                "author": {"id": message.author.id, "name": message.author.name,},
                "value": v,
            }
        )
    except Exception as e:
        await message.channel.send(str(e))


def rps():
    return random.choice(["rock", "paper", "scissor"])


def calc_rps(user_choice):
    bot_choice = rps()
    user_choice = user_choice.lower()

    if user_choice == bot_choice:  # same
        return 0
    if user_choice == "rock" and bot_choice == "paper":
        return -1
    elif user_choice == "paper" and bot_choice == "rock":
        return 1
    elif user_choice == "scissor" and bot_choice == "rock":
        return -1
    elif user_choice == "rock" and bot_choice == "scissor":
        return 1
    elif user_choice == "paper" and bot_choice == "scissor":
        return -1
    elif user_choice == "scissor" and bot_choice == "paper":
        return 1
    else:
        raise Exception("Invalid choice")


def rps_res(db, message):
    rps_games = db.collection("rps")
    query = rps_games.where("author.id", "==", message.author.id).stream()

    li = []
    for s in query:
        li.append(s.to_dict()["value"])

    return "Stats (Win: {} | Draw: {} | Lose: {})".format(
        li.count(1), li.count(0), li.count(-1)
    )
