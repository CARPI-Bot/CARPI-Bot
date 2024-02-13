import logging
import re
from pathlib import Path
from typing import Tuple

import discord
from discord.ext import commands
from discord.ext.commands import CommandError, Context

from globals import OWNER_IDS


class CARPIBot(commands.Bot):
    def __init__(self, prefix: str, intents: discord.Intents):
        super().__init__(
            command_prefix = prefix,
            intents = intents,
            owner_ids = OWNER_IDS
        )
        logging.info("Bot initialized")

    async def setup_hook(self) -> None:
        await self.load_cogs()
    
    async def on_ready(self) -> None:
        logging.info(f"Logged in as {self.user.name}#{self.user.discriminator}")
        if len(self.guilds) == 0:
            logging.warn("Bot is not in any guilds!")
        else:
            logging.info(f"Deployed in {len(self.guilds)} guild(s):")
            for guild in self.guilds:
                logging.info(f"\t{guild.name}")
    
    async def on_command_error(self, ctx: Context, error: CommandError) -> None:
        """
        Overridden function to silence all command errors by default.
        This behavior is ignored for any command that has a local error handler
        or if cog_command_error() is implemented in the command's parent cog.
        """
        pass

    async def load_cogs(self, rel_path: str = "./cogs") -> Tuple[Tuple[str]]:
        """
        Loads all extensions recursively within the given directory to
        the bot, and unloads any extensions that went missing since
        before this function's execution.

        Returns a tuple in the format:
        (reloaded_cogs, new_cogs, unloaded_cogs, bad_cogs)
        """
        abs_path = Path(rel_path).resolve()
        if not abs_path.is_dir():
            logging.error(f'Extensions directory "{rel_path}" is not valid!')
            return
        reloaded_cogs, new_cogs, unloaded_cogs, bad_cogs = set(), set(), set(), set()
        
        async def recursive_load(dir: Path, present_cogs: set = set()) -> set:
            """
            Does the actual loading of cogs. Returns a set containing
            the module names of all successfully loaded cogs present in
            the cogs directory at the time of this function's execution.
            """
            for file_name in dir.iterdir():
                new_path = dir / file_name
                if new_path.is_dir():
                    await recursive_load(new_path, present_cogs)
                elif new_path.suffix == ".py":
                    # Formats absolute path to an importable name like "cogs.calculator"
                    cog = re.sub(
                        pattern = R"[\\/]",
                        repl = ".",
                        string = str(new_path.relative_to(Path.cwd()).parent
                                 / Path(new_path.stem))
                    )
                    try:
                        if cog not in self.extensions.keys():
                            logging.info(f"Loading extension {cog}")
                            await self.load_extension(cog)
                            new_cogs.add(cog)
                        else:
                            logging.info(f"Reloading extension {cog}")
                            await self.reload_extension(cog)
                            reloaded_cogs.add(cog)
                    except Exception as err:
                        if isinstance(err, commands.ExtensionNotFound):
                            err_log = f"{cog} could not be found! Ignoring..."
                        elif isinstance(err, commands.ExtensionAlreadyLoaded):
                            err_log = f"{cog} is already loaded! Ignoring..."
                        elif isinstance(err, commands.NoEntryPointError):
                            err_log = f"{cog} has no setup() function! Ignoring..."
                        else:
                            err_log = f"{err}, ignoring..."
                        logging.warn(err_log)
                        bad_cogs.add(cog)
                    else:
                        present_cogs.add(cog)
            return present_cogs
        
        present_cogs = await recursive_load(abs_path)
        for missing_cog in set(self.extensions.keys()) - present_cogs:
            try:
                logging.info(f"Unloading extension {missing_cog}")
                await self.unload_extension(missing_cog)
                unloaded_cogs.add(missing_cog)
            except Exception as err:
                if isinstance(err, commands.ExtensionNotFound):
                    err_log = f"{missing_cog} could not be found! Ignoring..."
                if isinstance(err, commands.ExtensionNotLoaded):
                    err_log = f"{missing_cog} is already unloaded! Ignoring..."
                logging.warn(err_log)
                bad_cogs.add(missing_cog)
        await self.tree.sync()
        loaded_cogs = set(self.extensions.keys())
        if len(loaded_cogs) == 0:
            logging.warn("No extensions were loaded!")
        else:
            logging.info(f"Loaded {len(loaded_cogs)} extension(s):")
            for cog in loaded_cogs:
                logging.info(f"\t{cog}")

        return (reloaded_cogs, new_cogs, unloaded_cogs, bad_cogs)