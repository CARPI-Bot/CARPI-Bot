import sys
import asyncio
import logging
from datetime import datetime
from pathlib import Path

import discord

from bot import CARPIBot
from globals import CMD_PREFIX, TOKEN, getAbsPath

class ColoredFormatter(logging.Formatter):
    """
    Wrapper class that simply adds coloring to logging.Formatter.
    Requires a format and date format, but also accepts any kwargs
    accepted by logging.Formatter().
    """
    def __init__(self, fmt: str, datefmt: str, **kwargs):
        self._fmt = fmt
        self._datefmt = datefmt
        self._kwargs = kwargs
        self._reset_color = "\x1b[0m"
        self._COLORS = {
            logging.DEBUG: "\x1b[38;20m", # Gray
            logging.INFO: "\x1b[38;20m", # Gray
            logging.WARNING: "\x1b[33;20m", # Yellow
            logging.ERROR: "\x1b[31;20m", # Red
            logging.CRITICAL: "\x1b[31;1m" # Dark red
        }

    def format(self, record: logging.LogRecord) -> str:
        color = self._COLORS[record.levelno]
        formatter = logging.Formatter(
            **self._kwargs,
            fmt = f"{color}{self._fmt}{self._reset_color}",
            datefmt = self._datefmt,
        )
        return formatter.format(record)

def logging_init(log_level: int = logging.INFO) -> None:
    """
    Initializes logging settings once on startup; these settings
    determine the behavior of all logging calls within this project.
    """
    # Logging format config
    formatter_config = {
        "fmt": "[%(asctime)s %(levelname)s] %(message)s",
        "datefmt": "%H:%M:%S"
    }
    color_formatter = ColoredFormatter(**formatter_config)
    formatter = logging.Formatter(**formatter_config)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Console logging
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(color_formatter)
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
    file_handler.setFormatter(formatter)
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