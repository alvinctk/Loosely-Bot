import discord
from discord.ext import commands
import random
import os
import asyncio
import aiohttp
import kgs
import config
import requests

TOKEN="" # Replace the string the token given by discord api
kgs_to_send =[]
client = discord.Client()
bot = commands.Bot(command_prefix="!")
text_channel = "kgs"
@bot.event
async def on_ready():
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print("----------")
    print(discord.__version__)

@bot.command(pass_context=True)
async def hello(ctx):
    await bot.say("hello " + ctx.message.author.mention)

@bot.command(pass_context=True)
async def kgs_players(ctx):
    await bot.wait_until_ready()
    async with aiohttp.ClientSession() as kgs_session:
        await kgs.login(kgs_session, 0)
        channel = bot.get_channel(config.channels[text_channel])
        await kgs.get_messages(kgs_session, bot, channel, 1)
        await asyncio.sleep(1)

@bot.command(pass_context=True)
async def discord_invite(ctx):
    await bot.wait_until_ready()
    text = "hello " + ctx.message.author.name + ", the invitation to discord is https://discord.gg/DDrjdrC"
    await bot.say(text)
    kgs_to_send.append(text)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    #ctx = await bot.get_message(message)
    #if ctx.command is None:
        # Not a valid command (Normal message or invalid command)
        #If it's in kgs channel we add it in the kgs_to_send queue
    if message.channel == bot.get_channel(config.channels[text_channel]):
        text = str(message.author.display_name) + ": "
        if message.content in config.addon_command.keys():
            text += config.addon_command[message.content]
            await kgs.send_discord_message(bot, message.channel, text)
        else:
            text += message.content
        kgs_to_send.append(text)
    await bot.process_commands(message)

async def check_KGS():
    print("check_KGS")
    await bot.wait_until_ready()
    global kgs_to_send

    #Display a message for which time was bot last updated.
    channel = discord.Object(config.channels[text_channel])
    #channel = discord.utils.get(server.channels, name='kgs-test-bot', type=ChannelType.text)
    msg = "{} was just deployed.".format(bot.user.mention)
    await bot.send_message(channel, msg)

    async with aiohttp.ClientSession() as kgs_session:
        await kgs.login(kgs_session, 0)
        while not bot.is_closed == True:
            await kgs.send_kgs_messages(kgs_session, kgs_to_send)
            kgs_to_send = []
            await kgs.get_messages(kgs_session, bot, channel, 0)
            await asyncio.sleep(1)

bot.loop.create_task(check_KGS())
bot.run(TOKEN)
