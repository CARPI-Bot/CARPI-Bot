from datetime import datetime
from datetime import timedelta
import random
import re
from pathlib import Path

import aiomysql
import discord
from discord import app_commands, Interaction
from discord.app_commands import AppCommandError
from discord.ext import commands

from globals import ERROR_TITLE, send_generic_error

# Global variables
# SQL queries
course_query = ""
code_match_query = ""
# File info
assets_path = Path(__file__).parent.parent.with_name("assets")
rpi_seal = "rpi_small_seal_red.png"

def sanitize_str(input: str) -> str:
    """
    Returns a copy of the input in which all non-alphanumeric characters
    are eliminated, except for spaces.
    """
    return re.sub(
        pattern = " +",
        repl = " ",
        string = re.sub(
            pattern = r"[^a-zA-Z0-9-_&' ]",
            repl = "",
            string = input
        )
    )

def get_codes(input: str) -> list:
    """
    Returns a list of course codes for the given prerequisite string.
    """
    codes = re.sub(
        pattern = r"(or|and|\(|\))",
        repl = "",
        string = input
    )
    codes = codes.split("  ")
    new_codes = []
    for code in codes:
        # Account for concatenation where courses are joined by a comma
        new_codes += [s.strip() for s in code.split(",")]
    return new_codes

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
        ("You can die from radiation poisioning by eating 10 million bananas. Try not " +
            "to.", 10),
        ("We made this [video guide](https://www.youtube.com/watch?v=QX43QTYyV-8) to " +
            "help new users with this bot!", 10)
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
    A helper function that, given a row returned from an SQL query, identifies and returns
    the type of match made between the search term and the given result.
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

def get_restriction_info(row: dict) -> str:
    """
    Given a row returned from the course search, returns a string that represents the
    restrictions that correspond to the row's course.

    If there are no restrictions, returns an empty string.
    """
    return_string = ""
    # The dictionary keys, and the corresponding names to be used in the string
    field_names = (
        ['restr_major', "Major"],
        ['restr_clsfctn', "Classification"],
        ['restr_degree', "Degree"],
        ['restr_field', "Field"],
        ['restr_campus', "Campus"],
        ['restr_college', "College"]
    )
    for element in field_names:
        if row[element[0]] is not None:
            # TODO: This is a temporary solution for restrictions being too long
            # The real problem is that it should be stored differently in the database
            max_str = max(row[element[0]].split(','), key = len)
            return_string += f"{element[1]}: {max_str}\n"
    if len(return_string) > 0:
        return return_string[:-1]
    return return_string

async def get_course_options(conn: aiomysql.Connection, codes: list[str], label: str) \
    -> list[discord.SelectOption]:
    """
    This function returns a list of dropdown options that correspond to the given list of 
    prerequisite codes.

    The argument `label` is a string that will be displayed alongside the course code an
    name in the dropdown. For example if `label` is "Prereq", then a dropdown option would
    have the name "(Prereq) CSCI 1010: Calculus I".
    """
    cursor = await conn.cursor(aiomysql.DictCursor)
    regex_str = "("
    for code in codes:
        regex_str += code + "|"
    regex_str = regex_str[:-1] + ")"
    await cursor.execute(code_match_query, regex_str)
    prereq_options = []
    for row in await cursor.fetchall():
        prereq_options.append(
            discord.SelectOption(
                label = f"({label}) {row['dept']} {row['code_num']}: {row['title']}",
                value = f"{row['dept']} {row['code_num']}"
            )
        )
    return prereq_options

def make_unique_options(optns: list[discord.SelectOption]) -> list[discord.SelectOption]:
    """
    Returns a set of options, made unique by their course code. This function will only
    keep the first instance of a course in the list.
    """
    code_list = []
    new_options = []
    for option in optns:
        if option.value not in code_list:
            code_list.append(option.value)
            new_options.append(option)
    return new_options

async def course_search_embed(conn: aiomysql.Connection, cursor: aiomysql.DictCursor,
    search_term: str) -> tuple[discord.Embed, list[discord.SelectOption]]:
    """
    This function, given a cursor, returns an embed that displays the results of the
    course search query.

    If `search_term` is left blank, that indicates that  the search term should NOT be
    shown at the top of the embed. For example, in a search started by selecting from a
    dropdown, the search term should not be shown, as it was not the user's typed input.
    """
    # The dictionary keys, the field names for the embed, and labels for the dropdown
    field_names = (
        ['instructors', "Instructors", None],
        ['prereqs', "Prerequisites", "Prereq"],
        ['coreqs', "Corequisites", "Coreq"],
        ['cross_list', "Crosslisted", "Cross"]
    )
    # Courses that will be in the dropdown
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
                color = 0xd6001c
            )
            credits = get_credits_desc(row['credit_min'], row['credit_max'])
            # Credits, or add that the course is not offered
            if credits is not None:
                new_embed.add_field(
                    name = "Credits",
                    value = credits,
                    inline = False
                )
            else:
                if row['desc_text'] is not None:
                    new_embed.description = row['desc_text'] + "\n*This course was " + \
                        "not offered during the chosen semester.*"
                else: # TODO: change both of these to say the semester dynamically
                    new_embed.description = "*This course was not offered during the " + \
                        "chosen semester.*"
            for element in field_names:
                if row[element[0]] is not None:
                    if element[2] and row[element[0]]: # If they are both not null
                        codes = get_codes(row[element[0]])
                        # Add prereqs, coreqs, crosslists to the dropdown
                        related_courses += await get_course_options(
                            conn,
                            codes,
                            element[2]
                        )
                    new_embed.add_field(
                        name = element[1],
                        value = row[element[0]].replace(',', ', '),
                        inline = False
                    )
            restr_str = get_restriction_info(row)
            if restr_str != "":
                new_embed.add_field(
                    name = "Restrictions",
                    value = restr_str,
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
    if match_type != "":
        new_embed.set_footer(text = "Data from Spring 2024") # TODO: dynamically change
        new_embed.set_thumbnail(url = "attachment://rpi_small_seal_red.png")
        if search_term != "":
            if len(search_term) > 32:
                new_embed.set_author(name = f"\"{search_term[:32]}...\" → {match_type}!")
            else:
                new_embed.set_author(name = f"\"{search_term}\" → {match_type}!")
    return new_embed, related_courses

def get_terms_embed():
    new_embed = discord.Embed(
        title = "CRPI 2024: Course Search",
        description = "This is a course! Every course has a department (CRPI), code " +
            "(2024), and title (Course Search), as shown in the header above.",
        color = 0xd6001c
    )
    new_embed.add_field(
        name = "Credits",
        value = "This is the number of credit hours you can earn for this course. For " +
            "some courses, it can vary between sections.",
        inline = False
    )
    new_embed.add_field(
        name = "Instructors",
        value = "This is a list of all the professors that teach this course. It often " +
            "varies between sections.",
        inline = False
    )
    new_embed.add_field(
        name = "Prerequisites",
        value = "These are courses that you must take before (or in some cases, during)" +
            " this course.",
        inline = False
    )
    new_embed.add_field(
        name = "Corequisites",
        value = "These are courses that you must take alongside this course.",
        inline = False
    )
    new_embed.add_field(
        name = "Crosslisted",
        value = "These are courses where you cannot earn credit if you've already " +
            "completed this course, and vice versa.",
        inline = False
    )
    new_embed.add_field(
        name = "Restrictions",
        value = "These are conditions you must fulfill in order to take this course. " +
            "Some examples are major and year restrictions.",
        inline = False
    )
    new_embed.add_field(
        name = "Other Matches",
        value = "These are other course results from your search. You can choose any of" +
            " them from the dropdown menu to learn more.",
        inline = False
    )
    return new_embed   

# TODO: convert numbers to roman numerals or back (also do this with & and AND)
# TODO: add prerequisite courses to related courses with (prereq) next to it
# TODO: if you want to make the search algorithm crazy, do research about subprocesses so
# you don't hold up the bot
# TODO: ask users what they were looking for if there are no matches
# TODO: account for course codes with dashes or underscores (or anything in between)
# TODO: add default embed that "welcomes" users if no argument is given

class CourseSearch(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db_conn = None
        course_query_path = Path(__file__).with_name("course_data.sql")
        with course_query_path.open() as query:
            global course_query
            course_query = query.read()
        code_match_query_path = Path(__file__).with_name("code_match.sql")
        with code_match_query_path.open() as query:
            global code_match_query
            code_match_query = query.read()
    
    async def cog_load(self) -> None:
        self.db_conn = await self.bot.sql_conn_pool.acquire()
    
    async def cog_unload(self) -> None:
        self.bot.sql_conn_pool.release(self.db_conn)

    @app_commands.command(
        name = "course",
        description = "Search for a course in the RPI catalog!"
    )
    @app_commands.describe(course = "The course you want to search for.")
    async def course(self, interaction: Interaction, *, course: str):
        course = sanitize_str(course)
        if len(course) == 0:
            raise InvalidArgument
        elif len(course) > 128:
            raise LongArgument
        elif len(course) <= 1:
            raise ShortArgument
        view = CourseMenu(interaction, self.db_conn, 120, self.bot)
        self.bot.loop.create_task(view.timeout_timer(300))
        if (await view.course_query(course)): # if the query returned a result
            thumbnail = discord.File(
                fp =  assets_path / rpi_seal,
                filename = rpi_seal
            )
            await interaction.response.send_message(
                file = thumbnail,
                view = view,
                embed = view.embed,
                ephemeral = False
            )
        else:
            await interaction.response.send_message(
                view = view,
                embed = view.embed,
                ephemeral = False
            )

    @app_commands.command(
        name = "course_terms",
        description = "Learn how to understand course search info."
    )
    @app_commands.describe(public = "Whether to show this to everyone, or just you.")
    async def course_terms(self, interaction: Interaction, public: bool = False):
        # Create a view that times out instantly, there's nothing interactable
        view = CourseMenu(interaction, self.db_conn, 0, self.bot)
        help_embed = get_terms_embed()
        view.set_embed(help_embed)
        await interaction.response.send_message(
            view = view,
            embed = view.embed,
            ephemeral = not public
        )

    @course.error
    async def course_error(self, interaction: Interaction, error: AppCommandError):
        embed_desc = None
        desc_extra = ""
        lottery = random.randint(1, 3) == 3
        if isinstance(error, InvalidArgument):
            embed_desc = "Your input is invalid! Try something else."
        elif isinstance(error, LongArgument):
            embed_desc = "Your input is too long! Try something shorter."
            if (lottery):
                desc_extra = "If you like typing so much, do it [here]" + \
                    "(https://play.typeracer.com/) instead!"
        elif isinstance(error, ShortArgument):
            embed_desc = "Your input is too short! Try something longer."
            if (lottery):
                desc_extra = "If you hate typing THAT much... we can't exactly type " + \
                    " for you. You can find the course yourself [here]" + \
                    "(https://catalog.rpi.edu/)!"
        else:
            error = error.original
        if embed_desc is not None:
            embed_var = discord.Embed(
                title = ERROR_TITLE,
                description = embed_desc,
                color = discord.Color.red()
            )
            if len(desc_extra) > 0:
                embed_var.description += "\n\n" + desc_extra
            else:
                embed_var.add_field(
                    name = "Tip",
                    value = get_random_tip(),
                    inline = False
                )
            await interaction.response.send_message(embed=embed_var)
        else:
            # Interaction errors not supported yet by the bot
            print(error)
            raise error
    
class CourseMenu(discord.ui.View):
    def __init__(
        self,
        interaction: Interaction,
        db_conn: aiomysql.Connection,
        def_timeout: float,
        bot: commands.Bot
    ):
        super().__init__(
            timeout = def_timeout
        )
        self.interaction = interaction
        self.db_conn = db_conn
        self.related_courses = []
        self.embed = discord.Embed(
            title = "Course Search Error",
            description = "If you're seeing this, someting went wrong.",
            color = discord.Color.red()
        )
        self.timed_out = False
        self.bot = bot
        self.followup_msg = None

    async def course_query(self, search_term) -> bool:
        """
        This function searches for a course using the query defined when constructing this
        object, and changes the embed to show the resulting course.

        Returns true if the query found one or more matches.
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
        regex_acronym = reg_start_or_space
        for char in search_term:
            # Don't use spaces in acronyms
            if char != " ":
                regex_acronym += f"{char}.* "
        regex_acronym = regex_acronym[:-3]
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
            color = discord.Color.red()
        )
        self.embed.add_field(
            name = "Tip",
            value = get_random_tip()
        )
        if len(search_term) > 32:
            self.embed.set_author(name = f"\"{search_term[:32]}...\" → Nothing...")
        else:
            self.embed.set_author(name = f"\"{search_term}\" → Nothing...")

        # Execute the query
        async with self.db_conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(
                course_query,
                (
                    regex_code,
                    regex_full,
                    regex_start,
                    regex_any,
                    regex_acronym,
                    regex_abbrev
                )
            )

            # Get rid of UI elements, in case they are not needed for the next result
            self.clear_items()
            new_embed, self.related_courses = await course_search_embed(
                self.db_conn,
                cursor,
                search_term
            )
            if new_embed is not None:
                self.embed = new_embed
            
        if len(self.related_courses) > 0:
            self.related_courses = make_unique_options(self.related_courses)
            dropdown = RelatedCourseDropdown(
                placeholder = "Choose a course to learn more!",
                options = self.related_courses
            )
            self.add_item(dropdown)
        
        return new_embed is not None

    def set_embed(self, embed):
        """
        Directly set the embed of this menu. Useful for an override, like in
        `course_terms`.
        """
        self.embed = embed
    
    def set_followup_msg(self, msg: discord.WebhookMessage) -> None:
        """
        Set the followup message to be edited during `on_timeout()`. Necessary for embeds
        created from dropdown menu interactions that have dropdowns themselves.
        """
        self.followup_msg = msg
    
    async def on_timeout(self) -> None:
        if self.timed_out: return
        self.timed_out = True
        # If there are interactable items, make them inactive and show a message
        if len(self.children) > 0:
            for item in self.children:
                item.disabled = True
            # If a footer already exists, show the message next to it
            if self.embed.footer.text is not None:
                self.embed.set_footer(text = self.embed.footer.text + \
                    "  •  This menu has expired due to inactivity.")
            else:
                self.embed.set_footer(text = "This menu has expired due to inactivity.")
            if self.followup_msg is None:
                await self.interaction.edit_original_response(
                    view = self,
                    embed = self.embed
                )
            else:
                await self.followup_msg.edit(view = self, embed = self.embed)
    
    async def timeout_timer(self, sec: int) -> None:
        await discord.utils.sleep_until(datetime.now() + timedelta(seconds = sec))
        await self.on_timeout()

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
                course_query, # Use the same query
                (f"^{self.values[0]}$", "a^", "a^", "a^", "a^", "a^") # Only match code
            )
            # Reset the dropdown to show the placeholder
            self.view.remove_item(self).add_item(self)
            # Make sure to unpack the tuple
            new_embed, rel_courses = await course_search_embed(
                self.view.db_conn,
                cursor,
                ""
            )
            # Create a new view so another dropdown can be added if need be
            new_view = None
            if len(rel_courses) > 0:
                dropdown = RelatedCourseDropdown(
                    placeholder = "Choose a course to learn more!",
                    options = rel_courses
                )
                new_view = CourseMenu(
                    interaction,
                    self.view.db_conn,
                    120,
                    self.view.bot
                )
                self.view.bot.loop.create_task(new_view.timeout_timer(300))
                new_view.add_item(dropdown)
            # Edit the message to update the dropdown
            await interaction.response.edit_message()
            # Create a new file for the seal
            thumbnail = discord.File(
                fp =  assets_path / rpi_seal,
                filename = rpi_seal
            )
            # Send a new message, but only to the user who chose the option
            if new_view is not None:
                # Store the message to be edited later for timeout
                msg = await interaction.followup.send(
                    file = thumbnail,
                    view = new_view,
                    embed = new_embed,
                    ephemeral = True,
                    wait = True
                )
                # Send the message object to the view to be handled in on_timeout()
                new_view.set_followup_msg(msg)
                # And give it the embed too so it edits it properly
                new_view.set_embed(new_embed)
            else:
                await interaction.followup.send(
                    file = thumbnail,
                    embed = new_embed,
                    ephemeral = True
                )

async def setup(bot: commands.Bot):
    await bot.add_cog(CourseSearch(bot))

class InvalidArgument(app_commands.AppCommandError):
    pass

class LongArgument(app_commands.AppCommandError):
    pass

class ShortArgument(app_commands.AppCommandError):
    pass
