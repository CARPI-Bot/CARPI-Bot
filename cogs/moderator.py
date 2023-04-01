import datetime as dt
import discord
from discord.ext import commands
from globals import *

class Moderator(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    ### SHUTDOWN ###
    @commands.command(description="Turns the bot offline.", aliases=["kill"], hidden=True)
    @commands.check(commands.is_owner())
    async def shutdown(self, ctx):
        # Creates a response embed
        embed_var = discord.Embed(title="Shutting down...",
                                  color=0xC80000, timestamp=dt.datetime.now())
        if ctx.author.nick != None:
            invoker_name = ctx.author.nick
        else:
            invoker_name = ctx.author.name
        embed_var.set_footer(text=f"\u200bCommand initiated by {invoker_name}")
        # Sends the embed and closes the bot
        await ctx.send(embed=embed_var)
        await self.bot.close()
    
    @shutdown.error
    async def shutdown_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            embed_var = discord.Embed(title=ERROR_TITLE,
                                      description=NO_PERM_MSG,
                                      color=0xC80000)
            await ctx.send(embed=embed_var)
        # This should never run, if it does then bruh
        else:
            await sendDefaultError(ctx)
    
    ### CLEAR ###
    @commands.command(description="Deletes the last x number of messages in the channel.",
                      aliases=["purge"], hidden=True)
    @commands.check_any(commands.has_permissions(manage_messages=True), commands.is_owner())
    async def clear(self, ctx, num:int):
        if num < 1:
            embed_title = "Enter a number greater than or equal to 1."
        elif num == 1:
            embed_title = "Message deleted."
            await ctx.channel.purge(limit=num+1)
        else:
            embed_title = f"{num} messages deleted."
            await ctx.channel.purge(limit=num+1)

        embed_var = discord.Embed(title=embed_title, color=0x00FF00)
        await ctx.send(embed=embed_var, delete_after=DEL_DELAY)

    @clear.error
    async def clear_error(self, ctx, error):
        embed_desc = None
        if isinstance(error, commands.CheckFailure):
            embed_desc = NO_PERM_MSG
        elif isinstance(error, commands.MissingRequiredArgument):
            embed_desc = f"Usage: `{COMMAND_PREFIX}clear [number of messages]`"
        elif isinstance(error, commands.BadArgument):
            embed_desc = "Enter a valid integer."

        if embed_desc != None:
            embed_var = discord.Embed(title=ERROR_TITLE,
                                      description=embed_desc,
                                      color=0xC80000)
            await ctx.send(embed=embed_var)
        else:
            await sendDefaultError(ctx)

    ### TIMEOUT ###
    @commands.hybrid_command(description="Times out a user for a specified amount of time.",
                             aliases=["mute", "silence"], hidden=True)
    @commands.check_any(commands.has_permissions(moderate_members=True), commands.is_owner())
    async def timeout(self, ctx, member:discord.Member, *, time:str=""):

        # Guards against an empty argument
        if len(time) == 0:
            raise commands.BadArgument

        time = time.strip().split()
        days = 0; hours = 0; minutes = 0; seconds = 0

        for element in time:
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
            embed_var = discord.Embed(title=ERROR_TITLE,
                                      description=error_desc,
                                      color=0xC80000)
            await ctx.send(embed=embed_var)
            return
        
        # Executes timeout
        await member.timeout(dt.timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds))
        embed_var = discord.Embed(title=f"{member.name} has been timed out.",
                                  description=f"Duration: {days}D {hours}H {minutes}M {seconds}S",
                                  color=0xC80000)
        await ctx.send(embed=embed_var)
    
    @timeout.error
    async def timeout_error(self, ctx, error):
        embed_desc = None
        if isinstance(error, commands.CheckFailure):
            embed_desc = NO_PERM_MSG
        elif isinstance(error, commands.BadArgument) or isinstance(error, commands.MissingRequiredArgument):
            embed_desc = f"Usage: `{COMMAND_PREFIX}timeout <member> <days>d <hours>h <minutes>m <seconds>s`"

        if embed_desc != None:
            embed_var = discord.Embed(title=ERROR_TITLE,
                                      description=embed_desc,
                                      color=0xC80000)
            await ctx.send(embed=embed_var)
        else:
            await sendDefaultError(ctx)

    ### TIMEIN ###
    # To do: Output remaining timeout duration with confirmation
    @commands.hybrid_command(description="Removes timeout status from a user if they're currently timed out.",
                             aliases=["untimeout"], hidden=True)
    @commands.check_any(commands.has_permissions(moderate_members=True), commands.is_owner())
    async def timein(self, ctx, member:discord.Member):
        if member.is_timed_out():
            embed_title = f"Removed timeout from {member.name}."
            await member.timeout(dt.timedelta(seconds=0))
        else:
            embed_title = f"{member.name} is not timed out."
        
        embed_var = discord.Embed(title=embed_title, color=0x00FF00)
        await ctx.send(embed=embed_var)
    
    @timein.error
    async def timein_error(self, ctx, error):
        embed_desc = None
        if isinstance(error, commands.CheckFailure):
            embed_desc = NO_PERM_MSG
        elif isinstance(error, commands.BadArgument):
            embed_desc = f"Usage: `{COMMAND_PREFIX}timein <member>`"

        if embed_desc != None:
            embed_var = discord.Embed(title=ERROR_TITLE,
                                      description=embed_desc,
                                      color=0xC80000)
            await ctx.send(embed=embed_var)
        else:
            await sendDefaultError(ctx)

async def setup(bot):
    await bot.add_cog(Moderator(bot))