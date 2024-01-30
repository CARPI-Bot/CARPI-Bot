import sys
import asyncio
import logging
from datetime import datetime
from pathlib import Path
import discord
from bot import CARPIBot
from globals import COMMAND_PREFIX, TOKEN, getResourcePath

async def main():
    bot = CARPIBot(
        prefix = COMMAND_PREFIX,
        intents = discord.Intents.all(),
        token = TOKEN
    )
    await bot.startup()

if __name__ == "__main__":
    # Logging config
    curr_time = datetime.now().strftime("%Y.%m.%d %H.%M.%S")
    logfile_path = Path(getResourcePath(f"logs/{curr_time}.log"))
    logfile_path.touch()
    log_level = logging.INFO
    log_formatter = logging.Formatter(
        fmt = "[%(asctime)s %(levelname)s] %(message)s",
        datefmt = "%H:%M:%S"
    )

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # File logging
    file_handler = logging.FileHandler(
        filename = logfile_path,
        encoding = "utf-8"
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(log_formatter)
    root_logger.addHandler(file_handler)

    # Console logging
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(log_formatter)
    root_logger.addHandler(console_handler)

    # Main program loop
    asyncio.run(main())