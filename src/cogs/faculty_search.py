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
        if general_info[0] == "Faculty Not Found":
            await ctx.send(general_info[0])
        else:
            for info in general_info:
                await ctx.send(info)
        
            await ctx.send(about_info)

            for pub in publication_list:
                await ctx.send(pub)

    @faculty_search.error
    async def faculty_search_error(self, ctx, error):
        await ctx.send(str(error))     

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
        print(print_elements[0])
        if print_elements[0] == None:
            general_info.append("Faculty Not Found")
            return general_info
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
        container2 = scrape.find('div', class_="clearfix text-formatted field field--name-field-bio field--type-text-long field--label-hidden field__item")
        truncated_paragraph = ""
        if container2 == None:
            return "There is no about section for this faculty member."
        else:
            sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', (container2.get_text().strip()))
            if len(sentences) > 4:
                truncated_paragraph = ' '.join(sentences[:3])
                return (truncated_paragraph)
            else:
                return (container2.get_text().strip())
                
    def publications(self,link,headers): 
        html = requests.get(link,headers = headers)
        scrape = BeautifulSoup(html.content, 'html5lib')
        publications = scrape.find_all("div", class_="faculty-doc")
        publication_list = []
        for pub in publications:
            if "©" in pub:
                publication_list += ("No publications to date")
                return publication_list
            else:
                stripped_string = (pub.get_text().strip())
                cleaned_string = re.sub('\s+', ' ', stripped_string)
                publication_list.append(cleaned_string)
        return publication_list
    
async def setup(bot):
    await bot.add_cog(FacultySearch(bot))