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
                                
                    if(blurb == ""):
                        break
                    return blurb
        return 'No description'
        
    #discord user interface of the information on each building
    @commands.command (description = 'Searches for buildings in buildings list')
    async def building_search(self, ctx, *, arg):
        #the website to scrap each building and the corresponding building info 
        URL = "https://info.rpi.edu/map"
        Headers = ({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
                (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36', 'Accept-Language': 'en-US, en;q=0.5'})
        page = requests.get(URL, headers = Headers)
        soup = BeautifulSoup(page.content, 'html.parser')

        #the opening and closing times to parse from the pub safe card access website
        card_access_times_link = f"https://publicsafety.rpi.edu/campus-security/card-access-schedule"
        page2 = requests.get(card_access_times_link, headers = Headers)
        soup2 = BeautifulSoup(page2.content, 'html.parser')

        #information on Union specifically
        union_link = f"https://union.rpi.edu/business-and-service-directory/"
        page3 = requests.get(union_link, headers = Headers)
        soup3 = BeautifulSoup(page3.content, 'html.parser')
        

        #discord embeded message that has the header title for the output and the color of the block strip of info
        embedMsg = discord.Embed(title = f"Search Reuslts for **{arg}**",
                                 color = 0x9B27E6) 

        search_found = False
        #long lat building
        buildings = soup.find_all("a", {"class": "rpi-poi"})

        building_to_access = soup2.find_all("tr")
        #print("times: ", building_to_access)
        #loops through the buildings relating to the html scrapping above
        for building in buildings:
            building_name = building.text
        
            #to compare the argument with the building name all in lowercase for correct comparison
            if (arg.lower() in building_name.lower()):
                search_found = True
                lat = building["data-lat"]
                lon = building["data-lng"]
                building_description = await self.get_description(building_name, soup)
                #works on now scrapping the google maps link for the long and lat provided by the first website scrap
                google_map_link = f"https://www.google.com/maps/search/?api=1&query={lat}%2C{lon}"

                
                
                
                #format for the name and description of a building
                embedMsg.add_field(name   = f"**{building_name}**",
                                value  = f"```{building_description}```",
                                inline = False)
                #format for the google maps link for the location and directions to the building
                embedMsg.add_field(name   = "", 
                                value  = f"[Directions to {building_name}](<{google_map_link}>)", 
                                inline = False)
                
                #loops thru each building in the second website
                for a_building in building_to_access:
                    building_and_access = a_building.text
                    #content stored is the building name, mode (who has access), open/close times on each line
                    #split by new line and gets the first line to get the name of building
                    a_building_name = building_and_access.split('\n')[0]
                    #compares to the argument inputed on discord
                    if(arg.lower() in a_building_name.lower()):
                        #gets the mode of the building
                        a_building_mode = building_and_access.split('\n')[1]


                        formatted_mode = ""
                        #the building mode is stored as one word, with all words stuck together,, so this formats the string
                        for word in a_building_mode:
                            if word.isupper() and formatted_mode:
                                #adds a space before each capital letter
                                formatted_mode += " "  
                            formatted_mode += word


                        
                        a_building_time = building_and_access.split('\n')[2]

                        
                        #outputs on discord in same manner as how descirption is printed
                        embedMsg.add_field(name = "",
                                           value = f"```Who has access to {a_building_name}: {formatted_mode}```",
                                           inline = False)
                        embedMsg.add_field(name = "",
                                           value = f"```Opening and Closing of {a_building_name}: {a_building_time}```",
                                           inline = False)
                        
        #SCRAPE FOR UNION INFORMATION
        if(str(arg).lower() in "rensselaer union"):
            #formats the title of the list of info of services
            embedMsg.add_field(name   = f"**The Union offers the services below: **",
                                value  = "",
                                inline = False)
            #scrapes the name of the service
            union_services = soup3.find_all("a", {'style': 'color:black;'})
            #outputs each service's name
            for service in union_services:
                name_of_service = service.text
                embedMsg.add_field(name = "",
                                           value = f"```{name_of_service}```",
                                           inline = False)
            
            #finds the text of the service,, description
            service_text = soup.find('p', {'data-block-key': 'fop2b'})
            
            

                        
                
          
                
        #case for when the building the user inputs is not found, return custom message
        if(not search_found):
            embedMsg = discord.Embed(title = f"Search Reuslts for **{arg}** not found",
                                     color = 0x9B27E6) 
        #command to send out the embeded message
        await ctx.send(embed=embedMsg)

    #error checking
    @building_search.error
    async def building_search_error(self, ctx, error):
        await ctx.send(str(error))

#setting up the discord bot for usage
async def setup(bot):
    await bot.add_cog(building_search(bot))
    