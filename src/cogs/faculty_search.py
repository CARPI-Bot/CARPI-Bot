import discord
from discord.ext import commands
import asyncio
from bs4 import BeautifulSoup
import requests
import re



class fac_search(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    async def faculty_search(self,facul_mem:str,ctx):
        await facul_mem
        name = facul_mem
        name = name.replace(" ","-").lower()

        
        if name == "brian clyne":
            name += "-0"

        link = ("https://faculty.rpi.edu/")
        link += name

        headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.46", 
                "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"}


        html = requests.get(link,headers = headers)
        scrape = BeautifulSoup(html.content, 'html5lib')
        scraped_container1 = scrape.find(id="content")

        faculty_name = scraped_container1.find("h1", class_="page-title")
        department_name = scraped_container1.find('a', hreflang = 'en')
        email = scraped_container1.find('a', href=re.compile('mailto'))
        website = scraped_container1.find('a', href=re.compile('http://'))
        container2 = scrape.find_all('p')
        publications = scrape.find_all("div", class_="faculty-doc")
        room = scrape.find("div", class_="field field--name-field-location field--type-string field--label-hidden field__item")

        print_elements = [faculty_name,department_name,room,email,website]


        if faculty_name == None:
            print("There is no faculty member with inputed name")
        else:
            output = ""
            for element in print_elements:
                if(element == None):
                    output += ("N/A\n").strip()
                else:
                    output += ((element.get_text().strip()) + "\n")
            for pub in publications:
                if "©" in pub:
                    output += ("N/A").strip()
                    break
                else:
                    publication = pub.get_text().rstrip()
                    output += (publication)
        await ctx.send(output)


async def setup(bot):
        await bot.add_cog(fac_search(bot))