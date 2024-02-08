import datetime as dt
from datetime import timezone

import discord
from discord.ext import commands
from discord.ext.commands.context import Context

from bot import CARPIBot
from globals import (BAD_MEMBER_MSG, ERROR_TITLE, NO_PERM_MSG,
                     send_generic_error)

Context = commands.Context

class Moderator(commands.Cog):
    def __init__(self, bot: CARPIBot):
        self.bot = bot

    async def cog_command_error(self, ctx: Context, error: Exception) -> None:
        if not ctx.command.has_error_handler():
            await send_generic_error(ctx, error)

    ### SHUTDOWN ###
    @commands.command(
        aliases = ["stop", "kill"],
        hidden = True
    )
    @commands.check(commands.is_owner())
    async def shutdown(self, ctx: Context):
        embed_var = discord.Embed(
            title = "Shutting down...",
            color = 0xC80000
        )
        await ctx.send(embed=embed_var)
        await self.bot.close()
    
    @shutdown.error
    async def shutdown_error(self, ctx: Context, error):
        if isinstance(error, commands.CheckFailure):
            embed_var = discord.Embed(
                title = ERROR_TITLE,
                description = NO_PERM_MSG,
                color = 0xC80000
            )
            await ctx.send(embed=embed_var)
        else:
            await send_generic_error(ctx, error)
    
    ### RELOAD ###
    @commands.command(
        aliases = ["refresh"],
        hidden = True
    )
    @commands.check(commands.is_owner())
    async def reload(self, ctx: Context):
        cogs_status = await self.bot.load_cogs()
        embed_var = discord.Embed(
            title = "Extensions successfully reloaded!",
            color = 0x00C500
        )
        field_names = ("Reloaded", "New", "Unloaded", "Problem")
        for i, category in enumerate(cogs_status):
            if len(category) == 0:
                continue
            embed_var.add_field(
                name = f"{field_names[i]} cogs:",
                value = "\n".join(f"`{cog}`" for cog in category),
                inline = False
            )
        if len(cogs_status[3]) > 0:
            embed_var.title = "There was a problem with some extensions"
            embed_var.color = 0xC80000
            embed_var.set_footer(text="Check the console for more details.")
        await ctx.send(embed=embed_var)

    @reload.error
    async def reload_error(self, ctx: Context, error):
        if isinstance(error, commands.CheckFailure):
            embed_var = discord.Embed(
                title = ERROR_TITLE,
                description = NO_PERM_MSG,
                color = 0xC80000
            )
            await ctx.send(embed=embed_var)
        else:
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
            try:
                num_deleted = len(await ctx.channel.purge(limit=num+1)) - 1
                embed_title = f"{num_deleted} messages deleted."
            except:
                raise
        embed_var = discord.Embed(
            title = embed_title,
            color = 0x00FF00
        )
        await ctx.send(embed=embed_var, delete_after=3)

    @clear.error
    async def clear_error(self, ctx: Context, error):
        embed_desc = None
        if isinstance(error, commands.CheckFailure):
            embed_desc = NO_PERM_MSG
        elif isinstance(error, commands.MissingRequiredArgument):
            embed_desc = f"Usage: `{self.bot.command_prefix}clear [number of messages]`"
        elif isinstance(error, commands.BadArgument):
            embed_desc = "Enter a valid integer."

        if embed_desc != None:
            embed_var = discord.Embed(
                title = ERROR_TITLE,
                description = embed_desc,
                color = 0xC80000
            )
            await ctx.send(embed=embed_var)
        else:
            await send_generic_error(ctx, error)

    ### TIMEOUT ###
    @commands.hybrid_command(
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
        days, hours, minutes, seconds = 0, 0, 0, 0
        for element in time:
            try:
                int(element[:-1])
            except:
                raise commands.BadArgument
            else:
                if element.lower().endswith("d"):
                    days += int(element[:-1])
                elif element.lower().endswith("h"):
                    hours += int(element[:-1])
                elif element.lower().endswith("m"):
                    minutes += int(element[:-1])
                elif element.lower().endswith("s"):
                    seconds += int(element[:-1])
                else:
                    raise commands.BadArgument
        # Corrects any overflowing time components
        if seconds >= 60:
            minutes += seconds // 60
            seconds %= 60
        if minutes >= 60:
            hours += minutes // 60
            minutes %= 60
        if hours >= 24:
            days += hours // 24
            hours %= 24
        error_desc = None
        if member.is_timed_out():
            error_desc = "This user is already timed out."
        # Maximum possible timeout is 28 days (2,419,200 seconds)
        elif days * 86400 + hours * 3600 + minutes * 60 + seconds > 2419200:
            error_desc = "The maximum possible timeout duration is 28 days."
        if error_desc is not None:
            embed_var = discord.Embed(
                title = ERROR_TITLE,
                description = error_desc,
                color = 0xC80000
            )
            await ctx.send(embed=embed_var)
            return
        await member.timeout(
            dt.timedelta(
                days = days,
                hours = hours,
                minutes = minutes,
                seconds = seconds
            )
        )
        embed_var = discord.Embed(
            title = f"{member.name} has been timed out",
            description = f"Duration: {days}D {hours}H {minutes}M {seconds}S",
            color = 0xC80000
        )
        await ctx.send(embed=embed_var)
    
    @timeout.error
    async def timeout_error(self, ctx: Context, error):
        embed_desc = None
        if isinstance(error, commands.CheckFailure):
            embed_desc = NO_PERM_MSG
        elif isinstance(error, commands.MemberNotFound):
            embed_desc = BAD_MEMBER_MSG
        elif isinstance(error, commands.BadArgument) or \
             isinstance(error, commands.MissingRequiredArgument):
            embed_desc = f"Usage: `{self.bot.command_prefix}timeout " \
            + "<member> <days>d <hours>h <minutes>m <seconds>s`" \
            + "\nAt least one time argument is required."

        if embed_desc != None:
            embed_var = discord.Embed(
                title = ERROR_TITLE,
                description = embed_desc,
                color = 0xC80000
            )
            await ctx.send(embed=embed_var)
        else:
            await send_generic_error(ctx, error)

    ### TIMEIN ###
    @commands.hybrid_command(
        description = "Remove timeout from a user.",
        aliases = ["untimeout"],
        hidden = True
    )
    @commands.check_any(
        commands.has_permissions(moderate_members=True),
        commands.is_owner()
    )
    async def timein(self, ctx: Context, member: discord.Member):
        if member.is_timed_out():
            remaining_seconds = (member.timed_out_until
                                 - dt.datetime.now(timezone.utc)).seconds
            days, hours, minutes, seconds = 0, 0, 0, remaining_seconds
            # Converts remaining seconds into time components
            if seconds >= 60:
                minutes += seconds // 60
                seconds %= 60
            if minutes >= 60:
                hours += minutes // 60
                minutes %= 60
            if hours >= 24:
                days += hours // 24
                hours %= 24
            await member.timeout(dt.timedelta(seconds=0))
            embed_var = discord.Embed(
                title = f"Removed timeout from {member.name}",
                description = "Remaining duration: "
                    + f"{days}D {hours}H {minutes}M {seconds}S",
                color = 0x00FF00
            )
        else:
            embed_var = discord.Embed(
                title = f"{member.name} is not timed out",
                color = 0x00FF00
            )
        await ctx.send(embed=embed_var)
    
    @timein.error
    async def timein_error(self, ctx: Context, error):
        embed_desc = None
        if isinstance(error, commands.CheckFailure):
            embed_desc = NO_PERM_MSG
        elif isinstance(error, commands.MissingRequiredArgument):
            embed_desc = f"Usage: `{self.bot.command_prefix}timein <member>`"
        elif isinstance(error, commands.MemberNotFound):
            embed_desc = BAD_MEMBER_MSG

        if embed_desc != None:
            embed_var = discord.Embed(
                title = ERROR_TITLE,
                description = embed_desc,
                color = 0xC80000
            )
            await ctx.send(embed=embed_var)
        else:
            await ctx.send(str(error))

async def setup(bot: commands.Bot):
    await bot.add_cog(Moderator(bot))