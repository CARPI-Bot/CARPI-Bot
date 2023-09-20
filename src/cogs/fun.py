from discord.ext import commands
from globals import *
import random
import discord
import datetime

class Fun(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    ### HELLO ###
    @commands.command(description='Pings sender', aliases=["hi","hey"])
    async def hello(self, ctx):
        await ctx.send(f"Hello {ctx.author.mention}!")

    ### STINKY ###
    @commands.command(description='Pings random member and calls them stinky')
    async def stinky(self, ctx):
        #Get random position of memberlist
        stinky = random.choice(ctx.guild.members)
        await ctx.send(f"{stinky.mention} is stinky!")
    
    ### ROCK PAPER SCISSORS ### 
    @commands.command(description = "Play rock paper scissors against a bot")
    async def rps(self, ctx, msg):
        listy = ["rock", "paper", "scissors"]
        msg = msg.lower()
        WL = "are cute"
        botarg = random.choice(listy) 
        await ctx.send(botarg)
        if(msg == botarg):
            WL = "Tied"
        elif(msg == "rock" and botarg == "paper"):
            WL = "Lose"
        elif(msg == "paper" and botarg == "rock"):
            WL = "Win"
        elif(msg == "scissors" and botarg == "paper"):
            WL = "Win"
        elif(msg == "scissors" and botarg == "rock"):
            WL = "Lose"
        elif(msg == "paper" and botarg == "scissors"):
            WL = "Lose"
        elif(msg == "rock" and botarg == "scissors"):
            WL = "Win"
        else:
            WL = "suck"
        await ctx.send(f"You {WL}!")
    
    ### POLL ###
    @commands.command(description = 'poll "<question>" <choice 1> <choice 2> ... <choice 10>')
    async def poll(self, ctx, question, *choices):
        emojis = ["1️⃣", "2⃣", "3⃣", "4⃣", "5⃣",
                   "6⃣", "7⃣", "8⃣", "9⃣", "🔟"]
        if len(choices) > 10:
            await ctx.send("You can only have 10 options!")
            return

        embed = discord.Embed(
            title = "Poll",
            description = question,
            colour = ctx.author.colour,
            timestamp = datetime.datetime.utcnow()
        )

        options = "\n\n".join(["{}\t{}".format(emojis[i], choice) for i, choice in enumerate(choices)])

        embed.add_field(name = "Options: \n", value = options, inline = False)
        embed.set_footer(text="React to this message to vote!")

        msg = await ctx.send(embed=embed)
        for reaction in emojis[:len(choices)]:
            await msg.add_reaction(reaction)

    #Error handling not firing
    @poll.error
    async def poll_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Put arguments in quotes")
            await ctx.send("Command usage: [Title] [Option 1] [Option 2]")
    
    ### ROLL ONE DICE ### 
    @commands.command(description= "rolls a dice and sends the result")
    async def roll(self, ctx, n=6):
        # Sends the result of a single n-sided dice roll.
        if type(n) != int:
            await ctx.send("Please give an integer!")
            return

        # Initializes a list of values from 1 to 6 and randomly sends a single value
        outcomes = [i + 1 for i in range(n)]
        result = random.choice(outcomes)

        await ctx.send("You rolled a {:d}.".format(result))

    ### NROLL(ROLL MULTIPLE DICE) ###
    @commands.command(description = "nroll <number of dice> <number of sides on a die>")
    async def nroll(self, ctx, *args):
        # Sends the result of multiple n-sided dice rolls.
        if len(args) > 2:
            await ctx.send("Proper command: -nroll <number of dice> <number of sides on each dice>")
            return
        
        #checking that they use only numbers
        for arg in args:
            if not arg.isdigit():
                await ctx.send("Please only use numbers!")
                return

        dice = 2 if len(args) == 0 else int(args[0])
        sides = 6 if len(args) == 1 else int(args[1])

        #putting rolls into a list then outputting
        outcomes = [i + 1 for i in range(sides)]
        results = []
        for i in range(dice):
            results.append(random.choice(outcomes))
        await ctx.send("Here are the rolls in order: {}".format(results))

async def setup(bot):
    await bot.add_cog(Fun(bot))
