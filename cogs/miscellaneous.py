import discord
from discord.ext import commands
import random
import datetime

class Miscellaneous(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Gets the latentcy of the server")
    async def ping(self, ctx):
        # Retrieves the server latency in MS.
        embedVar = discord.Embed(title="Pong!", description="Your message was recieved in {}ms.".format(str(round(self.bot.latency * 1000) ) ), color=0x00C500, timestamp=datetime.datetime.now())
        embedVar.set_footer(text='\u200bPing checked by ' + str(ctx.author.nick))
        await ctx.send(embed= embedVar)
    
    @ping.error
    async def ping_error(self, ctx, error):
        # Should never run. If this runs then bruh
        if isinstance(error, commands.BadArgument):
            await ctx.send("Something went wrong.")

    @commands.command(description="Flips a coin. Can either be heads or tails.", aliases=["flip", "coin"])
    async def coinflip(self, ctx):
        # Calls a random float between 0 and 0.99 inclusive. Returns heads if 0 - 0.48 and tails if 0.49 - 0.99
        embedVar = discord.Embed(title="Coin Flip Result", description="{}".format("heads" if random.randint(0, 1) == 0 else "tails" ), color=0x00C500, timestamp=datetime.datetime.now())
        embedVar.set_footer(text='\u200bCoin flipped by ' + str(ctx.author.nick))
        await ctx.send(embed= embedVar)
    
    @coinflip.error
    async def coinflip_error(self, ctx, error):
        # Should never run. If this runs then bruh
        if isinstance(error, commands.BadArgument):
            await ctx.send("Something went wrong.")

    @commands.command(description="Returns a message that can be interacted with (clicked on) bringing a user to our GitHub Repo.")
    async def repo(self, ctx):
        embedVar = discord.Embed(title="Click Here to Redirect to the {} Repository".format(ctx.guild.get_member(1067560443444478034).name), url='https://github.com/Zen1124/tsdb', color=0x0099FF, timestamp=datetime.datetime.now())
        embedVar.set_footer(text='\u200bRepository link requested by ' + str(ctx.author.nick))
        await ctx.send(embed= embedVar)
    
    @repo.error
    async def repo_error(self, ctx, error):
        # Should never run. If this runs then bruh
        if isinstance(error, commands.BadArgument):
            await ctx.send("Something went wrong.")

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
    
    @commands.command(description='sus callout')
    async def sus(self, ctx):
        person = random.randint(0, 9)
        await ctx.send(f"{ctx.guild.members[person].mention} is SUS")
        await ctx.guild.member.timeout(datetime.timedelta(0, 0, 1, 0))
        await ctx.send(f"{ctx.guild.members[person].mention} get timed out for 1 min")
    
    @commands.command(description='secret message someone')
    async def callout(self, ctx, members: commands.Greedy[discord.Member], *, msg='personal callout'):
        for x in members:
            if not x.dm_channel == None:
                await x.dm_channel.send(f"Secret message: {msg}")
                await ctx.send("Message sent!")
            else:
                await x.create_dm()
                await x.dm_channel.send(f"Secret message: {msg}")
                await ctx.send("Message sent!")
        await ctx.message.delete()

async def setup(bot):
    await bot.add_cog(Miscellaneous(bot))