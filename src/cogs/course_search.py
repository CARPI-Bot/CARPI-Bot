import random
import re

import aiomysql
import discord
from discord.ext import commands
from discord.ext.commands import CommandError, Context

from globals import ERROR_TITLE, SQL_LOGIN, send_generic_error


def sanitize_str(input: str) -> str:
    """
    Returns a copy of the input in which all non-alphanumeric characters
    are eliminated, except for spaces.
    """
    return re.sub(
        pattern = " +",
        repl = " ",
        string = re.sub(
            pattern = "[^a-zA-Z0-9 ]",
            repl = "",
            string = input
        )
    )

def get_random_tip() -> str:
    """
    Returns a random tip.
    """
    # Move this to an external file, maybe
    tips = (
        ("You can search by acronyms! Try `RCOS` or `FOCS`.", 100),
        ("You can search by abbreviations! Try `Comp Org` or `P Soft`.", 100),
        ("This bot was made in RCOS! Consider joining the class next semester.", 100),
        ("You can die from radiation poisioning by eating 10 million bananas. Try not to.", 25),
        ("We made this [video guide](https://www.youtube.com/watch?v=QX43QTYyV-8) to help new users with this bot!", 25)
    )
    total_prob = 1
    for tip in tips:
        total_prob += tip[1]
    rand_tip = random.randint(0, total_prob)
    total_prob = 0
    for tip in tips:
        total_prob += tip[1]
        if rand_tip <= total_prob:
            return tip[0]
    # Has a 1/total chance of appearing
    return "There is no tip. Have a nice day."

# TODO: change search to prioritize matches at the beginning of the
# name, convert numbers to roman numerals or back, prioritize lower
# level classes, prioritize full title match

class CourseSearch(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.connection = None
        self.cursor = None
        # Move this to an external file, maybe
        self.search_query = """
            SELECT
                dept, # 0
                `code`, # 1
                `name`, # 2
                `description`, # 3
                `offered`, # 4
                `url`, # 5
                `credits`, # 6
                `prereq_coreq`, # 7
                `colisted`, # 8
                `crosslisted`, # 9
                `contact_lecture_lab_hours`, # 10
                REGEXP_LIKE(CONCAT(dept, " ", `code`), %s, 'i') AS code_match, # 11
                REGEXP_LIKE(`name`, %s, 'i') AS title_match, # 12
                REGEXP_LIKE(`name`, %s, 'i') AS title_similar # 13
            FROM
                courses
            HAVING
                title_match > 0
                OR title_similar > 0
                OR code_match > 0
            ORDER BY
                `name` ASC, code_match DESC, title_match DESC, title_similar DESC
            LIMIT 6
        """
    
    async def cog_load(self) -> None:
        try:
            self.connection: aiomysql.Connection = await aiomysql.connect(**SQL_LOGIN)
        except:
            raise Exception(
                "Could not connect to MySQL database. Make sure the server " \
                + "is running, and that your login information is correct"
            )
        self.cursor: aiomysql.Cursor = await self.connection.cursor()
    
    async def cog_unload(self) -> None:
        if self.connection:
            await self.cursor.close()
            await self.connection.close()

    @commands.hybrid_command(
        description = "Search for a course in the RPI catalog!"
    )
    async def course(self, ctx: Context, *, search_term: str):
        search_term = sanitize_str(search_term)
        if len(search_term) == 0:
            raise commands.BadArgument
        reg_start_or_space = "(^|.* )"
        # Just the search itself
        regex1 = search_term
        regex2 = "("
        # For acronyms
        if len(search_term) > 1:
            regex2 += reg_start_or_space
            for char in search_term:
                # Don't use spaces in acronyms
                if char != " ":
                    regex2 += f"{char}.* "
            regex2 = regex2[:-3]
        tokens = search_term.split()
        
        # For abbreviations
        if len(tokens) > 1:
            regex2 += f"|{reg_start_or_space}"
            for token in tokens:
                regex2 += f"{token}.* "
            regex2 = regex2[:-3]
        regex2 += ")"
        
        await self.cursor.execute(self.search_query, (search_term, regex1, regex2))
        
        # Default embed is "no matches", it will only be changed if
        # there is a match.
        return_embed = discord.Embed(
            title = "No Matches",
            description = "Try searching for something else.",
            color = 0xC80000
        )
        return_embed.add_field(
            name = "Tip:",
            value = get_random_tip()
        )

        field_names = (
            "",
            "",
            "",
            "",
            "Offered",
            "",
            "Credits",
            "Prereq/Coreq",
            "Colisted",
            "Crosslisted",
            "Contact/Lecture/Lab Hours"
        )
        similar_matches = ""
        for row_num, row in enumerate(await self.cursor.fetchall()):
            if row_num == 0:
                return_embed = discord.Embed(
                    title = f"{row[0]} {row[1]}: {row[2]}",
                    description = row[3],
                    url = row[5],
                    color = 0xff00ff
                )
                for element_num, element in enumerate(row):
                    if element_num >= len(field_names):
                        break
                    if element and len(field_names[element_num]) > 0:
                        return_embed.add_field(
                            name = field_names[element_num],
                            value = element,
                            inline = False
                        )
            else:
                similar_matches += f"{row[0]} {row[1]}: {row[2]}\n"
        if len(similar_matches) > 0:
            return_embed.add_field(
                name = "Similar Matches",
                value = similar_matches.strip('\n')
            )
        await ctx.send(embed = return_embed)

    @course.error
    async def course_error(self, ctx: Context, error: CommandError):
        embed_desc = None
        if isinstance(error, commands.CommandInvokeError):
            error = error.original
        if isinstance(error, commands.MissingRequiredArgument):
            embed_desc = f"Usage: `{self.bot.command_prefix}course [search term]`"
        elif isinstance(error, commands.BadArgument):
            embed_desc = f"Your input is invalid! Try something else."
        if embed_desc is not None:
            embed_var = discord.Embed(
                title = ERROR_TITLE,
                description = embed_desc,
                color = 0xC80000
            )
            await ctx.send(embed=embed_var)
        else:
            await send_generic_error(ctx, error)
    
async def setup(bot: commands.Bot):
    await bot.add_cog(CourseSearch(bot))