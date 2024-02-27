import calendar
from datetime import datetime

import aiohttp
from bs4 import BeautifulSoup
from table2ascii import PresetStyle, table2ascii


# Function to scrape events from the academic calendar webpage
async def events_from_webpage() -> dict:
    """
    This function performs web scraping on RPI's academic calendar webpage. It retrieves
    and organizes event data into a dictionary, providing a convenient format for
    accessing information about events for a particular school year.

    Note: An improvement could be made to automate the update and scraping process,
    eliminating the need to manually run the function for each school year.
    """

    # Accessing the website
    URL = "https://info.rpi.edu/registrar/academic-calendar"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
    }

    # Getting HTML content from the webpage
    async with aiohttp.ClientSession(headers=headers, timeout=aiohttp.ClientTimeout(5)) as session:
        async with session.get(url=URL) as response:
            soup = BeautifulSoup(await response.text(), "html5lib")

    # Finding the div container storing all the calendar dates
    academicCal = soup.find("div", attrs={"id": "academicCalendar"})

    # Storing calendar dates into a dictionary
    dates = {}
    monthConversion = {
        "January": 1,
        "February": 2,
        "March": 3,
        "April": 4,
        "May": 5,
        "June": 6,
        "July": 6,
        "August": 8,
        "September": 9,
        "October": 10,
        "November": 11,
        "December": 12
    }

    for month in academicCal.find_all("table"):
        rows = month.find_all("tr")
        month = rows[0].text
        month = month.split()
        month = monthConversion[month[0]]

        months = []
        for d in range(len(rows) - 1):
            day = rows[d + 1].find_all("td")[0].text
            date = {}
            date["month"] = month
            date["date"] = day
            date["event"] = rows[d + 1].find_all("td")[1].text
            date["url"] = rows[d + 1].a["href"]
            months.append(date)
        dates[month] = months

    return dates

def convert_d(date):
## this function returns the given date into the following format for easier reading for the datetime function:
##      2023-4-25 00:00:00
    # a dictionary that maps each month name to the corresponding month number
    months = {
        "January": 1,
        "February": 2,
        "March": 3,
        "April": 4,
        "May": 5,
        "June": 6,
        "July": 7,
        "August": 8,
        "September": 9,
        "October": 10,
        "November": 11,
        "December": 12
    }
   
    # isolating all parts of the date string and removing not needed characters
    date = date.split()
    for i in range(len(date)):
        date[i] = date[i].strip(",")
   
    # returns formatted dates
    month = months[date[0]]
    day = date[1]
    year = date[2]
    day = "{} {} {}".format(month, day, year)

    format = "%m %d %Y"
    datetime_str = datetime.strptime(day, format)
 
    return datetime_str

def getMonthAndDate(dates):
    """
    This function generates a formatted ASCII calendar for the current month and returns
    a list containing the formatted calendar and a list of events for the current month.
    """
    month = datetime.now().month
    year = datetime.now().year
    month_name = calendar.month_name[month]
    cal = calendar.Calendar(calendar.SUNDAY)
    currMonth = cal.monthdayscalendar(year, month)
    currMonth = [[day if day != 0 else "" for day in week] for week in currMonth]
    currEvents = dates[month]
    thin = table2ascii(
        header = ["sun", "mon", "tue", "wed", "thu", "fri", "sat"],
        body = currMonth,
        style = PresetStyle.thin_compact_rounded
    )
    thin = month_name + " Calendar\n" + thin
    return [thin, currEvents]

def getWeekAndDate(dates):
    """
    This function generates a formatted ASCII calendar for the current week and returns
    a list containing the formatted calendar and a list of events for the current week.
    """
    # Retrieve the current date    
    current_date = datetime.now()
    year, week, day = current_date.isocalendar()
    month = datetime.now().month
    cal = calendar.Calendar(calendar.SUNDAY)
    currMonth = cal.monthdayscalendar(year, month)
    currMonth = [[day if day != 0 else "" for day in week] for week in currMonth]
    currEvents = dates[month]
    weekEvents = []
    for event in currEvents:
        date = event["date"]
        if "-" in date:
            date = date.split("-")
            startDate = convert_d(date[0])
            _, startWeek, _ = startDate.isocalendar()
            endDate = convert_d(date[1])
            _, endWeek, _ = endDate.isocalendar()
            if week in range(startWeek, endWeek + 1):
                weekEvents.append(event)
        else:
            date = convert_d(date)
            _, event_week, _ = date.isocalendar()
            if event_week == week:
                weekEvents.append(event)      
    return weekEvents

def findEvent(prompt, dates):
    """
    This function takes a prompt, searches for direct and other relevant matches in the
    events, and returns a list of two dictionaries holding direct matches and other
    relevant matches from the calendar for the remaining events of the semester.
    """
    # Cleaning the prompt to make it easier to search through events
    prompt = prompt.lower()
    split_prompt = prompt.split()
    # Use list comprehensions to filter direct and other matches
    fullMatches = [event for month in dates for event in month if prompt in event["event"].lower()]
    # Check for matches with individual words in the prompt
    otherMatches = []
    for month in dates:
        for event in month:
            description = event["event"].lower()
            for word in split_prompt:
                if word in description and event not in fullMatches:
                    otherMatches.append(event)
                    break
    return [fullMatches, otherMatches]

def formatFind(findList):
    """
    This function takes a list of found events, separates them into direct matches and
    other relevant matches, and returns a formatted list for each category.
    """
    fullMatches, otherMatches = findList[0], findList[1]
    # Use a list comprehension to format direct matches
    full = "\n".join(f"**{event['date']}**\n[{event['event']}]({event['url']})" for event in fullMatches)
    # Use a list comprehension to format other relevant matches
    other = "\n".join(f"**{event['date']}**\n[{event['event']}]({event['url']})" for event in otherMatches)
    return [full, other]

if __name__ == "__main__":
    pass
    # Example usage of the functions
    # channel_id = 1099112664724152490
    # dates = events_from_webpage()
    # cal = getMonthAndDate(dates)
    # cal = getWeekAndDate(dates)

    # # Find and format events related to "no classes"
    # find = findEvent("no classes", dates.values())
    # find = formatFind(find)
