import discord
from discord.ext import commands
import mysql.connector as mysql
import re
import random
import logging
from globals import ERROR_TITLE, COMMAND_PREFIX, SQL_LOGIN, SQL_SCHEMA, sendUnknownError

Context = commands.Context

# Filters the user input so all non-alphanumeric characters are eliminated, except for spaces
def sanitize_str(input:str) -> str:
    return re.sub(
        pattern = " +",
        repl = " ",
        string = re.sub(
            pattern = "[^a-zA-Z0-9 ]",
            repl = "",
            string = input
        )
    )

def get_random_tip(self) -> str:
    total_prob = 1
    for tip in self.tips:
        total_prob += tip[1]
    rand_tip = random.randint(0, total_prob)
    total_prob = 0
    for tip in self.tips:
        total_prob += tip[1]
        if rand_tip <= total_prob:
            return tip[0]
    return "There is no tip. Have a nice day." # Has a 1/total chance of appearing

##### TODO: change search to prioritize matches at the beginning of the name, convert numbers to roman numerals or back, prioritize lower level classes, prioritize full title match

class CourseSearch(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.connection = None
        try:
            self.connection = mysql.connect(**SQL_LOGIN)
        except Exception as w:
            logging.error("Could not connect to MySQL database. Make sure the server is running, and that your login information is correct.")
        self.connection.database = SQL_SCHEMA
        self.cursor = self.connection.cursor()
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
        self.tips = [
            ["You can search by acronyms! Try `RCOS` or `FOCS`.", 100],
            ["You can search by abbreviations! Try `Comp Org` or `P Soft`.", 100],
            ["This bot was made in RCOS! Consider joining the class next semester.", 100],
            ["You can die from radiation poisioning by eating 10 million bananas. Try not to.", 25],
            ["We made this [video guide](https://www.youtube.com/watch?v=QX43QTYyV-8) to help new users with this bot!", 25]
        ]
    
    def __del__(self):
        if self.connection:
            self.cursor.close()
            self.connection.close()

    @commands.command(description="Search for a course in the RPI catalog.")
    async def course(self, ctx:Context, *, search_term:str):
        search_term = sanitize_str(search_term)
        if len(search_term) == 0:
            raise commands.BadArgument
        reg_start_or_space = "(^|.* )"
        regex1 = search_term # just the search itself
        
        regex2 = "("
        # for acronyms
        if len(search_term) > 1:
            regex2 += reg_start_or_space
            for char in search_term:
                # don't use spaces in acronyms
                if char != " ":
                    regex2 += f"{char}.* "
            regex2 = regex2[:-3]
        tokens = search_term.split()
        
        # for abbreviations
        if len(tokens) > 1:
            regex2 += f"|{reg_start_or_space}"
            for token in tokens:
                regex2 += f"{token}.* "
            regex2 = regex2[:-3]
        regex2 += ")"
        
        self.cursor.reset()
        self.cursor.execute(self.search_query, (search_term, regex1, regex2))
        
        # default embed is "no matches", it will only be changed if there is a match
        return_embed = discord.Embed(
            color = 0xC80000,
            title = "No Matches",
            description = "Try searching for something else."
        )
        return_embed.add_field(
            name = "Tip:",
            value = get_random_tip(self)
        )

        field_names = ["", "", "", "", "Offered", "", "Credits", "Prereq/Coreq", "Colisted", "Crosslisted", "Contact/Lecture/Lab Hours"]

        similar_matches = ""

        for row_num, row in enumerate(self.cursor):
            if row_num == 0:
                return_embed = discord.Embed(
                    color = 0xff00ff,
                    title = f"{row[0]} {row[1]}: {row[2]}",
                    description = row[3],
                    url = row[5]
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
    async def course_search_error(self, ctx:Context, error):
        embed_desc = None
        print(type(error))
        if isinstance(error, commands.CommandInvokeError):
            error = error.original
        if isinstance(error, commands.MissingRequiredArgument):
            embed_desc = f"Usage: `{COMMAND_PREFIX}course [search term]`"
        elif isinstance(error, commands.BadArgument):
            embed_desc = f"Your input is invalid! Try something else."
        if embed_desc != None:
            embed_var = discord.Embed(
                title = ERROR_TITLE,
                description = embed_desc,
                color = 0xC80000
            )
            await ctx.send(embed=embed_var)
        else:
            await sendUnknownError(ctx, error)
    
async def setup(bot):
    await bot.add_cog(CourseSearch(bot))