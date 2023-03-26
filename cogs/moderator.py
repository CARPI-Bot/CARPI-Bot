import datetime as dt
import discord
from discord.ext import commands
from globals import *

# For use in error handlers
ERROR_TITLE = "Something went wrong."
NO_PERM_MSG = "You don't have permissions to do that."

class Moderator(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    ### KILL ###
    @commands.command(description="Turns the bot offline.", aliases=["kill"], hidden=True)
    @commands.check(commands.is_owner())
    async def shutdown(self, ctx):
        embed_var = discord.Embed(title="Shutting down...",
                                color=0xC80000, timestamp=dt.datetime.now())
        embed_var.set_footer(text=f"\u200bCommand initiated by {ctx.author.nick}")
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

        embed_var = discord.Embed(title=embed_title, color=0xC80000)
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
    async def timeout(self, ctx, member:discord.Member, *, time:str):
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
        elif isinstance(error, commands.BadArgument):
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
        
        embed_var = discord.Embed(title=embed_title, color=0xC80000)
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

    ### ROLE ###
    # @commands.hybrid_command(description="Assigns or revokes role to/from a user", hidden=True)
    # @commands.check_any(commands.has_permissions(manage_roles=True), commands.is_owner())
    # async def role(self, ctx, *, roles:str):
    #     roles = roles.split()
    #     await ctx.send("ARGS DEBUG: " + roles)
    #     await ctx.send("ROLES DEBUG: " + ctx.guild.roles)

    #     if len(roles) >= 2 and len(roles) <= 3:
    #         if roles[0] == 'add' or roles[0] == 'remove':
    #             if len(roles) == 2:
    #                 return
    #             else:
    #                 # args len 3
    #                 return

    #     embed_var = discord.Embed(title=f"Invalid Command Use",
    #                               description="`{COMMAND_PREFIX}role add <role name>` adds a role to your user account\n \
    #                                          `{COMMAND_PREFIX}role add <role name> <tag>` adds a role to a tagged user's account\n \
    #                                          `{COMMAND_PREFIX}role remove <role name>` removes a role from your user account\n \
    #                                          `{COMMAND_PREFIX}role remove <role name> <tag>` removes a role from a tagged user's account",
    #                               color=0xC80000, timestamp=datetime.datetime.now())
    #     embed_var.set_footer(text=f"\u200bRole command use attempted by {ctx.author.nick}")
    #     await ctx.send(embed=embed_var)

    # @role.error
    # async def role_error(self, ctx, error):
    #     if isinstance(error, commands.BadArgument):
    #         await ctx.send("Something went wrong...")
    #     elif isinstance(error, commands.CommandInvokeError):
    #         error = error.original
    #         if isinstance(error, (discord.errors.HTTPException, discord.HTTPException)):
    #             embed_var = discord.Embed(title="Command Unavailable",
    #                                     description="I don't have the 'Manage Roles'.\n \
    #                                                  If you think this is an issue, ping an admin.",
    #                                     color=0xC80000, timestamp=datetime.datetime.now())
    #             embed_var.set_footer(text=f"\u200bRole command use attempted by {ctx.author.nick}")
    #             await ctx.send(embed=embed_var)
    #     else:
    #         await sendDefaultError(ctx)

async def setup(bot):
    await bot.add_cog(Moderator(bot))