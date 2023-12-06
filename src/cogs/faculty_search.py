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
        
        #Obtains all the data from functions below. 
        general_info = self.general(link,headers)
        about_info = self.about(link,headers)
        image = self.image(link,headers)
        publication_list = self.publications(link,headers)

        #Declaration of embed
        embed_var = discord.Embed(
        title = general_info[0],
        color = 0, # usually a hex value
        url = None,
        timestamp = None # usually a datetime object
        )

        #Conditional for if the faculty member does not exist.
        if general_info[0] == "Faculty Not Found":
            embed_var.add_field(
            name = "Error",
            value = general_info[0],
            inline = True # defaults to true if not specified
            )            
        else:
            embed_var.add_field(
                name="General Information",
                value= "Department: " + general_info[1] + "\nRoom: " + general_info[2] + "\nEmail: " + general_info[3] + "\nWebsite: " + general_info[4],
                inline=True
            )
            embed_var.add_field(
                name="About",
                value=about_info,
                inline=False
            )        
        if len(publication_list) >= 2:
            embed_var.add_field(
                name="Publication List",
                value=publication_list[0] + "\n\n" + publication_list[1],
                inline=False
            )
        elif len(publication_list) >= 1:
            embed_var.add_field(
                name="Publication List",
                value=publication_list[0],
                inline=False
            )
        embed_var.add_field(
            name="Profile Picture",
            value="",
            inline=False
            )
        embed_var.set_image(
            url=image
        )
        await ctx.send(embed=embed_var)           

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
        
    def image(self,link,headers):
        html = requests.get(link,headers = headers)
        scrape = BeautifulSoup(html.content, 'html5lib')
        img = scrape.find_all("img")
        img_link = img[1]
        part = str(img_link)

        start_index = part.find('src="')

        # If 'src="' is found, find the end of the attribute value
        if start_index != -1:
            end_index = part.find('"', start_index + 5)
    
        # Extract the attribute value
            if end_index != -1:
                extracted_line = part[start_index + 5:end_index]

        half1 = "https://faculty.rpi.edu"
        image_link = half1+extracted_line
        return image_link


    #Scrapes about section of a faculty page. 
    def about(self,link,headers): 
        html = requests.get(link,headers = headers)
        scrape = BeautifulSoup(html.content, 'html5lib')
        container2 = scrape.find('div', class_="clearfix text-formatted field field--name-field-bio field--type-text-long field--label-hidden field__item")
        truncated_paragraph = ""
        if container2 == None:
            return "There is no about section for this faculty member."
        else:
            #Simple splitting the paragraph properly into sentences, limiting the about section to 3 sentences max. 
            sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', (container2.get_text().strip()))
            if len(sentences) > 4:
                truncated_paragraph = ' '.join(sentences[:3])
                return (truncated_paragraph)
            else:
                return (container2.get_text().strip())
            
    #Scrapes all of the publications of the faculty page. 
    def publications(self,link,headers): 
        html = requests.get(link,headers = headers)
        scrape = BeautifulSoup(html.content, 'html5lib')
        publications = scrape.find_all("div", class_="faculty-doc")
        publication_list = []
        for pub in publications:
            if "Â©" in pub:
                publication_list += ("No publications to date")
                return publication_list
            else:
                stripped_string = (pub.get_text().strip())
                cleaned_string = re.sub('\s+', ' ', stripped_string)
                publication_list.append(cleaned_string)
        return publication_list
    
async def setup(bot):
    await bot.add_cog(FacultySearch(bot))