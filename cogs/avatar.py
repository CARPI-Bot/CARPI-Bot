from discord.ext import commands
from globals import *
from decimal import Decimal

class Avatar(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Gets the avatar of any user", aliases=["tst"])
    async def avatar(self, ctx, *userID:str):

        if len(userID) == 0:
            await ctx.send(str(ctx.author.display_avatar) )
        elif len(userID[0]) == 21:
            await ctx.send(str(ctx.guild.get_member(int( userID[0][2:len(userID) - 2] ) ).display_avatar ) )
        else:
            await ctx.send('Invalid command sent.')
    
    @avatar.error
    async def avatar_error(self, ctx, error):
        # Should never run. If this runs then bruh
        if isinstance(error, commands.BadArgument):
            await ctx.send("Something went wrong.")

async def setup(bot):
    await bot.add_cog(Avatar(bot))