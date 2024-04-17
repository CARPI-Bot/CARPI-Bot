import datetime as dt
from datetime import timedelta, timezone

import discord
from discord.ext import commands
from discord.ext.commands import CommandError, Context

from bot import CARPIBot
from globals import (BAD_MEMBER_MSG, ERROR_TITLE, NO_PERM_MSG,
                     send_generic_error)


class Moderator(commands.Cog):
    def __init__(self, bot: CARPIBot):
        self.bot = bot

    async def cog_command_error(self, ctx: Context, error: CommandError) -> None:
        if not ctx.command.has_error_handler():
            await send_generic_error(ctx, error)
    
    ### CLEAR ###
    @commands.command(
        aliases = ["erase", "purge"],
        hidden = True
    )
    @commands.check_any(
        commands.has_permissions(manage_messages=True),
        commands.is_owner()
    )
    async def clear(self, ctx: Context, num: int):
        if num < 1:
            raise commands.BadArgument
        else:
            num_deleted = len(await ctx.channel.purge(limit=num+1)) - 1
            embed_title = f"{num_deleted} messages deleted"
        embed_var = discord.Embed(
            title = embed_title,
            color = discord.Color.green()
        )
        await ctx.send(embed=embed_var, delete_after=3)

    @clear.error
    async def clear_error(self, ctx: Context, error: CommandError):
        embed_var = discord.Embed(
            title = ERROR_TITLE,
            color = discord.Color.red()
        )
        if isinstance(error, commands.CheckFailure):
            embed_var.description = NO_PERM_MSG
        elif isinstance(error, commands.MissingRequiredArgument):
            embed_var.title = "Incorrect usage"
            embed_var.description = f"Usage: `{self.bot.command_prefix}clear <num messages>`"
        elif isinstance(error, commands.BadArgument):
            embed_var.description = "Enter a valid integer."
        if embed_var.description:
            await ctx.send(embed=embed_var)
        else:
            await send_generic_error(ctx, error)

    ### TIMEOUT ###
    @commands.command(
        description = "Time out a user for a specified amount of time.",
        aliases = ["mute", "silence"],
        hidden = True
    )
    @commands.check_any(
        commands.has_permissions(moderate_members=True),
        commands.is_owner()
    )
    async def timeout(self, ctx: Context, member: discord.Member, *, time: str = ""):
        if len(time) == 0:
            raise commands.BadArgument
        time = time.strip().split()
        days, hrs, mins, secs = 0, 0, 0, 0
        for element in time:
            try:
                if element.lower().endswith("d"):
                    days += int(element[:-1])
                elif element.lower().endswith("h"):
                    hrs += int(element[:-1])
                elif element.lower().endswith("m"):
                    mins += int(element[:-1])
                elif element.lower().endswith("s"):
                    secs += int(element[:-1])
                else:
                    raise
            except:
                raise commands.BadArgument
        td = timedelta(days=days, hours=hrs, minutes=mins, seconds=secs)
        embed_var = discord.Embed(color=discord.Color.red())
        error_desc = None
        if member.is_timed_out():
            error_desc = "This user is already timed out."
        # Maximum possible timeout is 28 days (2,419,200 seconds)
        elif int(td.total_seconds()) >= 2419200:
            error_desc = "The maximum possible timeout duration is just under 28 days."
        if error_desc:
            embed_var.title = ERROR_TITLE
            embed_var.description = error_desc
            await ctx.send(embed=embed_var)
            return
        await member.timeout(td)
        days = td.days
        hrs = int(td / timedelta(hours=1)) % 24
        mins = int(td / timedelta(minutes=1)) % 60
        secs = int(td / timedelta(seconds=1)) % 60
        embed_var.title = f"{member.name} has been timed out"
        embed_var.description = f"Duration: `{days}D {hrs}H {mins}M {secs}S`"
        await ctx.send(embed=embed_var)
    
    @timeout.error
    async def timeout_error(self, ctx: Context, error: CommandError):
        embed_var = discord.Embed(
            title = ERROR_TITLE,
            color = discord.Color.red()
        )
        if isinstance(error, commands.CheckFailure):
            embed_var.description = NO_PERM_MSG
        elif isinstance(error, commands.MemberNotFound):
            embed_var.description = BAD_MEMBER_MSG
        elif isinstance(error, commands.BadArgument) or \
             isinstance(error, commands.MissingRequiredArgument):
            embed_var.title = "Incorrect usage"
            embed_var.description = f"Usage: `{self.bot.command_prefix}timeout " \
                                    + "<member> <days>d <hours>h <minutes>m <seconds>s`" \
                                    + "\nAt least one time field is required."
        if embed_var.description:
            await ctx.send(embed=embed_var)
        else:
            await send_generic_error(ctx, error)

    ### TIMEIN ###
    @commands.command(
        description = "Remove timeout from a user.",
        aliases = ["untimeout"],
        hidden = True
    )
    @commands.check_any(
        commands.has_permissions(moderate_members=True),
        commands.is_owner()
    )
    async def timein(self, ctx: Context, member: discord.Member):
        embed_var = discord.Embed(color=discord.Color.green())
        if not member.is_timed_out():
            embed_var.title = f"{member.name} is not timed out"
            await ctx.send(embed=embed_var)
            return
        remaining_secs = (member.timed_out_until - dt.datetime.now(timezone.utc)) \
                          .total_seconds()
        td = timedelta(seconds=remaining_secs)
        days = td.days
        hrs = int(td / timedelta(hours=1)) % 24
        mins = int(td / timedelta(minutes=1)) % 60
        secs = int(td / timedelta(seconds=1)) % 60
        await member.timeout(timedelta(seconds=0))
        embed_var.title = f"Removed timeout from {member.name}"
        embed_var.description = f"Remaining duration: `{days}D {hrs}H {mins}M {secs}S`"
        await ctx.send(embed=embed_var)
    
    @timein.error
    async def timein_error(self, ctx: Context, error: CommandError):
        embed_var = discord.Embed(
            title = ERROR_TITLE,
            color = discord.Color.red()
        )
        if isinstance(error, commands.CheckFailure):
            embed_var.description = NO_PERM_MSG
        elif isinstance(error, commands.MissingRequiredArgument):
            embed_var.title = "Incorrect usage"
            embed_var.description = f"Usage: `{self.bot.command_prefix}timein <member>`"
        elif isinstance(error, commands.MemberNotFound):
            embed_var.description = BAD_MEMBER_MSG
        if embed_var.description:
            await ctx.send(embed=embed_var)
        else:
            await send_generic_error(ctx, error)

async def setup(bot: commands.Bot):
    await bot.add_cog(Moderator(bot))