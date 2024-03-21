import json
from pathlib import Path

import discord
from discord import app_commands, Interaction
from discord.app_commands import AppCommandError
from discord.ext import commands


class AcademicCalendar(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        with Path("./assets/acadcal_2024.json").resolve().open() as infile:
            self.calendar_dict = json.load(infile)

    @app_commands.command(
        name = "calendar",
        description = "See RPI's academic calendar from within Discord!"
    )
    @app_commands.checks.cooldown(rate=1, per=5)
    async def calendar(self, interaction: Interaction):
        view_var = CalendarMenu(interaction, self.calendar_dict)
        thumbnail = discord.File(
            fp = Path("./assets/rpi_small_seal_red.png").resolve(),
            filename = "rpi_small_seal_red.png"
        )
        await interaction.response.send_message(
            file = thumbnail,
            view = view_var,
            embed = view_var.embed_var,
            ephemeral = True
        )
    
    @calendar.error
    async def calendar_error(self, interaction: Interaction, error: AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            embed_var = discord.Embed(
                title = "Slow down!",
                description = "You just saw the calendar! " +
                              "Try again in about 5 seconds.",
                color = discord.Color.red()
            )
            await interaction.response.send_message(
                embed = embed_var,
                ephemeral = True,
                delete_after = 5
            )

class CalendarMenu(discord.ui.View):

    class CalendarDropdown(discord.ui.Select):
        def __init__(self, embed_var: discord.Embed, calendar_data: dict, **kwargs):
            super().__init__(**kwargs)
            self.embed_var = embed_var
            self.calendar_data = calendar_data
        
        async def callback(self, interaction: Interaction):
            self.embed_var.title = f"Events for {self.values[0]}"
            self.embed_var.description = None
            self.embed_var.clear_fields()
            for event in self.calendar_data[self.values[0]]:
                self.embed_var.add_field(
                    name = event["date"],
                    value = f"[{event['title']}]({event['url']})",
                    inline = False
                )
            await interaction.response.edit_message(embed=self.embed_var)

    def __init__(self, interaction: Interaction, calendar_data: dict):
        super().__init__()
        self.interaction = interaction
        self.calendar_data = calendar_data
        self.embed_var = discord.Embed(
            title = "Welcome to RPI's academic calendar!",
            description = "Choose a month's events to display "
                          + "from the dropdown menu below.",
            color = 0xD6001C
        )
        self.embed_var.set_thumbnail(url="attachment://rpi_small_seal_red.png")
        self.options = []
        for month in self.calendar_data:
            self.options.append(
                discord.SelectOption(label=month)
            )
        dropdown = self.CalendarDropdown(
            embed_var = self.embed_var,
            calendar_data = self.calendar_data,
            placeholder = "Choose a month",
            options = self.options
        )
        self.add_item(dropdown)

    async def on_timeout(self) -> None:
        for item in self.children:
            item.disabled = True
        self.embed_var.set_footer(text="This menu has expired due to inactivity.")
        await self.interaction.edit_original_response(view=self, embed=self.embed_var)
        
async def setup(bot: commands.Bot):
    await bot.add_cog(AcademicCalendar(bot))