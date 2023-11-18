import discord
from discord.ext import commands
import asyncio
from bs4 import BeautifulSoup
import requests
import re



class FacultySearch(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Get name of faculty")
    async def faculty_search(self, ctx, *args):
        name = "-".join(args)
        name = name.lower()
        
        if name == "brian-clyne":
            name += "-0"
        link = ("https://faculty.rpi.edu/")
        link += name

        headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.46", 
                "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"}

        general_info = self.general(link,headers)
        about_info = self.about(link,headers)
        publication_list = self.publications(link,headers)
        for info in general_info:
            await ctx.send(info)
        for info in about_info:
            await ctx.send(info)
        for pub in publication_list:
            await ctx.send(pub)

    # @faculty_search.error
    # async def faculty_error(self, ctx:Context, error):
    #     await sendUnknownError(ctx, error)        

    def general(self,link,headers):  

        html = requests.get(link,headers = headers)
        scrape = BeautifulSoup(html.content, 'html5lib')
        scraped_container1 = scrape.find(id="content")
        faculty_name = scraped_container1.find("h1", class_="page-title")
        department_name = scraped_container1.find('a', hreflang = 'en')
        email = scraped_container1.find('a', href=re.compile('mailto'))
        website = scraped_container1.find('a', href=re.compile('http://'))
        room = scrape.find("div", class_="field field--name-field-location field--type-string field--label-hidden field__item") 
    
        print_elements = [faculty_name,department_name,room,email,website]
        general_info = []
        if print_elements[0] == None:
            return "Faculty Not Found"
        else:
            for element in print_elements:
                if element == None:
                    general_info.append("N/A\n".strip())
                else:
                    general_info.append(((element.get_text().strip()) + "\n").strip())
            return general_info


    def about(self,link,headers):  
        html = requests.get(link,headers = headers)
        scrape = BeautifulSoup(html.content, 'html5lib')
        container2 = scrape.find_all('p')
        about_info = []
        for element in container2:
            if element == None:
                about_info += "N/A\n".strip()
            else:
                about_info += ((element.get_text().strip()) + "\n").strip()
        return about_info
                
    def publications(self,link,headers): 
        html = requests.get(link,headers = headers)
        scrape = BeautifulSoup(html.content, 'html5lib')
        publications = scrape.find_all("div", class_="faculty-doc")
        publication_list = []
        for pub in publications:
            if "©" in pub:
                return "No publications to date"
            else:
                publication_list += pub.get_text().rstrip()
        return publication_list
    
async def setup(bot):
    await bot.add_cog(FacultySearch(bot))