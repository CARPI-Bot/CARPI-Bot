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

        # List of all languages respective to their compilers
        # Compilers are retrieved from the API: "https://godbolt.org/api/compilers/<language>"
        self.compilers = {
            'python': ['python310', 'Python 3.10'],
            'c++': ['g95', 'x86-64 gcc 9.5'],
            'cpp': ['g95', 'x86-64 gcc 9.5'],
            'c': ['g95', 'x86-64 gcc 9.5'],
            'java': ['java2100', 'jdk 21.0.0']
        }

    async def get_compile_data(self, language: str, source: str):
        compile_data = {
            "source": source,
            "compiler": self.compilers[language][0],
            "options": {
                "userArguments": "",
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
        return compile_data, compile_output

    async def get_link_data(self, compile_data): 
        link_data = {
            "sessions": [
                {
                    "id": 1,
                    "language": compile_data["lang"],
                    "source": compile_data["source"],
                    "compilers": [],
                    "executors": [
                        {
                        "arguments": compile_data["options"]["executeParameters"]["args"],
                        "compiler": {
                            "id": compile_data["compiler"],
                            "libs": compile_data["options"]["libraries"],
                            "options": compile_data["options"]["userArguments"]
                        },
                        "stdin": compile_data["options"]["executeParameters"]["stdin"]
                        }
                    ]
                }
            ]
        }

        link_request: requests.Response = requests.post(
            url = POST_LINK_URL,
            headers = {"Accept": "application/json"},
            json = link_data
        )

        link_output = link_request.json()
        return link_output

    @commands.hybrid_command(description="Compiles source code with a given language")
    async def compile(self, ctx: commands.Context, *, args):
        args = args.split(' ')

        if len(args) <= 1:
            raise commands.CommandError(f"Missing arguments: **source**")
        
        if args[0] not in self.compilers.keys():
            raise commands.CommandError(f"Language **{args}** not avaliable")
            
        language: str = args[0].lower().strip()

        source: str = "".join([a + " " for a in args[1:]])
        source = source.replace('`', '')

        compile_data, compile_output = await self.get_compile_data(language, source)
        link_output = await self.get_link_data(compile_data)
        
        out = ""
        color = discord.Color.light_embed()

        # If the program produces an error, print that instead of the output
        if compile_output["stderr"]:
            color = discord.Color.red()
            for text in compile_output["stderr"]:
                out += "\n" + text["text"]

            # (For C & CPP compiles; removes all console characters)
            if 'buildResult' in compile_output:
                out += '\n'
                for text in compile_output["buildResult"]["stderr"]:
                    placeholder = text["text"].replace("\x1b[01m\x1b[K", "") \
                        .replace("\x1b[m\x1b[K", "") \
                        .replace("\x1b[01;31m\x1b[K", "")

                    out += "\n" + placeholder

        elif compile_output["stdout"]:
            for text in compile_output["stdout"]:
                out += "\n" + text["text"]

        embed = discord.Embed(
            title="Program Output",
            description=f"```{out}```",
            color=color,
            timestamp=datetime.datetime.now(),
        )
        embed.set_footer(text=f"{ctx.author.nick} | {language} | {self.compilers[language][1]}")

        view = discord.ui.View()
        url_button = discord.ui.Button(
            label=f"\u200bView on godbolt.org", 
            style=discord.ButtonStyle.gray,
            url=link_output["url"]
        )

        view.add_item(url_button)

        await ctx.send(embed=embed, view=view)      

    @compile.error
    async def compile_error(self, ctx: commands.Context, error):
        embed = discord.Embed(
            title="Command Error",
            description=error,
            color=ctx.author.accent_color,
            timestamp=datetime.datetime.now()
        )

        await ctx.send(embed=embed)  
    
async def setup(bot):
    await bot.add_cog(Compiler(bot))