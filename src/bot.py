import asyncio
import logging
import re
import signal
from pathlib import Path

import aiomysql
import discord
from discord.ext import commands
from discord.ext.commands import CommandError, Context

from globals import OWNER_IDS, CONFIG


class CARPIBot(commands.Bot):
    def __init__(self, prefix: str, intents: discord.Intents, **kwargs):
        super().__init__(
            command_prefix = prefix,
            intents = intents,
            owner_ids = OWNER_IDS,
            **kwargs
        )
        # Intercepts CTRL+C signal and properly closes bot
        signal.signal(
            signal.SIGINT,
            lambda *args: asyncio.create_task(self.close())
        )
        # Initialized in self.setup_hook()
        self.sql_conn_pool = None
        logging.info("Bot initialized")

    async def setup_hook(self) -> None:
        try:
            self.sql_conn_pool = await aiomysql.create_pool(
                **CONFIG["sql_login"],
                db = CONFIG["sql_schema"]
            )
            logging.info("MySQL database connection pool initialized")
        except:
            logging.fatal(
                "Couldn't connect to MySQL database! Make sure the server is running "
                + "and login info is correct"
            )
            await self.close()
        await self.load_cogs()
    
    async def on_ready(self) -> None:
        logging.info(f"Logged in as {self.user.name}#{self.user.discriminator}")
        if len(self.guilds) == 0:
            logging.warn("Bot is not in any guilds!")
        else:
            logging.info(f"Deployed in {len(self.guilds)} guild(s):")
            for guild in self.guilds:
                logging.info(f"\t{guild.name}")

    async def close(self) -> None:
        """
        Overriden function to provide fine control over closing the bot.

        This is because commands.Bot.close() sometimes raises a noisy
        "Unclosed Connector" error, a bug on aiohttp's part according
        to discord.py's Discord server.
        """
        logging.info("Closing bot...")
        if self.sql_conn_pool is not None:
            self.sql_conn_pool.close()
            self.sql_conn_pool.terminate()
            await self.sql_conn_pool.wait_closed()
        try:
            await super().close()
        except asyncio.CancelledError:
            await self.http.close()
    
    async def on_command_error(self, ctx: Context, error: CommandError) -> None:
        """
        Overridden function to silence all command errors by default.
        This behavior is ignored for any command that has a local
        error handler or if cog_command_error() is implemented in the
        command's parent cog.
        """
        pass

    async def load_extension(self, name: str, *, package: str | None = None) -> None:
        logging.info(f"Loading extension {name}")
        await super().load_extension(name, package=package)

    async def unload_extension(self, name: str, *, package: str | None = None) -> None:
        logging.info(f"Unloading extension {name}")
        await super().unload_extension(name, package=package)

    async def load_cogs(self, rel_path: str = "./cogs") -> tuple[tuple[str]]:
        """
        Unloads any extensions currently loaded into the bot, then
        loads any extensions recursively within rel_path into the bot.
        Keeps track of successfully loaded cogs, cogs that were removed
        since before this function call, and cogs that raise errors.

        Returns a tuple in the format:
        (loaded_cogs, unloaded_cogs, bad_cogs)
        """
        abs_path = Path(rel_path).resolve()
        if not abs_path.is_dir():
            logging.error(f'Extensions directory "{rel_path}" is not valid!')
            return
        unloaded_cogs = set(await self.unload_cogs())
        bad_cogs = set()
        
        async def recursive_load(dir: Path) -> set[str]:
            """
            Does the actual loading of cogs. Returns a set containing
            the module names of all successfully loaded cogs.
            """
            for file_name in dir.iterdir():
                new_path = dir / file_name
                if new_path.is_dir():
                    await recursive_load(new_path)
                elif new_path.suffix == ".py":
                    # Formats absolute path to an importable name like "cogs.calculator"
                    cog = re.sub(
                        pattern = R"[\\/]",
                        repl = ".",
                        string = str(new_path.relative_to(Path.cwd()).parent
                                 / Path(new_path.stem))
                    )
                    try:
                        await self.load_extension(cog)
                    except Exception as err:
                        log_bad_cog = True
                        if isinstance(err, commands.ExtensionNotFound):
                            err_log = f"{cog} could not be found! Ignoring..."
                        elif isinstance(err, commands.ExtensionAlreadyLoaded):
                            err_log = f"{cog} is already loaded! Ignoring..."
                        elif isinstance(err, commands.NoEntryPointError):
                            err_log = f"{cog} has no setup() function! Ignoring..."
                            log_bad_cog = False
                        else:
                            err_log = f"{err}, ignoring..."
                        logging.warn(err_log)
                        if log_bad_cog:
                            bad_cogs.add(cog)
            return self.extensions.keys()
        
        loaded_cogs = await recursive_load(abs_path)
        for missing_cog in unloaded_cogs.intersection(loaded_cogs):
            unloaded_cogs.remove(missing_cog)
        if len(loaded_cogs) == 0:
            logging.warn("No extensions were loaded!")
        else:
            logging.info(f"Loaded {len(loaded_cogs)} extension(s):")
            for cog in loaded_cogs:
                logging.info(f"\t{cog}")
        return (loaded_cogs, unloaded_cogs, bad_cogs)
    
    async def unload_cogs(self) -> tuple[str]:
        """
        Unconditionally unloads all of the bot's loaded extensions.
        """
        unloaded_cogs = []
        for cog in set(self.extensions.keys()):
            try:
                await self.unload_extension(cog)
                unloaded_cogs.append(cog)
            except Exception as err:
                if isinstance(err, commands.ExtensionNotFound):
                    err_log = f"{cog} could not be found! Ignoring..."
                if isinstance(err, commands.ExtensionNotLoaded):
                    err_log = f"{cog} is already unloaded! Ignoring..."
                logging.warn(err_log)
        return tuple(unloaded_cogs)