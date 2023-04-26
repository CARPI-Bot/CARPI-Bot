import requests
from bs4 import BeautifulSoup


from datetime import datetime, timedelta, timezone




from time import sleep
from datetime import date, datetime


from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.background import BlockingScheduler

from apscheduler import events
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_MISSED, JobExecutionEvent
from apscheduler.triggers.date import DateTrigger


def events_from_webpage() :
    URL = "https://info.rpi.edu/registrar/academic-calendar"
    header = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
    }


    ## getting the HTML content from the webpage
    r = requests.get(URL, headers = header)
    soup = BeautifulSoup(r.content, 'html5lib')


    ## finding the div container storing all the calender dates
    academicCal = soup.find('div', attrs = {'id' : "academicCalendar"})


    ## storing calendar dates into a list of dictionaries
    dates = []
    months = {'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
            'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12}


    for month in academicCal.find_all('table'):
        rows = month.find_all('tr')  
        month = rows[0].text  


        for d in range(len(rows)-2):
            day = rows[d+1].find_all('td')[0].text


            date = {}
            date['month'] = month
            date['date'] = day
            date['event'] = rows[d+1].find_all('td')[1].text
            date['url'] = rows[d+1].a['href']
            dates.append(date)


    for day in dates:
        print(day['date'], day['event'], sep="\n")
        print()


    return dates

def send_to_channel(channel_id: int, event: str) -> None:
    print("txt")


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
   
if __name__ == "__main__" :
    channel_id = 1099112664724152490
    dates = events_from_webpage()
    schedule = BlockingScheduler(timezone = "America/New_York")


    schedule.add_job(send_to_channel, 'date', run_date = "2023-4-25 20:40:00",
                     kwargs={ "channel_id" : channel_id, "event" : "hhh"})
    schedule.start()