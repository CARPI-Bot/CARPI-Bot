import discord
from discord.ext import commands
import requests
from bs4 import BeautifulSoup
import re
from globals import sendUnknownError

Context = commands.Context

# Filters the user input so all non-alphanumeric characters are eliminated, except for spaces.
async def sanitize_str(input:str) -> str:
    return "".join(
    [c.lower() for c in input.strip()
        if c.isnumeric() or c.isalpha() or c == ' ']
    )

# Accesses a specific course's preview webpage and gathers data such as the course title
# and its description, given a HTTP session, URL, and headers to use in the GET request.
async def get_course_info(session:requests.Session, url:str, parser:str, headers:dict) -> dict:
    info = dict()
    course_response = session.get(
        url = url,
        headers = headers
    )
    if course_response.status_code != 200:
        raise 1
    course_soup = BeautifulSoup(course_response.content, parser)
    # Gets the header containing the course's name
    header = course_soup.find("h1", id="course_preview_title")
    info["title"] = header.string
    # Start searching for the course description following the course title header
    elements = list(header.next_siblings)
    course_desc = ""
    # Gathers all text between the first <hr> and <br> tag after the header
    for i in range(len(elements)):
        if elements[i].name == "hr":
            for j in range(i + 1, len(elements)):
                if elements[j].name == "br":
                    break
                text = elements[j].string
                course_desc += text.strip() if text != None else ""
            break
    info["description"] = course_desc
    return info

class CourseSearch(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot    

    @commands.command(description="Search for a course in the RPI catalog.")
    async def course(self, ctx:Context, *, search_term:str):
        PARSER = "html5lib"
        DOMAIN = "https://catalog.rpi.edu/"
        SEARCH_HREF = "search_advanced.php?"
        search_term = await sanitize_str(search_term)
        if len(search_term) == 0:
            raise commands.MissingRequiredArgument
        search_params = {
            # "cur_cat_oid": 26,
            "search_database": "Search",
            "filter[keyword]": search_term,
            "filter[exact_match]": 1,
            "filter[3]": 1,
            "filter[31]": 1
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " +
                        "(KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.46"
        }

        embed_var = discord.Embed(color=0xC80000)

        # Creates a HTTP session
        session = requests.Session()
        # Submits a search query with the specified search term and appropriate filters
        search_response = session.get(
            url = f"{DOMAIN}{SEARCH_HREF}",
            params = search_params,
            headers = headers
        )
        if search_response.status_code != 200:
            raise 1
        search_soup = BeautifulSoup(search_response.content, PARSER)

        # Returns all anchor elements that links to a course info preview
        anchors = search_soup.find_all("a", href=re.compile("preview_course.+coid=.+"))
        # NOTE: Anchors is sometimes empty, even though the HTTP response is always successful
        if len(anchors) == 0:
            raise 2

        # If no exact match is found, just display a list of other results
        title = "Possible Matches"
        description = "No prefix/code matches, but maybe you're looking for one of these courses?"
        # Checks if a best match was found, displays the course info if so
        # NOTE: Sometimes, no best match is found, yet the desired course still comes up
        # NOTE: Rarely, no "best match" is found but the desired course pops up twice
        if "Best Match" in anchors[0].get_text():
            # After popping twice, anchors is a list of follow-up course links
            top_anchor = anchors.pop(0)
            # NOTE: Sometimes, only a best match and no follow-up results are found
            if len(anchors) > 0:
                anchors.pop(0)
            try:
                info = await get_course_info(
                    session = session,
                    url = f"{DOMAIN}{top_anchor['href']}",
                    parser = PARSER,
                    headers = headers
                )
            except:
                raise 1
            title = info["title"]
            description = info["description"]
        
        embed_var.title = title
        embed_var.description = description
        # Prints a list of results whether or not a best match was found
        if len(anchors) > 0:
            related_courses = "\n".join([f"[{anchor.string}]({DOMAIN}{anchor['href']})" for anchor in anchors[:5]])
            embed_var.add_field(
                name = "Related courses:",
                value = related_courses
            )
        
        await ctx.send(embed=embed_var)

    @course.error
    async def course_search_error(self, ctx:Context, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed_var = discord.Embed(
                title = "Missing Required Argument",
                color = 0xC80000
            )
            await ctx.send(embed=embed_var)
        elif isinstance(error, commands.BadArgument):
            embed_var = discord.Embed(
                title = "Bad Argument",
                color = 0xC80000
            )
            await ctx.send(embed=embed_var)
        elif isinstance(error, int):
            embed_var = discord.Embed(
                description = "This is likely an issue with RPI's servers, but we're making a workaround to that!",
                color = 0xC80000
            )
            match error:
                case 1:
                    embed_var.title = "Error receiving a response"
                case 2:
                    embed_var.title = "No search results found"
            await ctx.send(embed=embed_var)
        else:
            await sendUnknownError(ctx, error)
    
async def setup(bot):
    await bot.add_cog(CourseSearch(bot))