import discord
from discord.ext import commands
from globals import *
import random
import datetime

class Miscellaneous(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    ### PING ###
    @commands.hybrid_command(description="Gets the latency of the server")
    async def ping(self, ctx):
        # Retrieves the server latency in milliseconds
        embedVar = discord.Embed(
            title="Pong!",
            description=f"Your message was recieved in {round(self.bot.latency * 1000)}ms.",
            color=0x00C500,
            timestamp=datetime.datetime.now()
        )
        if ctx.author.nick != None: invoker_name = ctx.author.nick
        else: invoker_name = ctx.author.name
        embedVar.set_footer(text=f"\u200bPing checked by {invoker_name}")
        await ctx.send(embed=embedVar)
    
    @ping.error
    async def ping_error(self, ctx):
        await sendDefaultError(ctx)
    
    ### AVATAR ###
    @commands.hybrid_command(description="Gets the avatar of any user")
    async def avatar(self, ctx, member:discord.Member=None):
        if (member == None):
            await ctx.send(ctx.author.display_avatar)
        else:
            await ctx.send(member.display_avatar)
    
    @avatar.error
    async def avatar_error(self, ctx, error):
        # Should never run. If this runs then bruh
        if isinstance(error, commands.MemberNotFound):
            embed_var = discord.Embed(
                title=ERROR_TITLE,
                description="Member not found. Nicknames and usernames are case sensitive, or maybe you spelled it wrong?",
                color=0xC80000
            )
            await ctx.send(embed=embed_var)
        else:
            await sendDefaultError(ctx)
    
    ### BANNER ###
    @commands.hybrid_command(description="Get the banner of any user!")
    async def banner(self, ctx:Context, member:discord.Member=None):
        target_user = (await self.bot.fetch_user(member.id)) if member != None \
                       else (await self.bot.fetch_user(ctx.author.id))
        banner_url = target_user.banner.url if target_user.banner != None else None
        target_color = target_user.accent_color
        embed_var = discord.Embed(
            title="This user doesn't have a banner set!" if banner_url == None else None,
            color=target_color
        )
        if banner_url != None: embed_var.set_image(url=banner_url)
        await ctx.send(embed=embed_var)
    
    @banner.error
    async def banner_error(self, ctx, error):
        if isinstance(error, commands.MemberNotFound):
            embed_var = discord.Embed(
                title=ERROR_TITLE,
                description=BAD_MEMBER_MSG,
                color=0xC80000
            )
            await ctx.send(embed=embed_var)
        else:
            await sendDefaultError(ctx)

    ### COINFLIP ###
    @commands.hybrid_command(description="Flips a coin. Can either be heads or tails.", aliases=["flip", "coin"])
    async def coinflip(self, ctx):
        # Calls a random float between 0 and 0.99 inclusive. Returns heads if 0 - 0.48 and tails if 0.49 - 0.99
        result = "Heads!" if random.randint(0, 1) == 0 else "Tails!"
        embedVar = discord.Embed(
            title=result,
            color=0x00C500,
            timestamp=datetime.datetime.now()
        )
        if ctx.author.nick != None: invoker_name = ctx.author.nick
        else: invoker_name = ctx.author.name
        embedVar.set_footer(text=f"\u200bCoin flipped by {invoker_name}")
        await ctx.send(embed=embedVar)
    
    @coinflip.error
    async def coinflip_error(self, ctx):
        # Should never run. If this runs then bruh
        await sendDefaultError(ctx)

    ### REPO ###
    @commands.hybrid_command(description="Returns a message that can be interacted with (clicked on) bringing a user to our GitHub Repo.")
    async def repo(self, ctx):
        embedVar = discord.Embed(
            title=f"Click Here to Redirect to the {ctx.guild.get_member(1067560443444478034).name} Repository",
            url='https://github.com/Zen1124/tsdb',
            color=0x0099FF,
            timestamp=datetime.datetime.now()
        )
        if ctx.author.nick != None: invoker_name = ctx.author.nick
        else: invoker_name = ctx.author.name
        embedVar.set_footer(text=f"\u200bRepository link requested by {invoker_name}")
        await ctx.send(embed=embedVar)
    
    @repo.error
    async def repo_error(self, ctx):
        # Should never run. If this runs then bruh
        await sendDefaultError(ctx)
    
    ### INVITE ###
    @commands.hybrid_command(description="Sends a link that can be used to invite CARPI to a server, or invite a user to a channel.")
    async def invite(self, ctx, *, args:str=""):

        if ctx.author.nick != None: invoker_name = ctx.author.nick
        else: invoker_name = ctx.author.name

        if len(args) < 0 or len(args) > 1:
            raise commands.BadArgument
        elif len(args) == 0:
            embedVar = discord.Embed(
                title=f"Click Here To Add {ctx.guild.get_member(1067560443444478034).name} To a Server",
                url="https://discord.com/api/oauth2/authorize?client_id=1067560443444478034&permissions=8&scope=bot",
                color=0x0099FF,
                timestamp=datetime.datetime.now()
            )
            embedVar.set_footer(text=f"\u200bBot invite link requested by {invoker_name}")
            await ctx.send(embed= embedVar)
        else:
            if args[0] != "vc" and args[0] != "here":
                raise commands.BadArgument
            elif args[0] == "vc":
                if ctx.author.voice == None:
                    embedVar = discord.Embed(
                        title="Voice Channel Invite Failed",
                        description="You must be in a voice channel to get a valid invite link.",
                        color=0xC80000,
                        timestamp=datetime.datetime.now()
                    )
                    embedVar.set_footer(text=f"\u200bVoice chat invite requested by {invoker_name}")
                    await ctx.send(embed= embedVar)
                else:
                    await ctx.send(await ctx.author.voice.channel.create_invite(max_age = 300) )
            else:
                await ctx.send(await ctx.channel.create_invite(max_age = 300) )
    
    @invite.error
    async def invite_error(self, ctx, error):
        # Should never run. If this runs then bruh
        if isinstance(error, commands.BadArgument):
            embed_var = discord.Embed(
                title=ERROR_TITLE,
                description=f"Usage: `{COMMAND_PREFIX}invite [optional \"vc\"]`",
                color=0xC80000
            )
            await ctx.send(embed=embed_var)
        else:
            sendDefaultError(ctx)

    @commands.hybrid_command(description="Returns a google drive of free textbooks")
    async def textbooks(self, ctx: commands.Context):
        DRIVE_LINK = "https://drive.google.com/drive/folders/1SaiXHIu8-ue2CwCw62ukl0U59KBc26dz"

        embed = discord.Embed(
            title="Textbooks",
            description=f"Here is a google drive link of freely avaliable textbooks.\n*Please note that these may or may not be current.*",
            url=DRIVE_LINK,
            color=ctx.author.accent_color,
            timestamp=datetime.datetime.now()
        )

        await ctx.send(embed=embed)
    
async def setup(bot):
    await bot.add_cog(Miscellaneous(bot))