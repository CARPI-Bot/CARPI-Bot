import discord
from discord.ext import commands
import mysql.connector as mysql
import re
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
            LIMIT 20
        """
    
    def __del__(self):
        self.cursor.close()
        self.connection.close()

    @commands.command(description="Search for a course in the RPI catalog.")
    async def course(self, ctx:Context, *, search_term:str):
        search_term = sanitize_str(search_term)
        if len(search_term) == 0:
            raise commands.MissingRequiredArgument
        reg_start_or_space = "(^|.* )"
        regex1 = f".*{search_term}.*" # just the search itself
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
        self.cursor.execute(self.search_query, (search_term, regex1, regex2))
        return_string = ""
        for row_num, row in enumerate(self.cursor):
            if (row_num == 0):
                return_string += f"{row[0]} {row[1]}: {row[2]}\n{row[3]}\n{row[4]}\n{row[5]}\nCredits: {row[6]}\n{row[7]}\n{row[8]}\n{row[9]}\n{row[10]}\n"
            elif (row_num == 1):
                return_string += "Other results: \n"
                return_string += f"{row[0]} {row[1]}: {row[2]}\n"
            else:
                return_string += f"{row[0]} {row[1]}: {row[2]}\n"
            # dept and code match: db[11] == 1:
            # full title match: db[12] == 1:
            # partial title match: db[13] == 1:
        await ctx.send(return_string.strip("\n"))

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