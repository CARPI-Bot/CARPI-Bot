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
        global NUMGAME_TARGET
        global NUMGAME_UPPERBOUND
        global NUMGAME_LOWERBOUND
        global NUMGAME_GUESSCOUNT

        if len(args) == 0:
            embedVar = discord.Embed(title="Command Usage", description="'{}numgame new <X> <Y>' creates a new game with X and Y as range boundaries\n'{}numgame <guess>' is used to take a guess.".format(COMMAND_PREFIX, COMMAND_PREFIX),  color=0xC80000, timestamp=datetime.datetime.now())
            embedVar.set_footer(text='\u200bNumGame Command Usage provided to ' + str(ctx.author.nick))
            await ctx.send(embed= embedVar)
        elif len(args) == 1:
            if args[0].isdigit():
                NUMGAME_GUESSCOUNT += 1
                if NUMGAME_TARGET == -1:
                    embedVar = discord.Embed(title="Game Not Started", description="You haven't started a number game yet.\nTry '{}numgame new <X> <Y>' creates a new game with X and Y as range boundaries".format(COMMAND_PREFIX),  color=0xEFEF00, timestamp=datetime.datetime.now())
                    embedVar.set_footer(text='\u200bNumGame Command Sent by ' + str(ctx.author.nick))
                    await ctx.send(embed= embedVar)
                elif int(args[0]) > NUMGAME_TARGET:
                    embedVar = discord.Embed(title="Too **High**", description="You entered {}, but that's a bit too high. Try lower...".format(args[0]),  color=0xEFEF00, timestamp=datetime.datetime.now())
                    embedVar.set_footer(text='\u200bNumGame Round Played by ' + str(ctx.author.nick))
                    await ctx.send(embed= embedVar)
                elif int(args[0]) < NUMGAME_TARGET:
                    embedVar = discord.Embed(title="Too **Low**", description="You entered {}, but that's a bit too low. Try higher...".format(args[0]),  color=0xEFEF00, timestamp=datetime.datetime.now())
                    embedVar.set_footer(text='\u200bNumGame Round Played by ' + str(ctx.author.nick))
                    await ctx.send(embed= embedVar)
                else:
                    embedVar = discord.Embed(title="Number Guessed!", description="You got it! The number was {} and you got it in {} guesses -- well done!\nA new number between {} and {} has been generated if you would like to try again.".format(args[0], NUMGAME_GUESSCOUNT, NUMGAME_LOWERBOUND, NUMGAME_UPPERBOUND),  color=0x00C500, timestamp=datetime.datetime.now())
                    embedVar.set_footer(text='\u200bNumber guessed by ' + str(ctx.author.nick))
                    await ctx.send(embed= embedVar)
                    NUMGAME_TARGET = random.randint(NUMGAME_LOWERBOUND + 1, NUMGAME_UPPERBOUND)
                    NUMGAME_GUESSCOUNT = 0
            else:
                embedVar = discord.Embed(title="Invalid Command", description="Looks like you tried using the numgame command.\nTry '{}numgame' for command options.".format(COMMAND_PREFIX),  color=0xC80000, timestamp=datetime.datetime.now())
                embedVar.set_footer(text='\u200bNumGame Command Used by ' + str(ctx.author.nick))
                await ctx.send(embed= embedVar)
        elif len(args) == 3:
            if args[0].lower() == 'new' and args[1].isdigit() and args[2].isdigit():
                if int(args[1]) >= int(args[2]) or int(args[1]) != abs(int(args[1])) or int(args[2]) != abs(int(args[2])):
                    embedVar = discord.Embed(title="Invalid NumGame Parameters", description="Something wasn't inputted correctly. Make sure the first number is smaller than the second, and that neither number is negative.",  color=0xC80000, timestamp=datetime.datetime.now())
                    embedVar.set_footer(text='\u200bFailed NumGame Reset by ' + str(ctx.author.nick))
                    await ctx.send(embed= embedVar)
                else:
                    embedVar = discord.Embed(title="Game Reset!", description="A new number has been chosen between {} and {}.\nGood luck!".format(args[1], args[2]),  color=0x00C500, timestamp=datetime.datetime.now())
                    embedVar.set_footer(text='\u200bNumGame Reset by ' + str(ctx.author.nick))
                    await ctx.send(embed= embedVar)
                    NUMGAME_TARGET = random.randint(int(args[1]) + 1, int(args[2]) )
                    NUMGAME_LOWERBOUND = int(args[1])
                    NUMGAME_UPPERBOUND = int(args[2])
                    NUMGAME_GUESSCOUNT = 0
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