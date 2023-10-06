import discord
from discord.ext import commands
from globals import *
import datetime
import requests

"""
Compiler Explorer API Documentation: https://github.com/compiler-explorer/compiler-explorer/blob/main/docs/API.md
"""

GET_COMPILERS_URL = "https://godbolt.org/api/compilers/" # Returns compilers; Filtered if language ID is provided

GET_LANGUAGES_URL = "https://godbolt.org/api/languages/" # Returns languages
GET_FORMATS_URL = "https://godbolt.org/api/formats/"     # Returns code formats

POST_COMPILE_URL = "https://godbolt.org/api/compiler/"   # Requires data JSON
POST_FORMAT_URL = "https://godbolt.org/api/format/"      # Requires data JSON
POST_LINK_URL = "https://godbolt.org/api/shortener"      # Requires data JSON

class Compiler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.compilers = {
            'python': 'python310',
            'c++': 'g95'
        }

    @commands.command(description="Compiles source code with a given language")
    async def compile(self, ctx: commands.Context, *, args):
        if '```' in args:
            args = args.split('```')      
        elif '``' in args:
            args = args.split('``')
        elif '`' in args:
            args = args.split('`')

        if isinstance(args, str):
            raise commands.CommandError(f"Missing arguments")

        language: str = args[0].lower().strip()
        source: str = args[1]

        if language not in self.compilers.keys():
            raise commands.CommandError(f"Language {language} is not avaliable")

        compile_data = {
            "source": source,
            "compiler": self.compilers[language],
            "options": {
                "userArguments": "-O3",
                "executeParameters": {
                    "args": [],
                    "stdin": ""
                },
                "compilerOptions": {
                    "executorRequest": True
                },
                "filters": {
                    "execute": True
                },
                "tools": [],
                "libraries": []
            },
            "lang": language,
            "allowStoreCodeDebug": True
        }

        compile_request: requests.Response = requests.post(
            url = POST_COMPILE_URL + compile_data["compiler"] + "/compile",
            headers = {"Accept": "application/json"},
            json = compile_data
        )

        compile_output = compile_request.json()

        out = ""
        if compile_output["stderr"]:
            for text in compile_output["stderr"]:
                out += "\n" + text["text"]

        elif compile_output["stdout"]:
            for text in compile_output["stdout"]:
                out += "\n" + text["text"]

        embed = discord.Embed(
            title="Program Output",
            description=out,
            color=ctx.author.accent_color,
            timestamp=datetime.datetime.now()
        )

        await ctx.send(embed=embed)      

    @compile.error
    async def compile_error(self, ctx: commands.Context, error):
        print(error)
    
async def setup(bot):
    await bot.add_cog(Compiler(bot))