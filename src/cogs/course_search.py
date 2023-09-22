import discord
from discord.ext import commands

class course_search(commands.Cog):
    def __init__(bot):
        self.bot = bot

    def isnumalpha(c:str) -> bool:
        # checks if c is a nubmer or a letter
        if (ord(c) >= 97 and ord(c) <= 122) or (ord(c) >= 48 and ord(c) <= 57 ) or ord(c) == 32:
            return True
        return False

    @commands.command(description = 'Searches for courses in course catalog')
    async def course_search(self, *, ctx):
        arg = "".join([c for c in arg if isnumalpha(c.lower())])
        url = f"https://catalog.rpi.edu/search_advanced.php?cur_cat_oid=26&search_database=\
            Search&search_db=Search&cpage=1&ecpage=1&ppage=1&spage=1&tpage=1&location=33\
                &filter%5Bkeyword%5D={arg}&filter%5Bexact_match%5D=1"
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
    
async def setup(bot):
    bot.add_cog(course_search(bot))