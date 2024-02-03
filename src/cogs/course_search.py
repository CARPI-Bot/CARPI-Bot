import discord
from discord.ext import commands
import mysql.connector as mysql
import re
import random
from globals import ERROR_TITLE, COMMAND_PREFIX, SQL_LOGIN, SQL_SCHEMA, sendUnknownError

Context = commands.Context

# Filters the user input so all non-alphanumeric characters are eliminated, except for spaces
def sanitize_str(input:str) -> str:
    return re.sub(
        pattern = " +",
        repl = " ",
        string = "".join(
            [c.lower() for c in input.strip() if c.isnumeric() or c.isalpha() or c == " "]
        )
    )

def get_random_tip(self) -> str:
        rand_tip = random.randint(0, self.tips[-1][1])
        for tip in self.tips:
            if rand_tip <= tip[1]:
                return tip[0]
        return "There is no tip. Have a nice day."

class CourseSearch(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.connection = mysql.connect(**SQL_LOGIN)
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
        self.tips = [ # each tip has a probability threshold to appear
            ["You can search by acronyms! Try `RCOS` or `FOCS`.", 100],
            ["You can search by abbreviations! Try `Comp Org` or `P Soft`.", 200],
            ["This bot was made in RCOS! Consider joining the class next semester.", 300],
            ["You can die from radiation poisioning by eating 10 million bananas. Try not to.", 325],
            ["We made this [video guide](https://www.youtube.com/watch?v=QX43QTYyV-8) to help new users with this bot!", 350] # the last tip has the max value for randint to generate
        ]
    
    def __del__(self):
        self.cursor.close()
        self.connection.close()

    @commands.command(description="Search for a course in the RPI catalog.")
    async def course(self, ctx:Context, *, search_term:str):
        search_term = sanitize_str(search_term)
        if len(search_term) == 0:
            raise commands.MissingRequiredArgument
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
        
        # default embed is the "no courses found", it will only be changed if there is a match
        return_embed = discord.Embed(
            color = 0xff0000,
            title = "No Matches",
            description = "Try searching for something else."
        )
        return_embed.add_field(
            name = "Tip:",
            value = get_random_tip(self)
        )

        field_names = ["", "", "", "", "Offered", "", "Credits", "Prereq/Coreq", "Colisted", "Crosslisted", "Contact/Lecture/Lab Hours"]

        related_courses = []

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
                related_courses.append(f"{row[0]} {row[1]}: {row[2]}\n")
        if len(related_courses) > 0:
            rel_cor_str = ""
            for course in related_courses:
                rel_cor_str += course
            return_embed.add_field(
                name = "Related Courses",
                value = rel_cor_str.strip('\n')
            )
        await ctx.send(embed = return_embed)

    @course.error
    async def course_search_error(self, ctx:Context, error):
        embed_desc = None
        if isinstance(error, commands.MissingRequiredArgument):
            embed_desc = f"Usage: `{COMMAND_PREFIX}course [search term]`"
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