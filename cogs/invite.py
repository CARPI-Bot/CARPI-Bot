from discord.ext import commands
from globals import *
from decimal import Decimal
import discord
import datetime

class Invite(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Sends a link that can be used to invite CARPI to a server, or invite a user to a channel.")
    async def invite(self, ctx, *args:str):
        # embedVar = discord.Embed(title="Click Here to Redirect to the {} Repository".format(ctx.guild.get_member(1067560443444478034).name), url='https://github.com/Zen1124/tsdb', color=0x0099FF, timestamp=datetime.datetime.now())

        await ctx.send(ctx.author.voice)

        if len(args) == 0:
            embedVar = discord.Embed(title="Click Here To Add {} To a Server".format(ctx.guild.get_member(1067560443444478034).name), url='https://discord.com/api/oauth2/authorize?client_id=1067560443444478034&permissions=8&scope=bot', color=0x0099FF, timestamp=datetime.datetime.now())
            embedVar.set_footer(text='\u200bRepository link requested by ' + str(ctx.author.nick))
            await ctx.send(embed= embedVar)

        elif len(args) == 1:
            if args[0] == 'vc':
                if ctx.author.voice == None:
                    embedVar = discord.Embed(title="Voice Channel Invite Failed", description="You must be in a voice channel to get a valid invite link.", color=0xC80000, timestamp=datetime.datetime.now())
                    embedVar.set_footer(text='\u200bVoice chat invite requested by ' + str(ctx.author.nick))
                    await ctx.send(embed= embedVar)
                else:
                    await ctx.send(await ctx.author.voice.channel.create_invite(max_age = 300) )
            
            elif args[0] == 'here':
                await ctx.send(await ctx.channel.create_invite(max_age = 300) )
    
    @invite.error
    async def invite_error(self, ctx, error):
        # Should never run. If this runs then bruh
        if isinstance(error, commands.BadArgument):
            await ctx.send("Something went wrong.")
        else:
            await ctx.send(str(error))

async def setup(bot):
    await bot.add_cog(Invite(bot))