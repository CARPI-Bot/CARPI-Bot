import discord
import asyncio
from discord.ext import commands


class help_menu(discord.ui.View):
    def __init__(self, pages):
        super().__init__(timeout=120)
        self.pages = pages
        self.current = 0

    @discord.ui.button(label=u"\u25C0", style=discord.ButtonStyle.primary)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current == 0:
            self.current = len(self.pages) - 1
        else:
            self.current -= 1
        await interaction.response.edit_message(embed=self.pages[self.current])

    @discord.ui.button(label=u"\u25B6", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current == len(self.pages) - 1:
            self.current = 0
        else:
            self.current += 1
        await interaction.response.edit_message(embed=self.pages[self.current])

class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(
        description = "Help command that shows all CARPI commands"
    )
    async def help(self, ctx: commands.Context):
        pages = []
        page_number = 1;
        for cog_name, cog in self.bot.cogs.items():
            embed = discord.Embed(title=cog_name, color=0x005b86)

            for command in cog.get_commands():
                if command.description == "":
                    cog_description = "No Descripton"
                else:
                    cog_description = command.description
                embed.add_field(name=command.name, value=cog_description, inline=False)
                embed.set_footer(text=f"Page {page_number}")
            pages.append(embed)
            page_number += 1

        view = help_menu(pages)
        
        await ctx.send(embed=pages[0], view=view)        

    #error checking
    @help.error
    async def help_error(self, ctx, error):
        await ctx.send(str(error))

#setting up the discord bot for usage
async def setup(bot):
    await bot.add_cog(Help(bot))
    

