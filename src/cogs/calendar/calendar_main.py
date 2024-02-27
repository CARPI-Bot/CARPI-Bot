import calendar
from datetime import datetime

import discord
from discord.ext import commands
from discord.ext.commands import CommandError, Context

from cogs.calendar.academic_cal import (events_from_webpage, findEvent,
                                        getMonthAndDate, getWeekAndDate)
from globals import *


class AcadCal(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    # Command to print the current month's calendar and events
    @commands.command(
        description = "Prints the current month's calendar and events.",
        aliases = ["month"]
    )
    async def print(self, ctx: Context):
        # Fetching events data from a webpage
        dates = await events_from_webpage()
        acadCalendar = getMonthAndDate(dates)
        # Creating an embed for the message
        embedVar = discord.Embed(
            title = f"Upcoming Events for {calendar.month_name[datetime.now().month]}",
            description = f"```\n{acadCalendar[0]}\n```",
        )
        # Adding the events for the current month to the embed
        for event in acadCalendar[1]:
            embedVar.add_field(
                name = event['date'],
                value = event['event'],
                inline = False
            )
        # Sending the embed as a message
        await ctx.send(embed=embedVar)
    
    # Handling errors for the print command
    @print.error
    async def print_error(self, ctx: Context, error: CommandError):
        await send_generic_error(ctx, error)
        
    # Command to print the current week's calendar and events
    @commands.command(
        description = "Prints the current week's calendar and events.",
        aliases = ["week"]
    )
    async def print_week(self, ctx: Context):
        # Fetching events data from a webpage
        dates = await events_from_webpage()
        weekEvents = getWeekAndDate(dates)
        # Creating an embed for the message
        embedVar = discord.Embed(
            title = f"Upcoming Events for the week"
        )
        # Adding the events for the current week to the embed
        for event in weekEvents:
            embedVar.add_field(
                name = event['date'],
                value = event['event'],
                inline = False
            )
        # Sending the embed as a message
        await ctx.send(embed=embedVar)

    # Handling errors for the print_week command
    @print_week.error
    async def print_week_error(self, ctx: Context, error: CommandError):
        await send_generic_error(ctx, error)

    # Command to find exact matches for a given prompt
    @commands.command(
        description = "Finds relevant events.",
        aliases = ["find"]
    )
    async def findexact(self, ctx: Context, *, prompt: str):
        # Fetching events data from a webpage
        dates = await events_from_webpage()
        eventsList = findEvent(prompt, dates.values())
        # Creating an embed for the message
        embedVar = discord.Embed(
            title = f'Showing matches for "' + prompt + '"'
        )
            
        # If there are no matches, adding a message to the embed
        if len(eventsList[0]) == 0:
            embedVar.add_field(
                name = "",
                value = "Sorry! There are no events :(",
                inline = False
            )
        else:
            # otherwise add matched events to the embed
            for event in eventsList[0]:
                embedVar.add_field(
                    name = event['date'],
                    value = "[" + event['event'] + "](" + event['url'] + ")",
                    inline = False
                )
        # Adding a button to ask if the user also wants a list of relevant events
        view = discord.ui.View()
        button = discord.ui.Button(
            label = "Find Other Relevant Events", 
            style = discord.ButtonStyle.blurple,
            custom_id = "find_relevant_button"
        )
        view.add_item(button)
        # Sending the embed with the button
        await ctx.send(embed=embedVar, view=view)
        # Handling button click event
        async def button_clicked(interaction):
            await self.findRelevant(ctx, prompt=prompt)
            await interaction.response.send_message(content="")
        button.callback = button_clicked

    # Handling errors for the findExact command
    @findexact.error
    async def findexact_error(self, ctx: Context, error: CommandError):
        await send_generic_error(ctx, error)

    # Command to find other relevant events based on a prompt
    @commands.command(
        description = "Finds relevant events.",
        aliases = ["findOthers"]
    )
    async def findrelevant(self, ctx: Context, *, prompt: str):
        # Fetching events data from a webpage
        dates = await events_from_webpage()
        eventsList = findEvent(prompt, dates.values())
        # Creating an embed for the message
        embedVar = discord.Embed(
            title = f'Showing Related Matches for "' + prompt + '"'
        )
        # If there are no matches, adding a message to the embed
        if len(eventsList[1]) == 0:
            embedVar.add_field(
                name = "",
                value = "Sorry! There are no more relevant events :(",
                inline = False
            )
        else: 
            # otherwise add related events to the embed
            for event in eventsList[1]:
                embedVar.add_field(
                    name = event['date'],
                    value = event['event'],
                    inline = False
                )
        # Sending the embed as a message
        await ctx.send(embed=embedVar)
    
    # Handling errors for the findRelevant command
    @findrelevant.error
    async def findrelevant_error(self, ctx: Context, error: CommandError):
        await send_generic_error(ctx, error)

async def setup(bot: commands.Bot):
    await bot.add_cog(AcadCal(bot))