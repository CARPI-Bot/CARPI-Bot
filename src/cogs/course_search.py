import discord
from discord.ext import commands
import asyncio

# for webscraping
import requests
from bs4 import BeautifulSoup
import re
#checks if each character in str is a letter, num, or a space
def isnumalpha(c:str) -> bool:
        if (ord(c) >= 97 and ord(c) <= 122) or (ord(c) >= 48 and ord(c) <= 57 ) or ord(c) == 32:
            return True
        return False

def get_info(course, Header) -> str:
    link = f"https://catalog.rpi.edu/{course}"
    r = requests.get(link, Header)
    soup = BeautifulSoup(r.content, 'html.parser')
    text = soup.find_all('p')
    return text

def get_title(course, Headers) -> str:
    link = f"https://catalog.rpi.edu/{course}"
    r = requests.get(link, Headers)
    soup = BeautifulSoup(r.content, 'html.parser')
    title = soup.find('h1', id='course_preview_title')
    return f'[{title.get_text()}]({link})'


class course_search(commands.Cog):
    def __init__(self, bot):
        self.bot = bot    

    @commands.command(description = 'Searches for courses in course catalog')
    async def course_search(self, ctx, *, arg):
        arg = "".join([c for c in arg if isnumalpha(c.lower())])
        url = f"https://catalog.rpi.edu/search_advanced.php?cur_cat_oid=26&search_database=\
            Search&search_db=Search&cpage=1&ecpage=1&ppage=1&spage=1&tpage=1&location=33\
                &filter%5Bkeyword%5D={arg}&filter%5Bexact_match%5D=1"
        Headers = ({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
                (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36', 'Accept-Language': 'en-US, en;q=0.5'})
                

        # get html content from the website
        r = requests.get(url, headers = Headers)
        soup = BeautifulSoup(r.content, 'html.parser')
        links = soup('a', href=re.compile("preview_course"))

        # checks if user input has a search. if not tell them to try again
        if len(links) == 0:
            await ctx.send(f"There is no information on {arg}")
            return
        
        #first result of searches
        best_result_title = get_title(links[0]['href'], Headers)
        await ctx.send(f"Search results for {best_result_title}")
        best_text = get_info(links[0]['href'], Headers)
        for i in range(4, len(best_text)):
            await ctx.send(best_text[i].get_text())
                    
        if len(links) == 1:
            return
        #list of intersted links user may want
        await ctx.send('Related courses that may interest you\n')
        if len(links)-1 >= 4:
            for i in range(1,5):
                await ctx.send(get_title(links[i]['href'], Headers))
        else:
            for i in range(1,range(len(links))):
                await ctx.send(get_title(links[i]['href'], Headers))
        

    @course_search.error
    async def course_search_error(self, ctx, error):
        await ctx.send(str(error))
    
async def setup(bot):
    await bot.add_cog(course_search(bot))