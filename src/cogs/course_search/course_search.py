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
    # Move this to an external MODULE, eventually
    tips = (
        ("Don't know what all the terminology means? Try using `/course_terms`!", 200),
        ("You can search by acronyms! Try `FOCS` or `MAU`.", 100),
        ("You can search by abbreviations! Try `Comp Org` or `P Soft`.", 100),
        ("This bot was made in RCOS! Consider joining the class next semester.", 100),
        ("You can die from radiation poisioning by eating 10 million bananas. Try not to.", 10),
        ("We made this [video guide](https://www.youtube.com/watch?v=QX43QTYyV-8) to help new " + 
            "users with this bot!", 10)
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
    if row['title_acronym']:
        return "Acronym Match"
    if row['title_abbrev']:
        return "Abbreviation Match"

async def course_search_embed(cursor: aiomysql.DictCursor, search_term: str) \
    -> tuple[discord.Embed, list[discord.SelectOption]]:
    """
    This function, given a cursor, returns an embed that displays the results of the course search
    query.

    If `search_term` is left blank, that indicates that  the search term should NOT be shown at the
    top of the embed. For example, in a search started by selecting from a dropdown, the search term
    should not be shown, as it will directly match a course code, and was not the user's typed
    input.
    """
    # The dictionary keys, and the corresponding field names for the embed
    field_names = (
        ['prereqs', "Prerequisites"],
        ['coreqs', "Corequisites"],
        ['cross_list', "Crosslisted"],
        ['restrictions', "Restrictions"]
    )
    related_courses = []
    rel_courses_field = ""
    match_type = ""
    new_embed = None
    # Fetch all data from the cursor, then parse through it
    for row_num, row in enumerate(await cursor.fetchall()):
        # The first result is the main result
        if row_num == 0:
            new_embed = discord.Embed(
                title = f"{row['dept']} {row['code_num']}: {row['title']}",
                color = 0xff00ff
            )
            if row['desc_text'] is not None:
                new_embed.description = row['desc_text']
            new_embed.add_field(
                name = "Credits",
                value = get_credits_desc(row['credit_min'], row['credit_max']),
                inline = False
            )
            for element in field_names:
                if row[element[0]] is not None:
                    new_embed.add_field(
                        name = element[1],
                        value = row[element[0]],
                        inline = False
                    )
            match_type = get_match_type(row)
        # Anything not the first result is just "related"
        else:
            related_courses.append(
                discord.SelectOption(
                    label = f"{row['dept']} {row['code_num']}: {row['title']}",
                    value = f"{row['dept']} {row['code_num']}"
                )
            )
            rel_courses_field += f"{row['dept']} {row['code_num']}: {row['title']}\n"
    if len(rel_courses_field) > 0:
        new_embed.add_field(
            name = "Other Matches",
            value = rel_courses_field.strip("\n"),
            inline = False
        )
    if (match_type != "" and search_term != ""):
        new_embed.set_author(name = f"\"{search_term}\" → {match_type}!")
    return new_embed, related_courses
    

# TODO: convert numbers to roman numerals or back
# TODO: add prerequisite courses to related courses with (prereq) next to it
# TODO: if you want to make the search algorithm crazy, do research about subprocesses so you don't
# hold up the bot
# TODO: ask users what they were looking for if there are no matches
# TODO: account for course codes with dashes or underscores (or anything in between)
# TODO: add default embed that "welcomes" users if no argument is given
# TODO: make it so each dropdown option can only be selected once

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
        self.bot.sql_conn_pool.release(self.db_conn)

    @app_commands.command(
        name = "course",
        description = "Search for a course in the RPI catalog!"
    )
    @app_commands.describe(course = "The course you want to search for, as a code or name.")
    async def course(self, interaction: Interaction, *, course: str):
        course = sanitize_str(course)
        if len(course) == 0:
            raise "Bad argument"
        view = CourseMenu(interaction, self.db_conn, self.course_query)
        await view.course_query(course)
        await interaction.response.send_message(
            view = view,
            embed = view.embed,
            ephemeral = False
        )

    @app_commands.command(
        name = "course_terms",
        description = "Learn how to understand course search info."
    )
    async def course_terms(self, interaction: Interaction):
        view = CourseMenu(interaction, self.db_conn, self.course_query)
        help_embed = discord.Embed(
            title = "CRPI 2024: Course Search",
            description = "This is a course! Every course has a department (CRPI), code (2024), " +
                "and title (Course Search), as shown in the header above.",
            color = 0xFF00FF
        )
        help_embed.add_field(
            name = "Credits",
            value = "This is the number of credit hours you can earn for this course. For some " +
                "courses, it can vary between sections.",
            inline = False
        )
        help_embed.add_field(
            name = "Prerequisites",
            value = "These are courses that you must take before (or in some cases, during) this " +
                "course.",
            inline = False
        )
        help_embed.add_field(
            name = "Corequisites",
            value = "These are courses that you must take alongside this course.",
            inline = False
        )
        help_embed.add_field(
            name = "Crosslisted",
            value = "These are courses where you cannot earn credit if you've already completed " +
                "this course, and vice versa.",
            inline = False
        )
        help_embed.add_field(
            name = "Restrictions",
            value = "These are conditions you must fulfill in order to take this course. Some " +
                "examples are major and year restrictions.",
            inline = False
        )
        help_embed.add_field(
            name = "Other Matches",
            value = "These are other course results from your search. You can choose any of them " +
                "from the dropdown menu to learn more.",
            inline = False
        )
        view.set_embed(help_embed)
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
        This function searches for a course using the query defined when constructing this object,
        and changes the embed to show the resulting course.
        """
        reg_start_or_space = "(^|.* )"
        # Full code match
        regex_code = f"^{search_term}$"
        # Full title match
        regex_full = f"^{search_term}$"
        # Title matched at the beginning
        regex_start = f"^{search_term}"
        # Title matched anywhere
        regex_any = search_term
        # For acronyms
        regex_acronym = ""
        if len(search_term) > 1:
            regex_acronym += reg_start_or_space
            for char in search_term:
                # Don't use spaces in acronyms
                if char != " ":
                    regex_acronym += f"{char}.* "
            regex_acronym = regex_acronym[:-3]
        else:
            regex_acronym = "a^" # Automatically make no matches if there's only one character
        # For abbreviations
        regex_abbrev = ""
        tokens = search_term.split()
        if len(tokens) > 1:
            regex_abbrev += reg_start_or_space
            for token in tokens:
                regex_abbrev += f"{token}.* "
            regex_abbrev = regex_abbrev[:-3]
        else:
            regex_abbrev = "a^"
        
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
        self.embed.set_author(name = f"\"{search_term}\" → Nothing...")

        # Execute the query
        async with self.db_conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(
                self.query,
                (regex_code, regex_full, regex_start, regex_any, regex_acronym, regex_abbrev)
            )

            # Get rid of UI elements, in case they are not needed for the next result
            self.clear_items()
            new_embed, self.related_courses = await course_search_embed(cursor, search_term)
            if new_embed is not None:
                self.embed = new_embed
            
        if len(self.related_courses) > 0:
            dropdown = RelatedCourseDropdown(
                placeholder = "Choose a course to learn more!",
                options = self.related_courses
            )
            self.add_item(dropdown)

    def set_embed(self, embed):
        """
        Directly set the embed of this menu. Useful for an override, like in `course_terms`.
        """
        self.embed = embed

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
        # Steal the connection from the view, then create a cursor
        async with self.view.db_conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(
                self.view.query, # Use the same query
                (f"^{self.values[0]}$", "a^", "a^", "a^", "a^", "a^") # Only match course code
            )
            # Make sure to unpack the tuple, and we don't need related courses (should be none)
            new_embed, _ = await course_search_embed(cursor, "")
            # Send a new message
            await interaction.response.send_message(embed = new_embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(CourseSearch(bot))