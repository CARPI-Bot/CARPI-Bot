import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path

import discord

from bot import CARPIBot
from globals import CMD_PREFIX, TOKEN

class ColoredFormatter(logging.Formatter):
    """
    Simple wrapper class that adds colors to logging. Requires a
    format, and otherwise accepts any kwargs that are accepted by
    logging.Formatter().
    """
    def __init__(self, fmt: str, **kwargs):
        self._fmt = fmt
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
            fmt = f"{color}{self._fmt}{self._reset_color}"
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
    logfile_path = Path(f"./logs/{curr_time}.log").resolve()
    logfile_path.touch()
    file_handler = logging.FileHandler(
        filename = logfile_path,
        encoding = "utf-8"
    )
    file_handler.setLevel(log_level)
    # Normal Formatter is used instead of ColoredFormatter for file
    # logging because colors would just render as text.
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
    # Main program loop
    await bot.start(TOKEN)

if __name__ == "__main__":
    logging_init()
    discordpy_ver = discord.__version__
    python_ver = ".".join(str(ver) for ver in sys.version_info[:3])
    logging.info(f"discord.py version {discordpy_ver}")
    logging.info(f"Python version {python_ver}")
    asyncio.run(main())