import discord
from discord.ext import commands
import requests
from datetime import datetime
import math
import calendar
from html2text import html2text
import urllib
from goodreads import client
from check import on_ready, is_bot_admin, confirm, wait_for_reply
ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(math.floor(n/10)%10!=1)*(n%10<4)*n%10::4])

class Utilities:
    def __init__(self, client):
        self.client = client

    async def get_book(self, *, query):
        response_ori = requests.get("https://www.googleapis.com/books/v1/volumes", params = {
        "q": query,
        "langRestrict": "en"
        })
        response = response_ori.json()
        if response["totalItems"] == 0:
            return None
        book = response["items"][0]
        authors = ""
        if len(book["volumeInfo"]["authors"]) == 1:
            authors = book["volumeInfo"]["authors"][0]
        else:
            if "authors" in book["volumeInfo"]:
                for timeslooped, author in enumerate(book["volumeInfo"]["authors"]):
                    if len(book["volumeInfo"]["authors"]) - 2 == timeslooped:
                        authors += f"{author} and "
                    elif len(book["volumeInfo"]["authors"])-1 == timeslooped:
                        authors += author
                    else:
                        authors += f"{author}, "
            else:
                authors = ""
        embed = discord.Embed(title = book["volumeInfo"]["title"],
        description = authors,
        colour = discord.Colour(0xe35ddd),
        timestamp = datetime.utcnow(),
        url = book["volumeInfo"]["infoLink"])
        if "imageLinks" in book["volumeInfo"]:
            embed.set_thumbnail(url=book["volumeInfo"]["imageLinks"]["thumbnail"])
        embed.set_author(name="Results on Google Books", url = "https://www.google.com/search?tbm=bks&"+urllib.parse.urlencode({"q":query}))
        embed.set_footer(text=f"Results on Google Books by {query} | {response['totalItems']} total results", icon_url="https://cohlab.com/wp-content/uploads/Google_-G-_Logo.svg-1.png")
        if "description" in book["volumeInfo"]:
            if len(book["volumeInfo"]["description"]) > 1000:
                embed.add_field(inline = False, name="Description", value=html2text(book["volumeInfo"]["description"])[:1000]+"...")
            else:
                embed.add_field(inline = False, name="Description", value=html2text(book["volumeInfo"]["description"]))
        elif "searchInfo" in book["volumeInfo"]:
            embed.add_field(inline = False, name="Description", value=html2text(book["searchInfo"]["textSnippet"]))
        else:
            embed.add_field(inline = False, name="Description", value="No description provided!")
        if "categories" in book["volumeInfo"]:
            if len(book["volumeInfo"]["categories"]) > 1:
                genres = ""
                for entry in book["volumeInfo"]["categories"]:
                    genres += ", " + entry
                embed.add_field(inline = False, name="Categories", value=genres)
            else:
                embed.add_field(inline = False, name="Categories", value=book["volumeInfo"]["categories"][0])
        else:
            embed.add_field(inline = False, name="Categories", value="This book is not categorized!")
        if book["volumeInfo"]["maturityRating"] == "NOT_MATURE":
            rating = "For all ages"
        else:
            rating = "Not suitable for -18"
        if "industryIdentifiers" in book["volumeInfo"]:
            id = f'Industry Identificator ({book["volumeInfo"]["industryIdentifiers"][len(book["volumeInfo"]["industryIdentifiers"])-1]["type"]}): {book["volumeInfo"]["industryIdentifiers"][len(book["volumeInfo"]["industryIdentifiers"])-1]["identifier"]}'
        else:
            id = f'Google Books identificator: {book["id"]}'
        if "pageCount" in book["volumeInfo"]:
            embed.add_field(inline = False, name="Book information", value=f"{book['volumeInfo']['pageCount']} pages\nFor all ages\n{id}")
        else:
            embed.add_field(inline = False, name="Book information", value=f"Page count is not listed\nFor all ages\nISBN: {book['volumeInfo']['industryIdentifiers'][1]['identifier']}")
        if "publisher" in book["volumeInfo"]:
            publisher = book['volumeInfo']['publisher']
        else:
            publisher = "No publisher"
        if "publishedDate" in book["volumeInfo"]:
            date = book["volumeInfo"]["publishedDate"].split("-")
            if len(date) == 3:
                date_text = f"{ordinal(int(date[2]))} {calendar.month_name[int(date[1])]}, {date[0]}"
                date_num = f" ({date[0]}/{date[1]}/{date[2]})"
            elif len(date) == 2:
                date_text = f"{calendar.month_name[int(date[1])]}, {date[0]}"
                date_num = f" ({date[1]}/{date[2]})"
            else:
                date_text = f"{date[0]}"
                date_num = ""
            embed.add_field(inline = False, name="Publish information", value=f"Published by {publisher}\n{date_text}{date_num}")
        else:
            embed.add_field(inline = False, name="Publish information", value=f"Published by {publisher}\nPublish date is not listed")
        string = ""
        if book["saleInfo"]["saleability"] == "FOR_SALE":
            embed.add_field(inline = False, name="Sales information", value=f"Ebook on sale on Google Books\n{book['saleInfo']['listPrice']['amount']}{book['saleInfo']['listPrice']['currencyCode']}\n[Get it now!]({book['saleInfo']['buyLink']})")
        else:
            embed.add_field(inline = False, name="Sales information", value=f"Not available on Google Books.\nWhat about [seaching it on Amazon](https://www.amazon.com/s/url=search-alias%3Dstripbooks-intl-ship&field-keywords={book['volumeInfo']['industryIdentifiers'][len(book['volumeInfo']['industryIdentifiers'])-1]['identifier']})?")
        return embed

    @commands.command()
    async def book (self, ctx, *, query):
        """Shows info on a book thanks to Google Books."""
        await ctx.trigger_typing()
        result = await self.get_book(query = query)
        if result == None:
            await ctx.send("Ooops! I found no results on that book. Is it not popular enough or did you just smash the keyboard?")
        else:
            await ctx.send(embed=result)

    @commands.guild_only()
    @is_bot_admin()
    @commands.command()
    async def suggest_everyone(self, ctx, *, book):
        """Suggests a book to everyone in the server. Remember: It must be a cool book!"""
        embed = await self.get_book(query = book)
        async def doDM(review = None):
            total = 0
            for member in ctx.guild.members:
                try:
                    if review:
                        await member.send(f'{ctx.author.mention} suggests you to read "{embed.title}"!\n\n"{review}" - {ctx.author.mention}', embed = embed)
                    else:
                        await member.send(f'{ctx.author.mention} suggests you to read "{embed.title}"!', embed = embed)
                except discord.Forbidden:
                    pass
                except discord.HTTPException as e:
                    if e.status != 400:
                        raise e
                else:
                    total += 1
            return total

        if book == None:
            await ctx.send("Ooops! I found no results on that book. Is it not popular enough or did you just smash the keyboard?")
        else:
            async def on_yes():

                async def final_yes():
                    async with ctx.typing():
                        await ctx.send("Okay, hold on... I'm DMing everyone I can...")
                        if answer:
                            total = await doDM(answer.content)
                        else:
                            total = await doDM()
                        await ctx.send(f"Done! I suggested your book to {total} people. I hope they like it!")

                async def final_no():
                    await ctx.send("Okay, nevermind then. Was the book not good enough? *sigh*")

                async def on_reply(reply):
                    global answer
                    answer = reply
                    await confirm(ctx, "That's a cool review!\n\nFinal step and confirmation, are you sure?", on_yes=final_yes, on_no=final_no)

                async def on_cancel():
                    await confirm(ctx, "Okay, no review.\n\nFinal step and confirmation, are you sure?", on_yes=final_yes, on_no=final_no)

                await wait_for_reply(ctx, 'Okay, do you want to give me a review about the book? Else, just say "no".', timeout=180, on_reply = on_reply, on_cancel = on_cancel, cancel = "no")

            async def on_no():
                await ctx.send("Okay, nevermind. For a more precise search, what about giving me the book's ISBN next time?")

            await confirm(ctx, "Is this the book you wanted? React to the message to say yes or no!", on_yes=on_yes, on_no=on_no, embed=embed)



def setup(client):
    client.add_cog(Utilities(client))
    on_ready(client)
