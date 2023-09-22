from globals import *
from discord.ext import commands
from typing import Optional
from datetime import datetime

'''
Commands:
    /poll (flags: PollFlags)
'''
class Interactive(commands.Cog):
    # Extended discord ui view
    class PollView(discord.ui.View):
        ...

    # Extended discord ui button
    class PollButton(discord.ui.Button):
        ...

    # The parameters for the '/poll' command
    class PollFlags(commands.FlagConverter):
        prompt: str

        response_one: str
        response_two: str

        response_three: Optional[str]
        response_four: Optional[str]
        response_five: Optional[str]

    def __init__(self, bot: discord.Client):
        self.bot: discord.Client = bot

    @commands.hybrid_command(description='Creates a poll within the current channel.', aliases=['survey', 'question'])
    async def poll_new(self, ctx: commands.Context, *, flags: PollFlags):
        embed: discord.Embed = discord.Embed(
            title=flags.prompt,
            color=ctx.author.color,
            timestamp=datetime.now()
        )

        embed.set_footer(text=f'\u200bPoll created by {ctx.author.display_name}')

        view: Interactive.PollView = Interactive.PollView()

        strings: list[str] = [flag[1] for flag in flags if flag[1] and flag[0] != 'prompt']
        for index, string in enumerate(strings):
            poll_button: Interactive.PollButton = Interactive.PollButton(
                label=f'\u200b{string}', 
                style=discord.ButtonStyle.primary,
                row=index
            )

            view.add_item(poll_button)

        await ctx.send(embed=embed, view=view)

async def setup(bot: discord.Client):
    await bot.add_cog(Interactive(bot))
