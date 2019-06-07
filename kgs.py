import json
import asyncio
import discord
import os
import config
import requests
import aiohttp

# kgs room id
ROOM=788560

# kgs bot account name
kgs_bot = "LooselyBot"

# kgs json api to read data
kgs_url = "http://www.gokgs.com/json/access"

# bold wrapper
def bold(fn):
    def wrapper(user):
        # insert some bold before and after text
        return "**" + fn(user) + "**"
    return wrapper

async def login(session, status):
        if status == 200:
            return

        # need to put your account name/password
        message = {
            "type": "LOGIN",
            "name": kgs_bot,
            "password": "",
            "locale": "en_US",
        }

        formatted_message = json.dumps(message)
        await session.post(kgs_url, data=formatted_message)

async def logout(session):
    session.post(kgs_url, json.dumps({"type": "LOGOUT"}))

@bold
def formatted_username(user):
    """
    user: KGS player dict
    yes_status: boolean to dicate whether to contain status of user

    Given a KGS player dict user, return a string containing user information
    """
    rank = ""
    if "g" in user["flags"]:
        rank = "Guest"
    elif "rank" in user:
        rank = user["rank"]
    else:
        rank = "-"
    return   user['name'] + " [" +  rank + "]"

def formatted_user_status(user):
    if "flags" not in user:
        return ""
    for k, v in config.kgs_user_flags_status.items():
        if k in user["flags"]:
            return v

def formatted_name(player):
    """
    Given a KGS player dict, return a str: username(rank)
    https://www.gokgs.com/json/dataTypes.html#user
    """
    text = "**" + player['name'] + "**"
    if 'rank' in player:
        text += " (" + player['rank'] + ")"
    return

def result(score):
    """
    Returns a string indicating the result of a game
    https://www.gokgs.com/json/dataTypes.html#score
    """
    if type(score) == float:
        if score > 0:
            out = "Black + " + str(score)
        else:
            out = "White + " + str(-score)
    else:
        out = score
    return out

async def get_kgs_players(m, session, bot, channel):
    if m["type"] == "ROOM_JOIN" and m["channelId"] == ROOM and "users" in m:
        text = ""
        for u in  m["users"]:
            text += "\n" + formatted_username(u)+ ": "
            text += formatted_user_status(u)
        await send_discord_message(bot, channel, text)
        await send_kgs_messages(session, text)

async def handle_message(session, bot, channel, data, op):
    if data is None or not "messages" in data:
        #print("not in message")
        return
    if "messages" in data:
        for m in data["messages"]:
            if "channelId" in m and "type" in m:
                if op == 1:
                    await get_kgs_players(m, session, bot, channel)
                    #text = ""
                    #for u in  m["users"]:
                    #    text += "\n" + formatted_username(u)+ ": "
                    #    text += formatted_user_status(u)
                    #await send_discord_message(bot, channel, text)
                   # await send_kgs_messages(session, text)
                if op == 0 and m['type'] == 'CHAT' and m['channelId'] == ROOM:
                    if m['user']['name'] != kgs_bot:

                        text = formatted_username(m["user"]) + ": "
                        #if (m["text"].startswith("/") and m["text"] in config.clyde_command)
                        if m["text"] in config.clyde_command:
                            text += config.clyde_command[m["text"]]
                            await send_kgs_messages(session,
                                              [config.clyde_command[m["text"]]])

                        elif m["text"] in config.addon_command:
                            text += config.addon_command[m["text"]]
                            await send_kgs_messages(session,
                                              [config.addon_command[m["text"]]])
                        else:
                            text += m["text"]

                        #    await send_discord_message(bot, channel, m["text"])
                        #text = formatted_username(m["user"]) + ": " + m["text"]
                        #print("text is " , text)
                        await send_discord_message(bot, channel, text)
            if m['type'] == 'LOGOUT':
                await login(session, 0)

async def get_messages(session, bot, channel, op):
   async with session.get(kgs_url) as r:
       data = await r.json()
       await handle_message(session, bot, channel, await r.json(), op)

       #print(data)
       #print(json.dumps(data))
#       if "messages" in data:
#           for m in data["messages"]:
#               if m["type"] == "CHAT" and m["channelId"] == ROOM:
#                   text = m["user"]["name"] + " [" +  m["user"]["rank"] + "]: " + m["text"]
#                   print(text)
#                   await send_discord_message(text, bot)

async def send_discord_message(bot, channel, message):
    await bot.send_message(channel, message)

async def send_kgs_messages(session, messages):
    for text in messages:
        message = {
            "type": "CHAT",
            "text": text,
            "channelId": ROOM
        }
        formatted_message = json.dumps(message)
        await session.post(kgs_url, data=formatted_message)
