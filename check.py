import discord
from discord.ext import commands
import json
import asyncio

def on_ready(client):
    global yes
    global no
    yes = discord.utils.get(client.emojis, id=513106537909321728)
    no = discord.utils.get(client.emojis, id=513337827644276788)

botconfig = json.loads(open("./botconfig.json", "r").read())

def is_bot_admin():
    async def predicate(ctx):
        return ctx.author.id in botconfig["bot_admins"]
    return commands.check(predicate)

async def confirm(ctx:commands.Context, text, timeout=30, on_yes = None, on_no = None, delete=False, embed:discord.Embed = None):
    message:discord.Message = await ctx.send(text, embed = embed)
    await message.add_reaction(yes)
    await message.add_reaction(no)

    def check(reaction:discord.Reaction, user):
        return user == ctx.message.author and reaction.emoji in (yes, no) and reaction.message.id == message.id

    try:
        reaction, user = await ctx.bot.wait_for('reaction_add', timeout=timeout, check=check)
    except asyncio.TimeoutError:
        if delete:
            await message.delete()
        await ctx.send(f"No reaction has been given in {timeout} seconds! Aborting...")
    else:
        if reaction.emoji is yes and on_yes is not None:
            if delete:
                try:
                    await message.delete()
                except discord.Forbidden:
                    pass
            if on_yes is not None:
                await on_yes()
        elif reaction.emoji is no:
            if delete:
                try:
                    await message.delete()
                except discord.Forbidden:
                    pass
            if on_no is not None:
                await on_no()

async def wait_for_reply(ctx:commands.Context, text, timeout=120, on_reply = None, on_cancel= None, cancel:str = "cancel", embed:discord.Embed = None):
    message:discord.Message = await ctx.send(text, embed = embed)

    def check(msg:discord.Message):
        return msg.author == ctx.message.author and msg.channel.id == message.channel.id

    try:
        reply = await ctx.bot.wait_for('message', timeout=timeout, check=check)
    except asyncio.TimeoutError:
        await ctx.send(f"No reply has been given in {timeout} seconds! Aborting...")
    else:
        if reply.content.lower() == cancel.lower():
            if on_cancel is not None:
                await on_cancel()
        else:
            if on_reply is not None:
                await on_reply(reply)
