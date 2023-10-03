import discord
from discord.ext import commands
import asyncio

# for webscraping
import requests
from bs4 import BeautifulSoup
#checks if each character in str is a letter, num, or a space
def isnumalpha(c:str) -> bool:
        if (ord(c) >= 97 and ord(c) <= 122) or (ord(c) >= 48 and ord(c) <= 57 ) or ord(c) == 32:
            return True
        return False

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
        # all_a = soup.find_all('a')
        all_a = soup.find_all(['td', 'a'], class_ = "td_dark", attrs={'href'})
        # all_a = soup.find_all('a', 'strong')
        # print(all_a)
        # preview_course = ''
        for a in all_a:
            print(a)
        # print(preview_course)
        # sorting_type = soup.find('input', attrs = {'id' : "sorting_type"}).find('href')
        # print(sorting_type)
        await ctx.send("Search results for [{}]({})".format(arg, r.url))
        await ctx.send(soup.title.text)

    @course_search.error
    async def course_search_error(self, ctx, error):
        await ctx.send(str(error))
    
async def setup(bot):
    await bot.add_cog(course_search(bot))