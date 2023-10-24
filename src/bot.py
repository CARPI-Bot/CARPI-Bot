import discord
from discord.ext import commands
import os
import sys
from globals import *

class CARPIBot(commands.Bot):
    def __init__(self, prefix:str, intents:discord.Intents, token:str):
        super().__init__(command_prefix=prefix, intents=intents)
        self.loaded_cogs = []
        self.token = token
        python_ver = ".".join(str(ver) for ver in sys.version_info[:3])
        log_info("Bot client initialized")
        log_info(f"discord.py version {discord.__version__} | Python version {python_ver}")

    async def setup_hook(self) -> None:
        log_info("Loading cogs...")
        await self.load_cogs(getResourcePath(cogs_dir_rel_path))
    
    async def on_ready(self) -> None:
        await self.consoleHandler()

    # Given a relative path to a directory, attempts to load all Python files within
    # and recursively within its subdirectories as extensions to the bot.
    async def load_cogs(self, rel_path:str) -> None:
        # Converts the relative path into an absolute one
        path = getResourcePath(rel_path)
        dir_basename = os.path.basename(path)
        if not os.path.isdir(path):
            log_err(f"Extensions directory \"{rel_path}\" is not valid!")
            sys.exit(1)
        async def recursive_load(path:str) -> None:
            for file_name in os.listdir(path):
                new_path = os.path.join(path, file_name).replace("\\", "/")
                if os.path.isdir(new_path):
                    await recursive_load(new_path)
                else:
                    if os.path.splitext(new_path)[1] == ".py":
                        # Formats the path to a module-like name like "cogs.calculator"
                        cog = os.path.splitext(new_path)[0] \
                            .replace("/", ".")[new_path.find(dir_basename):]
                        try:
                            await self.load_extension(cog)
                        except commands.ExtensionNotFound:
                            log_warn(f"{cog} could not be found! Ignoring...")
                        except commands.ExtensionAlreadyLoaded:
                            log_warn(f"{cog} is already loaded! Ignoring...")
                        except commands.NoEntryPointError:
                            log_warn(f"{cog} has no setup() function! Ignoring...")
                        except Exception as err:
                            log_warn(f"{err}, ignoring...")
                        else:
                            self.loaded_cogs.append(cog)
        await recursive_load(path)
                        
    async def consoleHandler(self) -> None:
        num_synced = len(await self.tree.sync())
        log_info(f"Logged in as {self.user.name}#{self.user.discriminator}")
        if len(self.loaded_cogs) == 0:
            log_warn("No extensions were loaded!")
        else:
            log_info(f"Loaded {len(self.loaded_cogs)} extension(s), {num_synced} commands synced:")
            for cog in self.loaded_cogs:
                print(f"\t{cog}")
        if len(self.guilds) == 0:
            log_warn("Bot is not currently in any guilds!")
        else:
            log_info(f"Deployed in {len(self.guilds)} guild(s):")
            for guild in self.guilds:
                print(f"\t{guild.name}")
    
    async def startup(self):
        await self.start(self.token)