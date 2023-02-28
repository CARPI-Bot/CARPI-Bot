from discord.ext import commands
from globals import *
import random
import discord

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description='Pings sender', aliases=["hi","hey"])
    async def hello(self, ctx):
        await ctx.send(f"Hello {ctx.author.mention}!")

    @commands.command(description='Pings random member and calls them stinky')
    async def stinky(self, ctx):
        #Get random position of memberlist
        stinky = random.choice(ctx.guild.members)
        await ctx.send(f"{stinky.mention} is stinky!")

    @commands.command(description='Sends an anonymous message to intended user through bot')
    async def secret(self, ctx, members: commands.Greedy[discord.Member], *, msg='so secret'):
        for x in members:
            if not x.dm_channel == None:
                await x.dm_channel.send(f"Secret message: {msg}")
                await ctx.send("Message sent!")
            else:
                await x.create_dm()
                await x.dm_channel.send(f"Secret message: {msg}")
                await ctx.send("Message sent!")
        await ctx.message.delete()
    #Error handling not firing
    @secret.error
    async def secret_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Command usage: [user/users] [message]")
    
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
        
async def setup(bot):
    await bot.add_cog(Fun(bot))
