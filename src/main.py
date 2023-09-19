import asyncio
from bot import Bot
from globals import *

async def main():
    bot = Bot(COMMAND_PREFIX, discord.Intents.all())
    await bot.start(bot.token)

if __name__ == "__main__":
    asyncio.run(main())