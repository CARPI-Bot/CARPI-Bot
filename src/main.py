import sys
import asyncio
import logging
from datetime import datetime
from pathlib import Path

import discord

from bot import CARPIBot
from globals import CMD_PREFIX, TOKEN, getAbsPath

def logging_init(log_level: int = logging.INFO) -> None:
    """
    Initializes logging settings once on startup; these settings
    determine the behavior of all logging calls within this project.
    """
    # Logging format config
    log_formatter = logging.Formatter(
        fmt = "[%(asctime)s %(levelname)s] %(message)s",
        datefmt = "%H:%M:%S"
    )

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Console logging
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(log_formatter)
    root_logger.addHandler(console_handler)

    # File logging
    curr_time = datetime.now().strftime("%Y.%m.%d %H.%M.%S")
    # Path.mkdir(exist_ok=True) for whatever reason throws an error if
    # a "./logs" directory exists, band-aid solution was to just stick
    # it inside a try/except block.
    try:
        Path.mkdir("./logs", exist_ok=True)
        logging.info('No "./logs" directory detected, creating one for you...')
    except:
        pass
    logfile_path = Path(getAbsPath(f"logs/{curr_time}.log"))
    logfile_path.touch()
    file_handler = logging.FileHandler(
        filename = logfile_path,
        encoding = "utf-8"
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(log_formatter)
    root_logger.addHandler(file_handler)

async def main():
    """
    Make sure all privileged intents are enabled in the Discord
    developer portal!
    
    You can access it using the link below:
    https://discord.com/developers/applications
    """
    bot = CARPIBot(
        prefix = CMD_PREFIX,
        intents = discord.Intents.all()
    )
    await bot.start(TOKEN)

if __name__ == "__main__":
    logging_init()
    # Main program loop
    asyncio.run(main())