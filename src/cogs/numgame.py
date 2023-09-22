import discord
from discord.ext import commands
import datetime
import random
from globals import *

class NumGame(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Plays a game of 'pick number between [X] and [Y]'.", aliases=["n"])
    async def numgame(self, ctx, *args:str):
        global target
        global upper_bound
        global lower_bound
        global guess_count
        if len(args) == 0:
            embedVar = discord.Embed(
                title="Command Usage",
                description=f"'{COMMAND_PREFIX}numgame new <X> <Y>' creates a new game with X and Y as range boundaries\n'{COMMAND_PREFIX}numgame <guess>' is used to take a guess.",
                color=0xC80000,
                timestamp=datetime.datetime.now()
            )
            embedVar.set_footer(text=f"\u200bNumGame Command Usage provided to {ctx.author.name}")
            await ctx.send(embed=embedVar)
        elif len(args) == 1:
            if args[0].isdigit():
                guess_count += 1
                if target == -1:
                    embedVar = discord.Embed(
                        title="Game Not Started",
                        description=f"You haven't started a number game yet.\nTry '{COMMAND_PREFIX}numgame new <X> <Y>' creates a new game with X and Y as range boundaries",
                        color=0xEFEF00,
                        timestamp=datetime.datetime.now()
                    )
                    embedVar.set_footer(text=f'\u200bNumGame Command Sent by {ctx.author.name}')
                    await ctx.send(embed= embedVar)
                elif int(args[0]) > target:
                    embedVar = discord.Embed(
                        title="Too **High**",
                        description=f"You entered {args[0]}, but that's a bit too high. Try lower...",
                        color=0xEFEF00,
                        timestamp=datetime.datetime.now()
                    )
                    embedVar.set_footer(text=f"\u200bNumGame Round Played by {ctx.author.name}")
                    await ctx.send(embed= embedVar)
                elif int(args[0]) < target:
                    embedVar = discord.Embed(
                        title="Too **Low**",
                        description=f"You entered {args[0]}, but that's a bit too low. Try higher...",
                        color=0xEFEF00,
                        timestamp=datetime.datetime.now()
                    )
                    embedVar.set_footer(text=f'\u200bNumGame Round Played by {ctx.author.name}')
                    await ctx.send(embed= embedVar)
                else:
                    embedVar = discord.Embed(
                        title="Number Guessed!",
                        description=f"You got it! The number was {args[0]} and you got it in {guess_count} guesses -- well done!\nA new number between {lower_bound} and {upper_bound} has been generated if you would like to try again.",
                        color=0x00C500,
                        timestamp=datetime.datetime.now()
                    )
                    embedVar.set_footer(text=f"\u200bNumber guessed by {ctx.author.nick}")
                    await ctx.send(embed= embedVar)
                    target = random.randint(lower_bound + 1, upper_bound)
                    guess_count = 0
            else:
                embedVar = discord.Embed(
                    title="Invalid Command",
                    description=f"Looks like you tried using the numgame command.\nTry '{COMMAND_PREFIX}numgame' for command options.",
                    color=0xC80000,
                    timestamp=datetime.datetime.now()
                )
                embedVar.set_footer(text=f"\u200bNumGame Command Used by {ctx.author.nick}")
                await ctx.send(embed= embedVar)
        elif len(args) == 3:
            if args[0].lower() == "new" and args[1].isdigit() and args[2].isdigit():
                if int(args[1]) >= int(args[2]) or int(args[1]) != abs(int(args[1])) or int(args[2]) != abs(int(args[2])):
                    embedVar = discord.Embed(
                        title="Invalid NumGame Parameters",
                        description="Something wasn't inputted correctly. Make sure the first number is smaller than the second, and that neither number is negative.",
                        color=0xC80000,
                        timestamp=datetime.datetime.now()
                    )
                    embedVar.set_footer(text=f"\u200bFailed NumGame Reset by {ctx.author.nick}")
                    await ctx.send(embed= embedVar)
                else:
                    embedVar = discord.Embed(
                        title="Game Reset!",
                        description=f"A new number has been chosen between {args[1]} and {args[2]}.\nGood luck!",
                        color=0x00C500,
                        timestamp=datetime.datetime.now()
                    )
                    embedVar.set_footer(text=f"\u200bNumGame Reset by by {ctx.author.nick}")
                    await ctx.send(embed= embedVar)
                    target = random.randint(int(args[1]) + 1, int(args[2]) )
                    lower_bound = int(args[1])
                    upper_bound = int(args[2])
                    guess_count = 0

    @numgame.error
    async def numgame_error(self, ctx, error):
        # Should never run. If this runs then bruh
        if isinstance(error, commands.BadArgument):
            await ctx.send("Something went wrong.")
        else:
            await sendDefaultError(ctx)

async def setup(bot):
    await bot.add_cog(NumGame(bot))