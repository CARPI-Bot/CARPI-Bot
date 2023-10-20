import discord
from discord.ext import commands
import datetime as dt
from datetime import timezone
from globals import *

Context = commands.Context

class Moderator(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    ### SHUTDOWN ###
    @commands.command(aliases=["kill"], hidden=True)
    @commands.check(commands.is_owner())
    async def shutdown(self, ctx:Context):
        # Creates a response embed
        embed_var = discord.Embed(
            title="Shutting down...",
            color=0xC80000
        )
        # Sends the embed and closes the bot
        await ctx.send(embed=embed_var)
        await self.bot.close()
    
    @shutdown.error
    async def shutdown_error(self, ctx:Context, error):
        if isinstance(error, commands.CheckFailure):
            embed_var = discord.Embed(
                title=ERROR_TITLE,
                description=NO_PERM_MSG,
                color=0xC80000
            )
            await ctx.send(embed=embed_var)
        else:
            await sendUnknownError(ctx, error)
    
    ### CLEAR ###
    @commands.command(aliases=["purge"], hidden=True)
    @commands.check_any(commands.has_permissions(manage_messages=True), commands.is_owner())
    async def clear(self, ctx:Context, num:int):
        # Creates a response embed and clears messages
        if num < 1:
            embed_title = "Enter a number greater than or equal to 1."
        else:
            try:
                num_deleted = len(await ctx.channel.purge(limit=num+1)) - 1
                embed_title = f"{num_deleted} messages deleted."
            except:
                raise
        embed_var = discord.Embed(
            title=embed_title,
            color=0x00FF00
        )
        # Embed automatically deletes itself after a delay
        await ctx.send(embed=embed_var, delete_after=DEL_DELAY)

    @clear.error
    async def clear_error(self, ctx:Context, error):
        embed_desc = None
        if isinstance(error, commands.CheckFailure):
            embed_desc = NO_PERM_MSG
        elif isinstance(error, commands.MissingRequiredArgument):
            embed_desc = f"Usage: `{COMMAND_PREFIX}clear [number of messages]`"
        elif isinstance(error, commands.BadArgument):
            embed_desc = "Enter a valid integer."

        if embed_desc != None:
            embed_var = discord.Embed(
                title=ERROR_TITLE,
                description=embed_desc,
                color=0xC80000
            )
            await ctx.send(embed=embed_var)
        else:
            await sendUnknownError(ctx, error)

    ### TIMEOUT ###
    @commands.hybrid_command(description="Time out a user for a specified amount of time.",
                             aliases=["mute", "silence"], hidden=True)
    @commands.check_any(commands.has_permissions(moderate_members=True), commands.is_owner())
    async def timeout(self, ctx:Context, member:discord.Member, *, time:str=""):
        # Guards against an empty argument
        if len(time) == 0:
            raise commands.MissingRequiredArgument
        time = time.strip().split()
        days, hours, minutes, seconds = 0, 0, 0, 0
        for element in time:
            try:
                int(element[:-1])
            except:
                raise commands.BadArgument
            else:
                if element.lower().endswith("d"): days += int(element[:-1])
                elif element.lower().endswith("h"): hours += int(element[:-1])
                elif element.lower().endswith("m"): minutes += int(element[:-1])
                elif element.lower().endswith("s"): seconds += int(element[:-1])
                else: raise commands.BadArgument
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
        # Checks that the user is not already timed out
        if member.is_timed_out():
            error_desc = "This user is already timed out."
        # Maximum possible timeout is 28 days (2,419,200 seconds)
        elif days * 86400 + hours * 3600 + minutes * 60 + seconds > 2419200:
            error_desc = "The maximum possible timeout duration is 28 days."
        # Outputs an error if either of the above conditions are true
        if error_desc != None:
            embed_var = discord.Embed(
                title=ERROR_TITLE,
                description=error_desc,
                color=0xC80000
            )
            await ctx.send(embed=embed_var)
            return
        # Executes timeout
        await member.timeout(dt.timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds))
        embed_var = discord.Embed(
            title=f"{member.name} has been timed out.",
            description=f"Duration: {days}D {hours}H {minutes}M {seconds}S",
            color=0xC80000
        )
        await ctx.send(embed=embed_var)
    
    @timeout.error
    async def timeout_error(self, ctx:Context, error):
        embed_desc = None
        if isinstance(error, commands.CheckFailure):
            embed_desc = NO_PERM_MSG
        elif isinstance(error, commands.MemberNotFound):
            embed_desc = BAD_MEMBER_MSG
        elif isinstance(error, commands.BadArgument) or isinstance(error, commands.MissingRequiredArgument):
            embed_desc = f"Usage: `{COMMAND_PREFIX}timeout <member> <days>d <hours>h <minutes>m <seconds>s`\n \
                           At least one time argument is required."

        if embed_desc != None:
            embed_var = discord.Embed(
                title=ERROR_TITLE,
                description=embed_desc,
                color=0xC80000
            )
            await ctx.send(embed=embed_var)
        else:
            await sendUnknownError(ctx, error)

    ### TIMEIN ###
    @commands.hybrid_command(description="Remove timeout from a user.", aliases=["untimeout"], hidden=True)
    @commands.check_any(commands.has_permissions(moderate_members=True), commands.is_owner())
    async def timein(self, ctx:Context, member:discord.Member):
        if member.is_timed_out():
            remaining_seconds = (member.timed_out_until - dt.datetime.now(timezone.utc)).seconds
            days, hours, minutes, seconds = 0, 0, 0, remaining_seconds
            # Organizes the total seconds into different time components
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
                title=f"Removed timeout from {member.name}.",
                description=f"Remaining duration: {days}D {hours}H {minutes}M {seconds}S",
                color=0x00FF00
            )
        else:
            embed_var = discord.Embed(title=f"{member.name} is not timed out.", color=0x00FF00)
        await ctx.send(embed=embed_var)
    
    @timein.error
    async def timein_error(self, ctx:Context, error):
        embed_desc = None
        if isinstance(error, commands.CheckFailure):
            embed_desc = NO_PERM_MSG
        elif isinstance(error, commands.MissingRequiredArgument):
            embed_desc = f"Usage: `{COMMAND_PREFIX}timein <member>`"
        elif isinstance(error, commands.MemberNotFound):
            embed_desc = "Member not found. Nicknames and usernames are case sensitive, or maybe you spelled it wrong?"

        if embed_desc != None:
            embed_var = discord.Embed(
                title=ERROR_TITLE,
                description=embed_desc,
                color=0xC80000
            )
            await ctx.send(embed=embed_var)
        else:
            await ctx.send(str(error))

async def setup(bot:commands.Bot):
    await bot.add_cog(Moderator(bot))