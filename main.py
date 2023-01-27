import discord
from discord.ext import commands
from globals import TOKEN

bot = commands.Bot(command_prefix="?", owner_id=230003732836909056, intents=discord.Intents.all())

def main():
    bot.run(TOKEN)
    
if __name__ == "__main__":
    main()