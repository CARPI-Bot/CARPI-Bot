import os
import sys
import discord
from discord.ext import commands
from globals import *

class CARPIBot(commands.Bot):
    def __init__(self, prefix:str, intents:discord.Intents, token:str):
        super().__init__(command_prefix=prefix, intents=intents)
        self.loaded_cogs = []
        self.token = token

        python_ver = ".".join(str(ver) for ver in sys.version_info[:3])
        print(
            "Bot client initialized",
            f"Discord.py version {discord.__version__} | Python version {python_ver}",
            sep="\n"
        )

    async def setup_hook(self) -> None:
        print("Loading cogs")
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
            print(f"[ERROR] Extensions directory \"{rel_path}\" is not valid!")
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
                            print(f"[WARNING] {cog} could not be found! Ignoring...")
                        except commands.ExtensionAlreadyLoaded:
                            print(f"[WARNING] {cog} is already loaded! Ignoring...")
                        except commands.ExtensionFailed:
                            print(f"[WARNING] {cog} failed to execute! Ignoring...")
                        except commands.NoEntryPointError:
                            print(f"[WARNING] {cog} has no setup() function! Ignoring...")
                        except Exception as err:
                            print(f"{err}")
                        else:
                            self.loaded_cogs.append(cog)
        await recursive_load(path)
                        
    async def consoleHandler(self) -> None:
        num_synced = len(await self.tree.sync())
        print(f"Logged in as {self.user.name}#{self.user.discriminator}")
        if len(self.loaded_cogs) == 0:
            print("[WARNING] No extensions were loaded")
        else:
            print(
                f"Loaded {len(self.loaded_cogs)} extension(s),",
                f"{num_synced} commands synced:"
            )
            for cog in self.loaded_cogs:
                print(f"\t{cog}")
        if len(self.guilds) == 0:
            print("[WARNING] Bot is not currently in any guilds")
        else:
            print(f"Deployed in {len(self.guilds)} guild(s):")
            for guild in self.guilds:
                print(f"\t{guild.name}")
    
    async def startup(self):
        await self.start(self.token)