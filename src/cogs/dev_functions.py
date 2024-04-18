import logging

import discord
from discord.ext import commands
from discord.ext.commands import CommandError, Context

from bot import CARPIBot
from globals import ERROR_TITLE, NO_PERM_MSG, send_generic_error


class DeveloperFunctions(commands.Cog):
    def __init__(self, bot: CARPIBot):
        self.bot = bot

    def cog_check(self, ctx: Context) -> bool:
        return ctx.author.id in self.bot.owner_ids
    
    async def cog_command_error(self, ctx: Context, error: CommandError) -> None:
        if not ctx.command.has_error_handler():
            await send_generic_error(ctx, error)
        elif isinstance(error, commands.CheckFailure):
            embed_var = discord.Embed(
                title = ERROR_TITLE,
                description = NO_PERM_MSG,
                color = discord.Color.red()
            )
            await ctx.send(embed=embed_var)
        else:
            await send_generic_error(ctx, error)
    
    ### SHUTDOWN ###
    @commands.command(
        name = "shutdown",
        aliases = ["stop", "close", "kill"],
        hidden = True
    )
    async def shutdown(self, ctx: Context):
        embed_var = discord.Embed(
            title = "Shutting down...",
            color = discord.Color.red()
        )
        await ctx.send(embed=embed_var)
        await self.bot.close()
    
    ### RELOAD ###
    @commands.command(
        name = "reload",
        aliases = ["refresh"],
        hidden = True
    )
    async def reload(self, ctx: Context):
        logging.info("Reloading extensions")
        cogs_status = await self.bot.load_cogs()
        embed_var = discord.Embed(
            title = "Extensions successfully reloaded!",
            color = discord.Color.green()
        )
        field_names = ("Loaded", "Unloaded", "Problem")
        for i, category in enumerate(cogs_status):
            if len(category) == 0:
                continue
            embed_var.add_field(
                name = f"{field_names[i]} cogs:",
                value = "\n".join(f"`{cog}`" for cog in category),
                inline = False
            )
        if len(cogs_status[2]) > 0:
            embed_var.title = "There was a problem with some extensions"
            embed_var.color = discord.Color.red()
            embed_var.set_footer(text="Check the console for more details.")
        await ctx.send(embed=embed_var)
    
    ### SYNC ###
    @commands.command(
        name = "sync",
        aliases = ["globalsync", "synccommands", "synccmds"],
        hidden = True
    )
    @commands.check(commands.is_owner())
    async def sync(self, ctx: Context):
        embed_var = discord.Embed(
            title = "Syncing application commands...",
            description = "If this is taking a while, you might be getting ratelimited.",
            color = discord.Color.red()
        )
        message = await ctx.send(embed=embed_var)
        logging.info("Syncing application commands")
        synced_cmds = await self.bot.tree.sync()
        logging.info("Application commands synced")
        embed_var.title = "Successfully synced application commands!"
        embed_var.description = None
        embed_var.color = discord.Color.green()
        display_val = ""
        row_count = 0
        for i, cmd in enumerate(synced_cmds):
            cmd_string = f"`{cmd.name}`\n"
            # Maximum allowed length for embed field value is 1024 characters
            if (len(cmd_string) + len(display_val) >= 1024 
                or row_count >= len(synced_cmds) // 3
                or i == len(synced_cmds) - 1):
                embed_var.add_field(
                    name = "",
                    value = display_val.strip("\n"),
                    inline = True
                )
                display_val = cmd_string
                row_count = 0
            else:
                display_val += cmd_string
                row_count += 1
        await message.edit(embed=embed_var)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(DeveloperFunctions(bot))