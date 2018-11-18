import discord
from discord.ext import commands
import time

class Management:
    def __init__(self, client):
        self.client = client

    @commands.is_owner()
    @commands.command()
    async def shutdown (self, ctx):
        """Shuts the bot down."""
        await ctx.send("Bot is shutting down...")
        await self.client.logout()
        await self.client.close()
        self.client.aiosession.close()

    @commands.is_owner()
    @commands.command()
    async def chat (self, ctx, channel : discord.TextChannel, *, tosay):
        """Chats a message in a channel"""
        await channel.send(tosay)

    @commands.is_owner()
    @commands.command()
    async def reloadcog(self, ctx, cog):
        """Reloads a cog (Unload & load)."""
        await ctx.send(f"Reloading {cog}...")
        self.client.unload_extension(f"Cogs.{cog}")
        self.client.load_extension(f"Cogs.{cog}")
        await ctx.send(f"{cog} reload complete :white_check_mark:")

    @commands.is_owner()
    @commands.command()
    async def loadcog(self, ctx, cog):
        """Only loads a cog."""
        await ctx.send(f"Reloading {cog}...")
        self.client.load_extension(f"Cogs.{cog}")
        await ctx.send(f"{cog} load complete :white_check_mark:")

    @commands.is_owner()
    @commands.command()
    async def unloadcog(self, ctx, cog):
        """Only unloads a cog."""
        await ctx.send(f"Reloading {cog}...")
        self.client.unload_extension(f"Cogs.{cog}")
        await ctx.send(f"{cog} unload complete :white_check_mark:")

    @commands.is_owner()
    @commands.command()
    async def reload(self, ctx):
        """Reloads all of the bot's cogs and other components."""
        if await self.client.is_owner(ctx.author):
            async with ctx.typing():
                done = 0
                msg = await ctx.send(f"Bot is reloading...```Command run start```({done} done)")
                await msg.edit(content = f"Bot is reloading...```Utilities reloaded```({done} done)")
                temp = []
                for cog in self.client.cogs:
                    temp.append(cog)
                    done = done + 1
                    await msg.edit(content = "Bot is reloading...```Appended to temp {}{}```({} done)".format(cog, str(temp), done))
                for cog in temp:
                    self.client.unload_extension(f"Cogs.{cog}")
                    done = done + 1
                    await msg.edit(content = f"Bot is reloading...```Unloaded {cog}```({done} done)")
                    self.client.load_extension(f"Cogs.{cog}")
                    done = done + 1
                    await msg.edit(content = f"Bot is reloading...```Loaded {cog}```({done} done)")
            await msg.edit(content = f"Bot is reloading...```Reload complete {time.time()}```({done} done)")
            await ctx.send( "Reload complete ✅")

def setup(client):
    cog_to_add = Management(client)
    Management.__name__ = "Bot management"
    client.add_cog(cog_to_add)
