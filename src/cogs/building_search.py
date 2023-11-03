import discord
from discord.ext import commands
import asyncio

#for webscraping
import requests 
from bs4 import BeautifulSoup

class building_search(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    '''
    get_description takes in each building name and the overall 
    scrapped website and returns the blurb of description information 
    for every building.
    '''
    async def get_description(self, building_name, soup):
        #finds all HTML <div> elements that have a "class" attribute with the value "field-content", 
        info = soup.find_all("div", {"class": "field-content"})
        for building_info in info:
            #gets the name of the buildings that are associated with h2 tag
            curr_building_name = building_info.find("h2").text
            #checks if the building names in both are the same
            if curr_building_name.lower() in (building_name).lower():
                #gets the actual description
                blurbs = building_info.find("div", {"class": "grid-6"})
                #check if blurbs is empty
                if blurbs is not None:
                    #find all paragraph
                    paragraphs = blurbs.find_all('p')
                    blurb = ""
                    for i, paragraph in enumerate(paragraphs):
                        #check if paragraph is empty
                        if paragraph.text.strip():
                            blurb += paragraph.text
                            #checks if the description of the building is more than one paragraph
                            if i < len(paragraphs) - 1:
                                blurb += '\n\n'
                    return blurb
        return 'No description'
        

    @commands.command (description = 'Searches for buildings in buildings list')
    async def building_search(self, ctx, *, arg):
        URL = "https://info.rpi.edu/map"
        Headers = ({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
                (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36', 'Accept-Language': 'en-US, en;q=0.5'})
        page = requests.get(URL, headers = Headers)
        soup = BeautifulSoup(page.content, 'html.parser')

        embedMsg = discord.Embed(title = f"Search Reuslts for **{arg}**",
                                 color = 0x9B27E6) 
        message = ""

        search_found = False
        #long lat building
        buildings = soup.find_all("a", {"class": "rpi-poi"})
        for building in buildings:
            building_name = building.text
            if arg.lower() in (building.text).lower():
                search_found = True
                lat = building["data-lat"]
                lon = building["data-lng"]
                building_description = await self.get_description(building_name, soup)
                google_map_link = f"https://www.google.com/maps/search/?api=1&query={lat}%2C{lon}"
                embedDescription = embedMsg.add_field(name = f"**{building_name}**",
                                   value = f"```{building_description}```",
                                   inline = True)
                embedMsg.add_field(name = "Link", value = f"[Click for directions to {building_name}](<{google_map_link}>)", inline = True)
                # message += f"### {building_name}\n[Click for directions to {building_name}](<{google_map_link}>)\n```{description}```"

                # await ctx.send(f"### {building_name}\n[Click for directions to {building_name}](<{google_map_link}>)\n```{description}```")
        if(not search_found):
            message = f"**{arg}** not found"
            # await ctx.send(f"**{arg}** not found")
            
        await ctx.send(embed=embedMsg)

    @building_search.error
    async def building_search_error(self, ctx, error):
        await ctx.send(str(error))


async def setup(bot):
    await bot.add_cog(building_search(bot))
    



