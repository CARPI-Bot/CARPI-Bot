import logging
from datetime import datetime, timedelta
from pathlib import Path

import aiomysql
import discord
from discord import app_commands, Interaction
from discord.app_commands import AppCommandError
from discord.ext import commands, tasks

from bot import CARPIBot
from globals import BASE_DIR


class AcademicCalendar(commands.Cog):
    def __init__(self, bot: CARPIBot):
        self.bot = bot
        self.db_conn = None
        query_path = Path(__file__).with_name("month_data.sql")
        with query_path.open() as query:
            self.query = query.read()

    async def cog_load(self) -> None:
        self.db_conn = await self.bot.sql_conn_pool.acquire()
    
    async def cog_unload(self) -> None:
        self.bot.sql_conn_pool.release(self.db_conn)

    @app_commands.command(
        name = "calendar",
        description = "Browse RPI's academic calendar within Discord!"
    )
    @app_commands.checks.cooldown(rate=1, per=30)
    @app_commands.describe(
        public = "Should other people be able to see and interact with the menu?"
    )
    async def calendar(self, interaction: Interaction, public: bool = False):
        view = CalendarMenu(interaction, self.db_conn, self.query)
        self.bot.loop.create_task(view.timeout_timer())
        thumbnail = discord.File(
            fp = BASE_DIR / "./assets/rpi_small_seal_red.png",
            filename = "rpi_small_seal_red.png"
        )
        await interaction.response.send_message(
            file = thumbnail,
            view = view,
            embed = view.embed,
            ephemeral = not public
        )
    
    @calendar.error
    async def calendar_error(self, interaction: Interaction, error: AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            embed = discord.Embed(
                title = "Slow down!",
                description = "You just saw the calendar! " +
                              "Try again in about 30 seconds.",
                color = discord.Color.red()
            )
            await interaction.response.send_message(
                embed = embed,
                ephemeral = True,
                delete_after = 5
            )
        else:
            print(error)

class CalendarMenu(discord.ui.View):
    def __init__(
        self,
        interaction: Interaction,
        db_conn: aiomysql.Connection,
        query: str
    ):
        super().__init__()
        self.interaction = interaction
        self.db_conn = db_conn
        self.query = query
        self.embed = discord.Embed(
            title = "Welcome to RPI's academic calendar!",
            description = "Choose a month's events to display "
                          + "from the dropdown menu below.",
            color = 0xD6001C
        )
        self.embed.set_thumbnail(url="attachment://rpi_small_seal_red.png")
        select_options = []
        self.month_names = (
            "January", "February", "March", "April", "May", "June", "July", "August",
            "September", "October", "November", "December"
        )
        for i, month in enumerate(self.month_names):
            select_options.append(
                discord.SelectOption(
                    label = month,
                    value = i + 1
                )
            )
        dropdown = CalendarDropdown(
            placeholder = "Choose a month",
            options = select_options
        )
        self.add_item(dropdown)
    
    async def timeout_timer(self) -> None:
        await discord.utils.sleep_until(datetime.now() + timedelta(minutes=15))
        await self.on_timeout()

    async def on_timeout(self) -> None:
        await self.interaction.followup.send("penis")
        for item in self.children:
            item.disabled = True
        self.embed.set_footer(text="This menu has expired due to inactivity.")
        await self.interaction.edit_original_response(view=self, embed=self.embed)

class CalendarDropdown(discord.ui.Select):
    def __init__(
        self,
        options: list[discord.SelectOption],
        placeholder: str,
        **kwargs
    ):
        super().__init__(
            options = options,
            placeholder = placeholder,
            **kwargs
        )
    
    async def callback(self, interaction: Interaction) -> None:
        month_name = self.view.month_names[int(self.values[0]) - 1]
        selected_year = str(datetime.now().year)
        self.view.embed.title = f"Events for {month_name}"
        self.view.embed.description = None
        self.view.embed.clear_fields()
        async with self.view.db_conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(
                self.view.query,
                [self.values[0], self.values[0], selected_year, selected_year]
            )
            events = await cursor.fetchall()
            if events is None or len(events) == 0:
                logging.warn(f"Calendar command yielded no events for {month_name}")
                self.view.embed.description = \
                    "No events found for this month." \
                    + " This is probably an error on our part, sorry!"
            else:
                for event in events:
                    format_date = event["date_start"].strftime(r"%B %d, %Y")
                    if event["date_end"] is not None:
                        format_date += f" - {event['date_end'].strftime(r'%B %d, %Y')}"
                    self.view.embed.add_field(
                        name = format_date,
                        value = event["title"],
                        inline = False
                    )
        await interaction.response.edit_message(embed=self.view.embed)
        
async def setup(bot: commands.Bot):
    await bot.add_cog(AcademicCalendar(bot))