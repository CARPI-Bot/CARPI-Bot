import discord
from discord.ext import commands
from globals import *
import aiohttp
import asyncio
import typing
import datetime
import requests
import re

"""
Compiler Explorer API Documentation: https://github.com/compiler-explorer/compiler-explorer/blob/main/docs/API.md
"""

GET_COMPILERS_URL = "https://godbolt.org/api/compilers/" # Returns compilers; Filtered if language ID is provided

GET_LANGUAGES_URL = "https://godbolt.org/api/languages/" # Returns languages
GET_FORMATS_URL = "https://godbolt.org/api/formats/"     # Returns code formats

POST_COMPILE_URL = "https://godbolt.org/api/compiler/"   # Requires data JSON
POST_FORMAT_URL = "https://godbolt.org/api/format/"      # Requires data JSON
POST_LINK_URL = "https://godbolt.org/api/shortener/"     # Requires data JSON

async def languageNotAvaliableError(ctx:commands.Context, error:commands.errors, color:int=0xC80000):
    embedVar = discord.Embed(
        title=ERROR_TITLE,
        description="Language not avaliable.",
        color=color
    )

    await ctx.send(embed=embedVar)

class Compiler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # List of all languages respective to their compilers
        # Compilers are retrieved from the API: "https://godbolt.org/api/compilers/<language>"
        self.compilers = {
            "python": ("python310", "Python 3.10"),
            "c++": ("g95", "x86-64 gcc 9.5"),
            "cpp": ("g95", "x86-64 gcc 9.5"),
            "c": ("g95", "x86-64 gcc 9.5")
        }

        # An embed that is sent with the command is called without any arguments
        self.help_embed = discord.Embed(
                title="Compiler",
                description=f"Compiles source code with a given language",
                color=discord.Color.light_embed(),
                timestamp=datetime.datetime.now(),
        )

        self.help_embed.add_field(
            name="Languages",
            value="First specify a language. The avaliable languages are: \n`{}`".format(
                  "` `".join(self.compilers.keys())),
            inline=False
        )

        self.help_embed.add_field(
            name="Source Formatting",
            value="Second, include the code you want the bot to run.\n\n\
                   For single lines, you want to surround your code with either \` or \`\` characters.\n\
                   ***{}compile python*** `print('Hello, world!')`\n\n\
                   For multi line code, you want to surround your code in \`\`\` characters.\n\
                   ***{}compile c++***\
                   ```#include <iostream>\n\nint main() {{\n    std::cout << \"Hello, world!\\n\";\n    return 0;\n}}```".format(
                   COMMAND_PREFIX, COMMAND_PREFIX),
            inline=False
        )

    async def get_compile_data(self, session, language: str, source: str):
        compile_data = {
            "source": source,
            "compiler": self.compilers[language][0],
            "options": {
                "userArguments": "",
                "executeParameters": {
                    "args": [],
                    "stdin": "0"
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

        compile_output = None
        async with session.post(
                url = POST_COMPILE_URL + compile_data["compiler"] + "/compile",
                headers = {"Accept": "application/json"},
                json = compile_data
            ) as response:

            compile_output = await response.json()

        return compile_data, compile_output

    async def get_link_data(self, session, compile_data):
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

        link_output = None
        async with session.post(
                url = POST_LINK_URL,
                headers = {"Accept": "application/json"},
                json = link_data
            ) as response:

            link_output = await response.json()

        return link_output

    ### COMPILE ###
    @commands.hybrid_command(description="Compiles source code with a given language")
    async def compile(self, ctx: commands.Context, language, *, source):
        if not language:
            raise commands.MissingRequiredArgument
        elif (not language and source) or (language and not source):
            raise commands.BadArgument
        if language not in self.compilers.keys():
            raise commands.UserInputError

        source = source.replace("`", "")

        async with aiohttp.ClientSession() as session:
            compile_data, compile_output = await self.get_compile_data(session, language, source)
            link_output = await self.get_link_data(session, compile_data)

        out = ""
        color = discord.Color.light_embed()

        # If the program produces an error, print that instead of the output
        if compile_output["stderr"]:
            color = discord.Color.red()
            for text in compile_output["stderr"]:
                out += "\n" + text["text"]

            # (For C & CPP compiles; removes all console characters using regex compile)
            if "buildResult" in compile_output:
                out += "\n"
                for text in compile_output["buildResult"]["stderr"]:
                    out += re.compile(r"(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]").sub("", "\n" + text["text"])

        elif compile_output["stdout"]:
            for text in compile_output["stdout"]:
                out += "\n" + text["text"]

        out += " "
        returned = compile_output["code"]
        embed = discord.Embed(
            title="Program Output",
            description=f"```{out}```",
            color=color,
            timestamp=datetime.datetime.now(),
        )
        embed.add_field(name="Program Returned", value=returned, inline=False)
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
    async def compile_error(self, ctx: commands.Context, error: commands.errors):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(embed=self.help_embed)
        elif isinstance(error, commands.UserInputError):
            await languageNotAvaliableError(ctx, error)
        else:
            await sendUnknownError(ctx)

async def setup(bot):
    await bot.add_cog(Compiler(bot))
