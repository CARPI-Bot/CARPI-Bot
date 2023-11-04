import discord
from discord.ext import commands
import asyncio
from bs4 import BeautifulSoup
import requests
import re



class faculty_search(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    def general(self,facul_name):
        link = ("https://faculty.rpi.edu/")
        link += facul_name

        headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.46", 
                "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"}
        
        html = requests.get(link,headers = headers)
        scrape = BeautifulSoup(html.content, 'html5lib')
        scraped_container1 = scrape.find(id="content")
        faculty_name = scraped_container1.find("h1", class_="page-title")
        department_name = scraped_container1.find('a', hreflang = 'en')
        email = scraped_container1.find('a', href=re.compile('mailto'))
        website = scraped_container1.find('a', href=re.compile('http://'))
        room = scrape.find("div", class_="field field--name-field-location field--type-string field--label-hidden field__item") 
    
        print_elements = [faculty_name,department_name,room,email,website]
        return_list = []
        for element in print_elements:
            if element == None:
                return_list += "N/A\n".strip()
            else:
                return_list += ((element.get_text().strip()) + "\n").strip()


    def about(self,facul_name):

        link = ("https://faculty.rpi.edu/")
        link += facul_name

        headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.46", 
                "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"}
        
        html = requests.get(link,headers = headers)
        scrape = BeautifulSoup(html.content, 'html5lib')


        container2 = scrape.find_all('p')
        return_list = []
        for element in container2:
            if element == None:
                return_list += "N/A\n".strip()
            else:
                return_list += ((element.get_text().strip()) + "\n").strip()

        return return_list
                
    def publications(self,facul_name):
        
        link = ("https://faculty.rpi.edu/")
        link += facul_name

        headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.46", 
                "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"}
        
        html = requests.get(link,headers = headers)
        scrape = BeautifulSoup(html.content, 'html5lib')


        publications = scrape.find_all("div", class_="faculty-doc")
        return_list = []
        for pub in publications:
            if "©" in pub:
                return_list += ("N/A").strip()
                return return_list
            else:
                return_list += pub.get_text().rstrip()
        return return_list

    def print(self,facul_name):
        name = facul_name
        name = name.replace(" ","-").lower()

        
        if name == "brian clyne":
            name += "-0"

        output = []
        output += faculty_search.general()
        output += faculty_search.about()
        output += faculty_search.publications()
        
        return output

async def setup(bot):
    await bot.add_cog(faculty_search(bot))