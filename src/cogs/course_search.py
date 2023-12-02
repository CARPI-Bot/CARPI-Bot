import discord
from discord.ext import commands
import mysql.connector as mysql
import re
from globals import ERROR_TITLE, COMMAND_PREFIX, sendUnknownError

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
        self.connection = mysql.connect(
            host = "localhost",
            user = "root",
            password = "carpibot"
        )
        self.connection.database = "course_data"
        self.cursor = self.connection.cursor()
        self.search_query = """
            SELECT
                dept,
                `code`,
                `name`,
                REGEXP_LIKE(CONCAT(dept, " ", `code`), %s, 'i') AS code_match,
                REGEXP_LIKE(`name`, %s, 'i') AS title_match,
                REGEXP_LIKE(`name`, %s, 'i') AS title_similar
            FROM
                courses
            HAVING
                title_match > 0
                OR title_similar > 0
                OR code_match > 0
            ORDER BY
                code_match DESC, title_match DESC, title_similar DESC
            LIMIT 20
        """
    
    def __del__(self):
        self.cursor.close()
        self.connection.close()

    @commands.command(description="Search for a course in the RPI catalog.")
    async def course(self, ctx:Context, *, search_term:str):
        search_term = sanitize_str(search_term)
        print(len(search_term))
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
        for db in self.cursor:
            # dept and code match
            if db[3] == 1:
                print("\033[93m", f"{db[0]} {db[1]}: {db[2]}", "\033[0m")
            # full title match
            elif db[4] == 1:
                print("\033[92m", f"{db[0]} {db[1]}: {db[2]}", "\033[0m")
            # partial title match
            elif db[5] == 1:
                print("\033[96m", f"{db[0]} {db[1]}: {db[2]}", "\033[0m")
            # just similar in description
            else:
                print(f"{db[0]} {db[1]}: {db[2]}")
            await ctx.send(f"{db[0]} {db[1]}: {db[2]}")

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