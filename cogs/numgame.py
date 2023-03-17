from discord.ext import commands
from globals import *
from decimal import Decimal
import discord
import datetime
import random

class NumGame(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Plays a game of 'pick number between [X] and [Y]'.", aliases=["n"])
    async def numgame(self, ctx, *args:str):

        await ctx.send(NUMGAME_INTEGER)

        if len(args) == 0:
            embedVar = discord.Embed(title="Command Usage", description="'{}numgame new <X> <Y>' creates a new game with X and Y as range boundaries\n'{}numgame <guess>' is used to take a guess.".format(COMMAND_PREFIX, COMMAND_PREFIX),  color=0xC80000, timestamp=datetime.datetime.now())
            embedVar.set_footer(text='\u200bNumGame Command Usage provided to ' + str(ctx.author.nick))
            await ctx.send(embed= embedVar)
        elif len(args) == 1:
            if args[0].isdigit():
                if int(args[0]) > NUMGAME_INTEGER:
                    embedVar = discord.Embed(title="Too **High**", description="You entered {}, but that's a bit too high. Try lower...".format(args[0]),  color=0xEFEF00, timestamp=datetime.datetime.now())
                    embedVar.set_footer(text='\u200bNumGame Round Played by ' + str(ctx.author.nick))
                    await ctx.send(embed= embedVar)
                elif int(args[0]) < NUMGAME_INTEGER:
                    embedVar = discord.Embed(title="Too **Low**", description="You entered {}, but that's a bit too low. Try higher...".format(args[0]),  color=0xEFEF00, timestamp=datetime.datetime.now())
                    embedVar.set_footer(text='\u200bNumGame Round Played by ' + str(ctx.author.nick))
                    await ctx.send(embed= embedVar)
                else:
                    embedVar = discord.Embed(title="Number Guessed!", description="You got it! The number was {} -- well done!\nA new number between 0 and 100 has been generated if you would like to keep going".format(args[0]),  color=0x00C500, timestamp=datetime.datetime.now())
                    embedVar.set_footer(text='\u200bNumber guessed by ' + str(ctx.author.nick))
                    await ctx.send(embed= embedVar)
                    NUMGAME_INTEGER = random.randInt(1, 100)
        elif len(args) == 3:
            if args[1].lower() == 'new' and args[2].isdigit() and args[3].isdigit():
                if int(args[2]) >= int(args[3]) or int(args[2]) != abs(int(args[2])) or int(args[3]) != abs(int(args[2])):
                    embedVar = discord.Embed(title="Invalid NumGame Parameters", description="Something wasn't inputted correctly. Make sure the first number is smaller than the second, and that neither number is negative.".format(args[0]),  color=0xC80000, timestamp=datetime.datetime.now())
                    embedVar.set_footer(text='\u200bFailed NumGame Reset by ' + str(ctx.author.nick))
                    await ctx.send(embed= embedVar)
                else:
                    embedVar = discord.Embed(title="Game Reset!", description="A new number has been chosen between {} and {}.\nGood luck!".format(args[2], args[3]),  color=0x00C500, timestamp=datetime.datetime.now())
                    embedVar.set_footer(text='\u200bNumGame Reset by ' + str(ctx.author.nick))
                    await ctx.send(embed= embedVar)
                    NUMGAME_INTEGER = random.randInt(int(args[2]) + 1, args[3])
            else:
                pass
    @numgame.error
    async def numgame_error(self, ctx, *args:str, error):
        # Should never run. If this runs then bruh
        if isinstance(error, commands.BadArgument):
            await ctx.send("Something went wrong.")
        else:
            await ctx.send(str(error) )

async def setup(bot):
    await bot.add_cog(NumGame(bot))