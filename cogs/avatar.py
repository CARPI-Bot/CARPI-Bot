import discord
from discord.ext import commands
from globals import *

class Avatar(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Gets the avatar of any user")
    async def avatar(self, ctx, member:discord.Member=None):
        if (member == None):
            await ctx.send(ctx.author.display_avatar)
        else:
            await ctx.send(member.display_avatar)
    
    @avatar.error
    async def avatar_error(self, ctx, error):
        # Should never run. If this runs then bruh
        if isinstance(error, commands.BadArgument):
            await ctx.send("Something went wrong.")
        if isinstance(error, commands.MemberNotFound):
            await ctx.send("Invalid member.")

async def setup(bot):
    await bot.add_cog(Avatar(bot))