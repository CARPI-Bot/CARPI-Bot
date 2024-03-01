import discord
import asyncio
from discord.ext import commands

class helpdetail(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def helpdetail(self, ctx: commands.Context):
        calculator_help = discord.Embed(title = "Calculator", description="Define function and enter two or more valid numbers, each separated by a space.", color=0x005b86)
        calculator_help.add_field(name="Commands", value="add `#` `#` ...\ndivide `#` `#` ...\nmodulus `#` `#` ...\nmultiply `#` `#` ...\npower `#` `#` ...\nsqrt `#` `#` ...\nsubtract `#` `#` ...")

        miscellaneous_help = discord.Embed(title = "Miscellaneous", description="Description Here", color=0x005b86)
        miscellaneous_help.add_field(name="Commands", value="avatar `arg`\nbanner `arg`\ncoinflip `arg`\nping `arg`\nrepo `arg`\ntextbooks `arg`")

        cousrse_search_help = discord.Embed(title = "Course Search", description="Search RPI courses and their details", color=0x005b86)
        cousrse_search_help.add_field(name="Commands", value="course `course name here`")

        calendar_help = discord.Embed(title = "Calendar", description="Calendar Details", color=0x005b86)
        calendar_help.add_field(name="Commands", value="print\nprint_week")

        pages = [calculator_help, miscellaneous_help, cousrse_search_help, calendar_help]
        buttons = [u"\u25C0", u"\u25B6"]
        current = 0

        msg = await ctx.send(embed=pages[current])

        for button in buttons:
            await msg.add_reaction(button)

        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", check=lambda reaction, user: user == ctx.author and reaction.emoji in buttons, timeout=60.0)
                if reaction.emoji == buttons[0]:  # Left arrow
                    if current > 0:
                        current -= 1
                elif reaction.emoji == buttons[1]:  # Right arrow
                    if current < len(pages) - 1:
                        current += 1
                await msg.edit(embed=pages[current])
                # Remove the user's reaction to allow for new reactions
                await msg.remove_reaction(reaction, user)
            except asyncio.TimeoutError:
                pages[current].set_footer(text="Timed out")
                await msg.edit(embed=pages[current])
                break
            except Exception as e:
                print(e) 
                

    #error checking
    @helpdetail.error
    async def stockx_error(self, ctx, error):
        await ctx.send(str(error))

#setting up the discord bot for usage
async def setup(bot):
    await bot.add_cog(helpdetail(bot))
    

