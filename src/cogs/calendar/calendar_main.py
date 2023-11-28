import asyncio
from globals import *
from time import sleep
from datetime import date, datetime

import discord
from discord.ext import commands
from cogs.calendar.academic_cal import events_from_webpage, getMonthAndDate, findEvent, formatFind
import calendar
from datetime import date, datetime, timedelta, timezone

class AcadCal(commands.Cog) :
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(description="Prints the current month's calendar and events.",
                             aliases=["cal"])
    async def print(self, ctx):
        
        dates = events_from_webpage()
        acadCalendar = getMonthAndDate(dates)

        # Create an emded for the message
        embedVar = discord.Embed(
            title=f"Upcoming Events for {calendar.month_name[datetime.now().month]}",
            description=f"```\n{acadCalendar[0]}\n```",
        )

        for event in acadCalendar[1]:
            embedVar.add_field(
                name = event['date'],
                value = event['event'],
                inline=False
            )

        await ctx.send(embed=embedVar)
    
    @print.error
    async def print_calendar_error(self, ctx, error):
        print(error)
    
    @commands.command(description="Finds relavant events.",  aliases=["find"])
    async def findExact(self, ctx:Context, *, prompt:str):

        dates = events_from_webpage()
        eventsList = findEvent(prompt, dates.values())
        finds = formatFind(eventsList)

        embedVar = discord.Embed(
            title=f'Showing matches for "' + prompt + '"'
        )

        for event in eventsList[0]:
            embedVar.add_field(
                name = event['date'],
                value = "[" + event['event'] + "](" + event['url'] + ")",
                inline = False
            )
        
        if len(eventsList[0]) == 0:
            embedVar.add_field(
                name = "",
                value = "Sorry! There are no events :(",
                inline = False
            )
        
        # add a button to ask if the user also wants a list of relevant events
        view = discord.ui.View()
        button = discord.ui.Button(
                label="Find Relevant", 
                style=discord.ButtonStyle.blurple,
                custom_id="find_relevant_button"
        )

        view.add_item(button)

        message = await ctx.send(embed=embedVar, view=view)

        async def button_clicked(interaction):
            await self.findRelevant(ctx, prompt=prompt)
            await interaction.response.send_message(content="")
        
        button.callback = button_clicked

    @findExact.error
    async def print_calendar_error(self, ctx, error):
        print(error)

    @commands.command(description="Finds relevant events.", aliases=["findOthers"])
    async def findRelevant(self, ctx:Context, *, prompt:str):

        dates = events_from_webpage()
        eventsList = findEvent(prompt, dates.values())
        finds = formatFind(eventsList)

        embedVar = discord.Embed(
            title=f'Showing Related Matches for "' + prompt + '"'
        )
        
        for event in eventsList[1]:
            embedVar.add_field(
                name = event['date'],
                value = event['event'],
                inline = False
            )

        if len(eventsList[1]) == 0:
            embedVar.add_field(
                name = "",
                value = "Sorry! There are no more relevant events :(",
                inline = False
            )

        await ctx.send(embed=embedVar)
    
    @findRelevant.error
    async def print_calendar_error(self, ctx, error):
        print(error)


async def setup(bot):
    await bot.add_cog(AcadCal(bot))