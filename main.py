import discord
from discord.ext import commands
import asyncio
import json
import traceback

botconfig = json.loads(open("./botconfig.json", "r").read())
commands_info = json.loads(open("./commands.json", "r").read())

extensions = ["Core", "Utilities", "Bot management"]

client = commands.Bot(command_prefix = "book!", case_insensitive = True)

log_channel = None

@client.event
async def on_ready():
    print("The Book Bot is botting up!")
    if not hasattr(client, 'appinfo'):
        client.appinfo = await client.application_info()
    global log_channel
    log_channel = client.get_channel(512325364174028811)
    setattr(client, "log_channel", log_channel)
    await log_channel.send("The Book Bot is booting up...")
    await client.change_presence(activity=discord.Activity(type=0, name="booting up..."), status=discord.Status.idle)
    await log_channel.send("Loading cogs...")
    for extension in extensions:
        try:
            client.load_extension(f"Cogs.{extension}")
        except Exception as error:
            print(f"[{error}] , error while loading cog {extension}")
            await log_channel.send(f"[{error}] , error while loading cog {extension}")
    await log_channel.send(":white_check_mark: The Book Bot is online!")
    await client.change_presence(activity=discord.Activity(type=0, name="with books"),status="online")
    print("The Book Bot is online!")

@client.event
async def on_message(ctx):
    if ctx:
        if ctx.author.bot:
            return
        else:
            if ctx.content == client.user.mention:
                await ctx.channel.send("Hi! I'm a Book Bot and I love books.\n\nIf you want to use any of my commands, just use the prefix `book!`. To see a list of commands, then say `book!help`")
            else:
                context = await client.get_context(ctx)
                if context.valid:
                    if isinstance(ctx.channel, discord.TextChannel):
                        if not ctx.channel.permissions_for(ctx.channel.guild.me).send_messages:
                            return
                        else:
                            await client.process_commands(ctx)
                    else:
                        return
                else:
                    if isinstance(ctx.channel, discord.DMChannel):
                        await log_channel.send(f"`{ctx.author.mention} ({ctx.author.id})` said through DMs with invalid context:```{ctx.content}```")

@client.event
async def on_command_error(ctx: commands.Context, error):
    if isinstance(error, commands.NoPrivateMessage):
        await ctx.send("I'm sorry, but this command can not be used through DMs!")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send(f"Oops! I do not have enough permissions to run {ctx.command}!```error```")
    elif isinstance(error, commands.DisabledCommand):
        await ctx.send("Sorry! This command is disabled and can not be used.")
    elif isinstance(error, commands.CheckFailure):
        await ctx.send(":lock: Sweetie, you don't have enough permissions to run this command!")
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"Really sorry, but you need to calm down! You're on a cooldown.```{error}```")
    elif isinstance(error, commands.MissingRequiredArgument):
        if f'{ctx.command}_args' in commands_info:
            args = commands_info[f'{ctx.command}_args']
        else:
            args = ""
        await ctx.send(f"You are missing required arguments!\nCommand usage: `book!{ctx.command}{args}`")
    elif isinstance(error, commands.BadArgument):
        if f'{ctx.command}_args' in commands_info:
            args = commands_info[f'{ctx.command}_args']
        else:
            args = ""
        await ctx.send(f"One of your arguments is incorrect!\nCommand usage: `book!{ctx.command}{args}`")
    elif isinstance(error, commands.CommandNotFound):
        return

    else:
        await ctx.send(":rotating_light: Oh noes! Something went ***TERRIBLY***  wrong! No, It's not grammar, It's an internal error! :rotating_light:")
        await log_channel.send(f"<@407093314316140554>\n\n{error}\n¨{traceback.format_exc()}")
        raise error

client.run(botconfig["token"])
print("The Book Bot is shutting down...")
