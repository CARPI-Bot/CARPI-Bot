import asyncio
import discord
from bot import CARPIBot
from globals import COMMAND_PREFIX, TOKEN

async def main():
    bot = CARPIBot(COMMAND_PREFIX, discord.Intents.all(), token=TOKEN)
    await bot.startup()

if __name__ == "__main__":
    asyncio.run(main())