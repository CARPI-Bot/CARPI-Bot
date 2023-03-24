import discord
from discord import app_commands
from discord.ext import commands

class SlashCommands(commands.Cog):

    def __init__(self, bot:commands.Bot):
        self.bot = bot
    
    @app_commands.command(name="add", description="Add two numbers together!")
    async def addition(self, interaction:discord.Interaction, num1:int, num2:int):
        await interaction.response.send_message(f"Your sum is {num1 + num2}")
    
async def setup(bot:commands.Bot):
    await bot.add_cog(SlashCommands(bot))