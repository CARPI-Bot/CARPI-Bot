import discord
from discord.ext import commands
import datetime as dt
import random
from globals import *

Context = commands.Context

class Miscellaneous(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    ### PING ###
    @commands.hybrid_command(description="Pong!")
    async def ping(self, ctx:Context):
        # Gets the bot to server latency in milliseconds
        embedVar = discord.Embed(
            title = "Pong!",
            description = f"Your message was received in {int(self.bot.latency * 1000)}ms.",
            color = 0x00C500
        )
        await ctx.send(embed=embedVar)
    
    @ping.error
    async def ping_error(self, ctx:Context, error):
        await sendUnknownError(ctx, error)
    
    ### AVATAR ###
    @commands.hybrid_command(description="Get the avatar of any user.")
    async def avatar(self, ctx:Context, member:discord.Member=None):
        # Avatar and color information is only accessible using fetch_user()
        target_user = (await self.bot.fetch_user(member.id if member != None else ctx.author.id))
        avatar_url = target_user.avatar.url
        target_color = target_user.accent_color
        embed_var = discord.Embed(color=target_color)
        embed_var.set_image(url=avatar_url)
        await ctx.send(embed=embed_var)
    
    @avatar.error
    async def avatar_error(self, ctx:Context, error):
        if isinstance(error, commands.MemberNotFound):
            embed_var = discord.Embed(
                title = ERROR_TITLE,
                description = BAD_MEMBER_MSG,
                color = 0xC80000
            )
            await ctx.send(embed=embed_var)
        else:
            await sendUnknownError(ctx, error)
    
    ### BANNER ###
    @commands.hybrid_command(description="Get the banner of any user.")
    async def banner(self, ctx:Context, member:discord.Member=None):
        # Banner and color information is only accessible using fetch_user()
        target_user = (await self.bot.fetch_user(member.id if member != None else ctx.author.id))
        banner_url = target_user.banner.url if target_user.banner != None else None
        target_color = target_user.accent_color
        embed_var = discord.Embed()
        if banner_url != None:
            embed_var.color = target_color
            embed_var.set_image(url=banner_url)
        else:
            embed_var.title = "This user doesn't have a banner set!"
        await ctx.send(embed=embed_var)
    
    @banner.error
    async def banner_error(self, ctx:Context, error):
        if isinstance(error, commands.MemberNotFound):
            embed_var = discord.Embed(
                title = ERROR_TITLE,
                description = BAD_MEMBER_MSG,
                color = 0xC80000
            )
            await ctx.send(embed=embed_var)
        else:
            await sendUnknownError(ctx, error)

    ### COINFLIP ###
    @commands.hybrid_command(description="Flip a coin!", aliases=["flip", "coin"])
    async def coinflip(self, ctx:Context):
        result = "Heads!" if random.randint(0, 1) == 0 else "Tails!"
        embedVar = discord.Embed(
            title = result,
            description = f"This had a 50% chance of happening.",
            color = 0x00C500
        )
        await ctx.send(embed=embedVar)
    
    @coinflip.error
    async def coinflip_error(self, ctx:Context, error):
        await sendUnknownError(ctx, error)

    ### REPO ###
    @commands.hybrid_command(description="Check out our repository!", aliases=["repository"])
    async def repo(self, ctx:Context):
        embedVar = discord.Embed(
            title = f"Click Here to Redirect to the {self.bot.user.name} Repository!",
            url = "https://github.com/SameriteRL/CARPI-Bot",
            description = "This is a project within the Rensselaer Center for Open Source (RCOS)",
            color = 0x0099FF
        )
        await ctx.send(embed=embedVar)
    
    @repo.error
    async def repo_error(self, ctx:Context, error):
        await sendUnknownError(ctx, error)

    ### TEXTBOOKS ###
    @commands.hybrid_command(description="Shhh...")
    async def textbooks(self, ctx:commands.Context):
        DRIVE_LINK = "https://drive.google.com/drive/folders/1SaiXHIu8-ue2CwCw62ukl0U59KBc26dz"
        embed = discord.Embed(
            title = "Textbooks",
            description = f"Here is a google drive link of freely avaliable textbooks.\n*Please note that these may or may not be current.*",
            url = DRIVE_LINK,
            color = ctx.author.accent_color,
            timestamp = dt.datetime.now()
        )
        await ctx.send(embed=embed)
    
async def setup(bot:commands.Bot):
    await bot.add_cog(Miscellaneous(bot))