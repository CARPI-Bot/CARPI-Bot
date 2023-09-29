from globals import *
from discord.ext import commands
from typing import Optional
from datetime import datetime, timedelta
from asyncio import sleep

'''
Commands:
    /poll (flags: PollFlags)
'''

# Extended discord ui view
def create_pollview_class(loop_duration, loop_count=1):
    class PollView(discord.ui.View):
        def __init__(self):
            super().__init__()

            self.response_data = {}
            self.buffer = True
       
    return PollView

# Extended discord ui button
class PollButton(discord.ui.Button):
    ...

# The parameters for the '/poll' command
class PollFlags(commands.FlagConverter):
    prompt: str
    duration_in_minutes: int

    response_one: str
    response_two: str

    response_three: Optional[str]
    response_four: Optional[str]
    response_five: Optional[str]

class Interactive(commands.Cog):
    def __init__(self, bot: discord.Client):
        self.bot: discord.Client = bot

    @commands.hybrid_command(description='Creates a poll within the current channel.', aliases=['survey', 'question'])
    async def poll_new(self, ctx: commands.Context, *, flags: PollFlags):
        end_time = datetime.now() + timedelta(minutes=flags.duration_in_minutes)

        embed: discord.Embed = discord.Embed(
            title=flags.prompt,
            color=ctx.author.color,
            timestamp=end_time
        )

        embed.set_footer(text=f'\u200bPoll created by {ctx.author.display_name}')

        view_class: discord.ui.View = create_pollview_class(flags.duration_in_minutes)
        view: discord.ui.View = view_class()
        
        # Adding PollButton objects to the view class
        strings: list[str] = [flag[1] for flag in flags if flag[1] and 'response' in flag[0]]
        for index, string in enumerate(strings):
            poll_button: PollButton = PollButton(
                label=f'\u200b{string}', 
                style=discord.ButtonStyle.primary,
                row=index
            )

            view.add_item(poll_button)

        await ctx.send(embed=embed, view=view, delete_after=flags.duration_in_minutes)
        await sleep(flags.duration_in_minutes)
        
        # <After the duration as expired>
        for button in view.to_components():
            button.disabled = True

        await ctx.send(embed=embed, view=view)


async def setup(bot: discord.Client):
    await bot.add_cog(Interactive(bot))
