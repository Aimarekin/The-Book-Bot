import discord
from discord.ext import commands
import json

commands_info = json.loads(open("./commands.json", "r").read())

class Core:
    def __init__(self, client):
        self.client = client

    async def gen_cog_cmds(self, ctx, cog, showall = False):
        cmds = self.client.get_cog_commands(cog)
        if len(cmds) > 0:
            list = ""
            for command in cmds:
                runnable = False
                if not command.hidden:
                    try:
                        runnable = await command.can_run(ctx=ctx)
                    except:
                        runnable = False
                if f'{command}_args' in commands_info:
                    args = commands_info[f'{command}_args']
                else:
                    args = ""
                if showall:
                    if runnable:
                        list += f"`book!{command}{args}` :slight_smile:\n{command.help}\n\n"
                    else:
                        list += f"`book!{command}{args}` :slight_frown:\n{command.help}\n\n"
                else:
                    if runnable:
                        list += f"`book!{command}{args}`\n{command.help}\n\n"
            if list != "":
                return list
            else:
                return None
        else:
            return None

    @commands.command()
    async def help (self, ctx, *, command:str =None):
        """Returns a list of commands."""
        await ctx.trigger_typing()
        if not command:
            helpembed = discord.Embed(title="Check out my commands!", colour=discord.Colour(0x2ecc71), description="Here is a list of the commands you can use with me. Hope you like them!")
            for cog in self.client.cogs:
                list = await self.gen_cog_cmds(ctx, cog)
                if list:
                    helpembed.add_field(name = cog, value = list, inline = False)
            await ctx.send(embed= helpembed)
        else:
            found = self.client.get_command(command.lower())
            if found:
                try:
                    runnable = await found.can_run(ctx=ctx)
                    if runnable:
                        runnable = not found.hidden
                except:
                    runnable = False
                if runnable:
                    can_run = "You can run this command."
                else:
                    can_run = "You can not run this command! Sad face."
                helpembed = discord.Embed(title=found.name, colour=discord.Colour(0x2ecc71), description=f"`book!{found}{commands_info[f'{found}_args']}`\n\n{found.help}\n\nPart of: {found.cog_name}\n\n{can_run}")
                await ctx.send(embed = helpembed)
            else:
                found = self.client.get_cog(command.capitalize())
                if found:
                    helpembed = discord.Embed(title=command.capitalize(), colour=discord.Colour(0x2ecc71), description= await self.gen_cog_cmds(ctx, command.capitalize(), showall = True))
                    await ctx.send(embed = helpembed)
                else:
                    helpembed = discord.Embed(title="Error", colour=discord.Colour.dark_red(), description=f"There is no command/cog called {command.capitalize()}.\nSorry about that!")
                    await ctx.send(embed = helpembed)

    @commands.command()
    async def ping (self, ctx):
        """Checks if I am online and returns the amount of time I take to receive your messages through Discord."""
        await ctx.send("Pong!  🏓\n\n`PING: {} ms`".format(round(self.client.latency * 1000, 2)))


def setup(client):
    client.remove_command("help")
    client.add_cog(Core(client))
