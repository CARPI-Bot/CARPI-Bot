import random
import re
from pathlib import Path

import aiomysql
import discord
from discord import app_commands, Interaction
from discord.app_commands import AppCommandError
from discord.ext import commands

from globals import ERROR_TITLE, send_generic_error


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
        ("We made this [video guide](https://www.youtube.com/watch?v=QX43QTYyV-8) to help new " + 
            "users with this bot!", 25)
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

def get_credits_desc(min, max) -> str:
    """
    A helper function that converts a minimum and maximum credit value to a description.
    """
    if min == max:
        return max
    return f"Between {min} and {max}"

def get_match_type(row) -> str:
    """
    A helper function that, given a row returned from an SQL query, identifies and returns the type
    of match made between the search term and the given result.
    """
    if row['code_match']:
        return "Code Match"
    if row['title_exact_match']:
        return "Exact Title Match"
    if row['title_start_match'] or row['title_match']:
        return "Title Match"
    if row['title_similar']:
        return "Acronym or Abbreviation Match"

# TODO: change search to prioritize matches at the beginning of the
# name, convert numbers to roman numerals or back, prioritize lower
# level classes, prioritize full title match
# TODO: add prerequisite courses to related courses if there are no
# others, or add them to the dropdown with a (prereq) next to it
# TODO: if you want to make the search algorithm crazy, do research
# about subprocesses so you don't hold up the bot

class CourseSearch(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db_conn = None
        query_path = Path("./cogs/course_search/course_data.sql").resolve()
        with query_path.open() as query:
            self.course_query = query.read()
    
    async def cog_load(self) -> None:
        self.db_conn = await self.bot.sql_conn_pool.acquire()
    
    async def cog_unload(self) -> None:
        self.db_conn.close()

    @app_commands.command(
        name = "course",
        description = "Search for a course in the RPI catalog!"
    )
    async def course(self, interaction: Interaction, *, search_term: str):
        search_term = sanitize_str(search_term)
        if len(search_term) == 0:
            raise "Bad argument"
        view = CourseMenu(interaction, self.db_conn, self.course_query)
        await view.course_query(search_term)
        await interaction.response.send_message(
            view = view,
            embed = view.embed,
            ephemeral = False
        )

    @course.error
    async def course_error(self, interaction: Interaction, error: AppCommandError):
        embed_desc = None
        if error == "Bad argument":
            embed_desc = f"Your input is invalid! Try something else."
        else:
            error = error.original
        if embed_desc is not None:
            embed_var = discord.Embed(
                title = ERROR_TITLE,
                description = embed_desc,
                color = 0xC80000
            )
            await interaction.response.send_message(embed=embed_var)
        else:
            # Interaction errors not supported yet by the bot
            print(error)
    
class CourseMenu(discord.ui.View):
    def __init__(
        self,
        interaction: Interaction,
        db_conn: aiomysql.Connection,
        query: str
    ):
        super().__init__()
        self.interaction = interaction
        self.db_conn = db_conn
        self.query = query
        self.related_courses = []
        self.embed = discord.Embed(
            title = "Course Search Error",
            description = "If you're seeing this, someting went wrong.",
            color = 0xC80000
        )

    async def course_query(self, search_term):
        """
        This function modifies this CourseMenu to use the specified query, and change the embed to
        show the resulting course.
        """
        reg_start_or_space = "(^|.* )"
        # Just the search itself
        regex1 = search_term
        # A full title match
        regex2 = f"^{search_term}$"
        # Title matched at the beginning
        regex3 = f"^{search_term}"
        regex4 = "("
        # For acronyms
        if len(search_term) > 1:
            regex4 += reg_start_or_space
            for char in search_term:
                # Don't use spaces in acronyms
                if char != " ":
                    regex4 += f"{char}.* "
            regex4 = regex4[:-3]
        tokens = search_term.split()
        
        # For abbreviations
        if len(tokens) > 1:
            regex4 += f"|{reg_start_or_space}"
            for token in tokens:
                regex4 += f"{token}.* "
            regex4 = regex4[:-3]
        regex4 += ")"
        
        # Default embed is "no matches", it will only be changed if there is a match.
        self.embed = discord.Embed(
            title = "No Matches",
            description = "Try searching for something else.",
            color = 0xC80000
        )
        self.embed.add_field(
            name = "Tip:",
            value = get_random_tip()
        )

        # Execute the query
        async with self.db_conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(
                self.query,
                (search_term, regex1, regex2, regex3, regex4)
            )

            # The dictionary keys, and the corresponding field names for the embed
            field_names = (
                ['prereqs', "Prerequisites"],
                ['coreqs', "Corequisites"],
                ['crosslist', "Crosslisted"],
                ['restrictions', "Restrictions"]
            )
            # Get rid of UI elements, in case they are not needed for the next result
            self.clear_items()
            self.related_courses = []
            rel_courses_field = ""
            match_type = ""
            # Fetch all data from the cursor, then parse through it
            for row_num, row in enumerate(await cursor.fetchall()):
                print(f"{row['dept']} {row['code_num']}: {row['title']} - {row['code_match']} {row['title_exact_match']} {row['title_start_match']} {row['title_match']} {row['title_similar']}")
                # The first result is the main result
                if row_num == 0:
                    self.embed = discord.Embed(
                        title = f"{row['dept']} {row['code_num']}: {row['title']}",
                        color = 0xff00ff
                    )
                    if row['desc_text'] is not None:
                        self.embed.description = row['desc_text']
                    self.embed.add_field(
                        name = "Credits",
                        value = get_credits_desc(row['credit_min'], row['credit_max']),
                        inline = False
                    )
                    for element in field_names:
                        if row[element[0]] is not None:
                            self.embed.add_field(
                                name = element[1],
                                value = row[element[0]],
                                inline = False
                            )
                    match_type = get_match_type(row)
                # Anything not the first result is just "related"
                else:
                    self.related_courses.append(
                        discord.SelectOption(
                            label = f"{row['dept']} {row['code_num']}: {row['title']}",
                            value = f"{row['dept']} {row['code_num']}"
                        )
                    )
                    rel_courses_field += f"{row['dept']} {row['code_num']}: {row['title']}\n"
            if len(rel_courses_field) > 0:
                self.embed.add_field(
                    name = "Related Courses",
                    value = rel_courses_field.strip("\n"),
                    inline = False
                )
            self.embed.set_author(name = f"{search_term} → {match_type}!")
        if len(self.related_courses) > 0:
            dropdown = RelatedCourseDropdown(
                placeholder = "Choose a related course to learn more...",
                options = self.related_courses
            )
            self.add_item(dropdown)

class RelatedCourseDropdown(discord.ui.Select):
    def __init__(
        self,
        options: list[discord.SelectOption],
        placeholder: str,
        **kwargs
    ):
        super().__init__(
            options = options,
            placeholder = placeholder,
            **kwargs
        )

    async def callback(self, interaction: Interaction) -> None:
        await interaction.response.send_message("🫡")

async def setup(bot: commands.Bot):
    await bot.add_cog(CourseSearch(bot))