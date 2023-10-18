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

#takes in a str type link and outputs information about given course
def get_info(course, Header) -> str:
    link = f"https://catalog.rpi.edu/{course}"
    r = requests.get(link, Header)
    soup = BeautifulSoup(r.content, 'html.parser')
    texts = soup.find_all('p')
    #blurb about the course itself
    information = texts[4].hr.next_sibling.get_text()

    # #whether it is a prereq or a coreq and provide the link along with the req
    # prereq = texts[4].strong.next_sibling.get_text()
    # prereq_course = texts[4].a.get_text() #prereq/coreq course name

    # #when it is offered
    # time_offered = texts[4].span.find_next('strong').next_sibling.get_text()
    # #number of credit hours given and lab hours
    # credit_hours = texts[4].find_all('em')[1]
    # lab_hours = credit_hours.find_next('strong').next_sibling.get_text()
    
    
    # print_text = f"{information}\n\
    #                {prereq} {prereq_course}\n\
    #                When Offered: {time_offered}\n\
    #                Credit Hours: {credit_hours.get_text()}\n\
    #                Contact, Lecture or Lab Hours: {lab_hours}"
    return information

def get_title(course, Headers) -> str:
    link = f"https://catalog.rpi.edu/{course}"
    r = requests.get(link, Headers)
    soup = BeautifulSoup(r.content, 'html.parser')
    title = soup.find('h1', id='course_preview_title')
    return title.get_text()


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
                
        embedVar = discord.Embed(
            title = '',
            description='',
            color = 0x07CEFD
        )
        # get html content from the website
        r = requests.get(url, headers = Headers)
        soup = BeautifulSoup(r.content, 'html.parser')
        links = soup('a', href=re.compile("preview_course"))

        # checks if user input has a search. if not tell them to try again
        if len(links) == 0: 
            embedVar.title = f"Search results for {arg}"
            embedVar.description=f"There is no information on {arg}"
            await ctx.send(embed = embedVar)
            return
        
        #first result of searches
        best_result_title = get_title(links[0]['href'], Headers)
        best_result = get_info(links[0]['href'], Headers)            
        if len(links) == 1:            
            embedVar.title = best_result_title
            embedVar.url = f"https://catalog.rpi.edu/{links[0]['href']}"
            embedVar.description=best_result
            await ctx.send(embed = embedVar)
            return
        #list of intersted links user may want
        embedVar.add_field(
            name = 'Related courses that may interest you',
            value = '',
            inline = False
            )
        if len(links)-1 >= 4:
            for i in range(1,5):
                related_title = get_title(links[i]['href'], Headers)
                link = f"https://catalog.rpi.edu/{links[i]['href']}"
                embedVar.add_field(
                    name = '',
                    value = f"[{related_title}]({link})",
                    inline = False
                )
                # await ctx.send(get_title(links[i]['href'], Headers))
        else:
            for i in range(1,range(len(links))):
                related_title = get_title(links[i]['href'], Headers)
                link = f"https://catalog.rpi.edu/{links[i]['href']}"
                embedVar.add_field(
                    name = '',
                    value = f"[{related_title}]({link})",
                    inline = True
                )
        embedVar.title = best_result_title
        embedVar.url = f"https://catalog.rpi.edu/{links[0]['href']}"
        embedVar.description = best_result
        await ctx.send(embed = embedVar)

    @course_search.error
    async def course_search_error(self, ctx, error):
        embedVar = discord.Embed(
            description=str(error)
        )
        await ctx.send(embed = embedVar)
    
async def setup(bot):
    await bot.add_cog(course_search(bot))