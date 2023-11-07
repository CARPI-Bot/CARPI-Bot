import requests
from bs4 import BeautifulSoup
from datetime import date, datetime, timedelta, timezone
from time import sleep

from table2ascii import table2ascii, PresetStyle
import calendar

# from PIL import Image, ImageDraw

def events_from_webpage() :
    '''
    This funtion is the main webscrapping function of the academic calendar. It when running, it is 
    directed to RPI's calendar page, parses through the page source of the website and organizes all 
    the data into a dictionary for easier access. It will return a dictionary of all the events
    listed on the calander for that particular schoolyear.

    Something that could be improved about this function would be to make it update and webscrape
    the website automatically instead of needing to manually run the funtion every school year.
    '''

    ## accessing the website
    URL = "https://info.rpi.edu/registrar/academic-calendar"
    header = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
    }

    ## getting the HTML content from the webpage
    r = requests.get(URL, headers = header)
    soup = BeautifulSoup(r.content, 'html5lib')

    ## finding the div container storing all the calender dates
    academicCal = soup.find('div', attrs = {'id' : "academicCalendar"})

    ## storing calendar dates into a list of dictionaries with keys for the
    ## month, day, event name, and a url of to more details about the event.
    dates = {}
    monthConversion = { "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
            "July": 6, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12}


    for month in academicCal.find_all('table'):
        rows = month.find_all('tr')  
        month = rows[0].text
        month = month.split()
        month = monthConversion[month[0]]

        months = []
        for d in range(len(rows)-1):
            day = rows[d+1].find_all('td')[0].text

            date = {}
            date['month'] = month
            date['date'] = day
            date['event'] = rows[d+1].find_all('td')[1].text
            date['url'] = rows[d+1].a['href']
            months.append(date)
        dates[month] = months

    return dates

def convert_d(date):
## this function returns the given date into the following format for easier reading for the datetime function:
##      2023-4-25 00:00:00

    # a dictionary that maps each month name to the corresponding month number
    months = { "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
               "July": 6, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12}
   
    # isolating all parts of the date string and removing not needed characters
    date = date.split()
    for i in range(len(date)):
        date[i] = date[i].strip()
        date[i] = date[i].strip(",-")
   
    # returns a list of formatted dates
    date_range = []
    i = 0
    while i < len(date):
        month = months[date[i]]
        day = date[i+1]
        year = date[i+2]

        date_range.append("{}-{}-{} 00:00:00".format(year, month, day))
        i += 4

    return date_range

def getMonthAndDate(dates):

    month = datetime.now().month
    year = datetime.now().year
    month_name = calendar.month_name[month]    
    cal = calendar.Calendar(calendar.SUNDAY)
    currMonth = cal.monthdayscalendar(year,month)
    currMonth = [[day if day != 0 else "" for day in week] for week in currMonth]
    currEvents = dates[month]

    thin = table2ascii(
        header=["sun", "mon", "tue", "wed", "thu", "fri", "sat"],
        body= currMonth,
        style=PresetStyle.thin_compact_rounded,
    )

    thin = month_name+" Calendar\n"+thin

    return [thin, currEvents]

def findEvent(prompt, dates):
    ''' dates will be the values for each month (so a list of dictionaries for events of that month) '''
    # print(dates)
    prompt = prompt.lower()

    split_prompt = prompt.split()
    # print(prompt)
    ## loop through the list

    fullMatches = []
    otherMatches =[]

    for month in dates:        
        for event in month:
            found = False
            description = event['event']
            description = description.lower()

            if description.find(prompt) != -1:
                fullMatches.append(event)
            else: 
                for word in split_prompt:
                    if description.find(word+" ") != -1:
                        otherMatches.append(event)
                        break
    
    # for match in fullMatches:
    #     print(match["date"], match['event'])
    return [fullMatches, otherMatches]

# def convertToImage(dates):
#     calendar = getMonthAndDate(dates)
#     text = calendar[0]

#     width, height = (1000, 1000)
#     im = Image.new("RGBA", (width, height), "white")

#     draw = ImageDraw.Draw(im)
#     # w, h = draw.multiline_text(text)

#     draw.multiline_text(((width)/2,(height)/2), text, fill="black")

#     im.save("final.png", "PNG")

#     return im

def formatFind(findList):
    fullMatches = findList[0]
    otherMaches = findList[1]

    full = ""
    other = ""

    # for event in fullMatches:
    #     full += "**" + event["date"] + "**\n" + event["event"]
    #     full += "\n"

    event = fullMatches[0]
    
    full += "**" + event["date"] + "**\n[" + event["event"] + "](" + event["url"] + ")"

    
    for event in otherMaches:
        other += "**" + event["date"] + "**\n " + event["event"]
        other += "\n"

    # print(full, "\n", other)
    
    return [full, other]

if __name__ == "__main__" :
    channel_id = 1099112664724152490
    dates = events_from_webpage()
    cal = getMonthAndDate(dates)
    # print(cal)
    # print(dates)
    # print(dates.values())
    find = findEvent("no classes", dates.values())
    find = formatFind(find)

    # convertToImage(dates)