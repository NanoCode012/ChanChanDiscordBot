import discord
import os
import random

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from fantasi import *

# Use a service account
cred = credentials.Certificate('siit-293014-firebase-adminsdk-427ti-ca473c1b7a.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await client.get_channel(803946625705443358).send("I am backkkk!")

def roll(message):
    val = random.randint(1, 100)
    
    roll_ref = db.collection(u'rolls').document()
    roll_ref.set({
        'channel_id': message.channel.id,
        'author': { 
            'id': message.author.id,
            'name': message.author.name,
        },
        'value': val,
    })
    return val

def roll_rank():
    stream = db.collection(u'rolls').order_by(u'value', direction=firestore.Query.DESCENDING).limit(3).stream()

    top = {}
    for i, s in enumerate(stream):
        d = s.to_dict()
        name = d['author']['name']
        val = d['value']
        
        top[i] = {'name': name, 'value': val}

    return top

def rps():
    return random.choice(['rock', 'paper', 'scissor'])

def calc_rps(user_choice):
    bot_choice = rps()
    user_choice = user_choice.lower()

    if (user_choice == bot_choice): # same
        return 0
    if (user_choice == 'rock' and bot_choice == 'paper'):
        return -1
    elif (user_choice == 'paper' and bot_choice == 'rock'):
        return 1
    elif (user_choice == 'scissor' and bot_choice == 'rock'):
        return -1
    elif (user_choice == 'rock' and bot_choice == 'scissor'):
        return 1
    elif (user_choice == 'paper' and bot_choice == 'scissor'):
        return -1
    elif (user_choice == 'scissor' and bot_choice == 'paper'):
        return 1
    else:
        raise Exception('Invalid choice')

def rps_res(message):
    rps_games = db.collection('rps')
    query = rps_games.where('author.id', '==', message.author.id).stream()

    li = []
    for s in query:
        li.append(s.to_dict()['value'])

    return 'Stats (Win: {} | Draw: {} | Lose: {})'.format(li.count(1), li.count(0), li.count(-1))

def f_checkacc(id):
    try:
        db_ref = next(db.document('fantasi/data').collection('characters').where('author.id', '==', id).limit(1).stream())
        return True
    except StopIteration:
        return False

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    messages = {
        '$hello': f'Hello {message.author.name}!',
        '$fuckoff': f'No no no. How would I dare?!',
        '$roll': f'{message.author.name} got {roll(message)}',
        '$rps-res': f'{message.author.name} | {rps_res(message)}',
    }

    if message.content in messages:
        await message.channel.send(messages[message.content])

    if message.content == '$roll-rank': 
        top = roll_rank()

        for i in range(3):
            nm, vl = top[i]['name'], top[i]['value']
            await message.channel.send(f'{i + 1}. {nm} {vl}')

    if message.content.startswith('$rps '):
        choice = message.content.split(' ')[-1]

        try:
            v = calc_rps(choice)
            if (v == 1):
                await message.channel.send(f'How could you win, {message.author.name}?? ')
            elif (v == 0):
                await message.channel.send(f'We are a draw, so I take it as my win, {message.author.name}')
            elif (v == -1):
                await message.channel.send(f'I won against you, {message.author.name}! Pathetic!')

            db_ref = db.collection(u'rps').document()
            db_ref.set({
                'channel_id': message.channel.id,
                'author': { 
                    'id': message.author.id,
                    'name': message.author.name,
                },
                'value': v,
            })
        except Exception as e:
            await message.channel.send(str(e))
        
    if message.content.startswith('$f '):
        opt = message.content.split(' ')[1:]

        has_acc = f_checkacc(id=message.author.id)
        out = f'{message.author.name} | '
        if opt[0] == 'create':
            if not has_acc:
                db_ref = db.document('fantasi/data').collection('characters').document()
                db_ref.set(Character(message).to_dict())
                out += 'Character created'
            else:
                out += 'You already have an account!'
        elif opt[0] in ['status', 'roll']: # commands which require account permissions
            try:
                assert has_acc, 'You do not have an account yet!'

                db_ref = next(db.document('fantasi/data').collection('characters').where('author.id', '==', message.author.id).limit(1).stream())
                character = Character.from_dict(db_ref.to_dict())
                if opt[0] == 'status':
                    out += str(character)
                elif opt[0] == 'roll':
                    assert len(opt) > 1, 'Missing roll value'
    
                    val = int(opt[1])
                    cutoff = 70
                    roll_val, diff = character.roll(val, cutoff=cutoff)

                    db.document('fantasi/data').collection('rolls').document().set({
                        'character_id': db_ref.id,
                        'roll': roll_val,
                        'cutoff': cutoff,
                        'diff': diff,
                    })

                    out += f'You rolled {roll_val}. '

                    status = 'won' if roll_val >= cutoff else 'lost'
                    out += f'You {status} {diff}.'

                    db.document(f'fantasi/data/characters/{db_ref.id}').update({
                        'gold': character.gold
                    })

            except ValueError:
                out += 'Incorrect input. Should be a value!'
            except Exception as e:
                out += str(e)
            
        else:
            out += 'That command cannot be found'

        if out:
           await message.channel.send(out) 
            
                
    if message.content == '$stop': 
        await message.channel.send('I am leaving.. for now!')
        await client.logout()

    print(message)

client.run(os.getenv("DISCORD_BOT_TOKEN"))