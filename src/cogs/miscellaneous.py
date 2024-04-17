import random

import discord
from discord.ext import commands
from discord.ext.commands import CommandError, Context

from bot import CARPIBot
from globals import BAD_MEMBER_MSG, ERROR_TITLE, send_generic_error

class Miscellaneous(commands.Cog):
    def __init__(self, bot: CARPIBot):
        self.bot = bot

    async def cog_command_error(self, ctx: Context, error: CommandError) -> None:
        if not ctx.command.has_error_handler():
            await send_generic_error(ctx, error)
    
    ### AVATAR ###
    @commands.hybrid_command(
        description = "Get the avatar of any user."
    )
    async def avatar(self, ctx: Context, member: discord.Member = None):
        # Avatar and color information is only accessible using fetch_user()
        target_user = await self.bot.fetch_user(member.id if member else ctx.author.id)
        avatar_url = target_user.avatar.url if target_user.avatar else None
        embed = discord.Embed()
        if avatar_url:
            embed.set_image(url=avatar_url)
            embed.color = target_user.accent_color
        else:
            embed.title = "This user doesn't have an avatar set!"
            embed.color = discord.Color.blurple()
        await ctx.send(embed=embed)
    
    @avatar.error
    async def avatar_error(self, ctx: Context, error: CommandError):
        if isinstance(error, commands.MemberNotFound):
            embed = discord.Embed(
                title = "Member not found",
                description = BAD_MEMBER_MSG,
                color = discord.Color.red()
            )
            await ctx.send(embed=embed)
        else:
            await send_generic_error(ctx, error)
    
    ### BANNER ###
    @commands.hybrid_command(
        description = "Get the banner of any user."
    )
    async def banner(self, ctx: Context, member: discord.Member = None):
        # Banner and color information is only accessible using fetch_user()
        target_user = await self.bot.fetch_user(member.id if member else ctx.author.id)
        banner_url = target_user.banner.url if target_user.banner else None
        embed = discord.Embed()
        if banner_url:
            embed.set_image(url=banner_url)
            embed.color = target_user.accent_color
        else:
            embed.title = "This user doesn't have a banner set!"
            embed.color = discord.Color.blurple()
        await ctx.send(embed=embed)
    
    @banner.error
    async def banner_error(self, ctx: Context, error: CommandError):
        if isinstance(error, commands.MemberNotFound):
            embed = discord.Embed(
                title = ERROR_TITLE,
                description = BAD_MEMBER_MSG,
                color = discord.Color.red()
            )
            await ctx.send(embed=embed)
        else:
            await send_generic_error(ctx, error)

    ### COINFLIP ###
    @commands.hybrid_command(
        description = "Flip a coin!",
        aliases = ["flip", "coin"]
    )
    async def coinflip(self, ctx: Context):
        result = "Heads!" if random.randint(0, 1) == 0 else "Tails!"
        embedVar = discord.Embed(
            title = result,
            description = "This had a 50% chance of happening.",
            color = discord.Color.green()
        )
        await ctx.send(embed=embedVar)

    ### TEXTBOOKS ###
    @commands.hybrid_command(
        description = "Shhh..."
    )
    async def textbooks(self, ctx: commands.Context):
        drive_link = \
            "https://drive.google.com/drive/folders/1SaiXHIu8-ue2CwCw62ukl0U59KBc26dz"
        embed = discord.Embed(
            title = "Textbook Google Drive",
            description = f"Here is a repository of freely avaliable textbooks. "
                          + "Note that these may or may not be current.",
            url = drive_link,
            color = discord.Color.blurple()
        )
        await ctx.send(embed=embed)
    

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Miscellaneous(bot))