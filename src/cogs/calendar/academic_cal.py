# Importing necessary modules and packages
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Importing a third-party library for converting tables to ASCII art
from table2ascii import table2ascii, PresetStyle
import calendar

# Function to scrape events from the academic calendar webpage
def events_from_webpage():
    '''
    This function performs web scraping on RPI's academic calendar webpage. It retrieves
    and organizes event data into a dictionary, providing a convenient format for
    accessing information about events for a particular school year.

    Note: An improvement could be made to automate the update and scraping process,
    eliminating the need to manually run the function for each school year.
    '''

    # Accessing the website
    URL = "https://info.rpi.edu/registrar/academic-calendar"
    header = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
    }

    # Getting HTML content from the webpage
    r = requests.get(URL, headers=header)
    soup = BeautifulSoup(r.content, 'html5lib')

    # Finding the div container storing all the calendar dates
    academicCal = soup.find('div', attrs={'id': "academicCalendar"})

    # Storing calendar dates into a dictionary
    dates = {}
    monthConversion = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
                       "July": 6, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12}

    for month in academicCal.find_all('table'):
        rows = month.find_all('tr')
        month = rows[0].text
        month = month.split()
        month = monthConversion[month[0]]

        months = []
        for d in range(len(rows) - 1):
            day = rows[d + 1].find_all('td')[0].text

            date = {}
            date['month'] = month
            date['date'] = day
            date['event'] = rows[d + 1].find_all('td')[1].text
            date['url'] = rows[d + 1].a['href']
            months.append(date)
        dates[month] = months

    return dates

# Function to get the current month's calendar and events
def getMonthAndDate(dates):
    '''
    This function generates a formatted ASCII calendar for the current month and returns
    a list containing the formatted calendar and a list of events for the current month.
    '''

    month = datetime.now().month
    year = datetime.now().year
    month_name = calendar.month_name[month]
    cal = calendar.Calendar(calendar.SUNDAY)
    currMonth = cal.monthdayscalendar(year, month)
    currMonth = [[day if day != 0 else "" for day in week] for week in currMonth]
    currEvents = dates[month]

    thin = table2ascii(
        header=["sun", "mon", "tue", "wed", "thu", "fri", "sat"],
        body=currMonth,
        style=PresetStyle.thin_compact_rounded,
    )

    thin = month_name + " Calendar\n" + thin

    return [thin, currEvents]

# Function to find events based on a prompt
def findEvent(prompt, dates):
    '''
    This function takes a prompt, searches for direct and other relevant matches in the
    events, and returns a list of two dictionaries holding direct matches and other
    relevant matches from the calendar for the remaining events of the semester.
    '''

    # Cleaning the prompt to make it easier to search through events
    prompt = prompt.lower()
    split_prompt = prompt.split()

    # Loop through the list of events
    fullMatches = []
    otherMatches = []

    # Search for matches and filter through them
    for month in dates:
        for event in month:
            description = event['event'].lower()

            # Check for direct matches
            if description.find(prompt) != -1:
                fullMatches.append(event)
            else:
                # Check for matches with individual words in the prompt
                for word in split_prompt:
                    if description.find(word + " ") != -1:
                        otherMatches.append(event)
                        break
    return [fullMatches, otherMatches]

# Function to format the found events
def formatFind(findList):
    '''
    This function takes a list of found events, separates them into direct matches and
    other relevant matches, and returns a formatted list for each category.
    '''

    fullMatches = findList[0]
    otherMatches = findList[1]

    full = ""
    other = ""

    # Format direct matches
    for event in fullMatches:
        full += "**" + event["date"] + "**\n[" + event["event"] + "](" + event["url"] + ")"
        full += "\n"

    # Format other relevant matches
    for event in otherMatches:
        other += "**" + event["date"] + "**\n[" + event["event"] + "](" + event["url"] + ")"
        other += "\n"

    return [full, other]

# Main block of code to test the functions
if __name__ == "__main__":
    # Example usage of the functions
    channel_id = 1099112664724152490
    dates = events_from_webpage()
    cal = getMonthAndDate(dates)

    # Find and format events related to "no classes"
    find = findEvent("no classes", dates.values())
    find = formatFind(find)
