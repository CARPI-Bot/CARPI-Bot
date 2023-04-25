import asyncio
from src.bot import Bot
from globals import *

async def main():
    bot = Bot(COMMAND_PREFIX, discord.Intents.all())
    await bot.start(bot.get_token())

if __name__ == "__main__":
    asyncio.run(main())