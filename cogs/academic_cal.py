import requests
from bs4 import BeautifulSoup

import discord
from discord.ext import commands

from datetime import datetime, timedelta, timezone


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

for month in academicCal.find_all('table'):
    rows = month.find_all('tr')  
    month = rows[0].text  

    for d in range(len(rows)-2):
        date = {}
        date['month'] = month
        date['date'] = rows[d+1].find_all('td')[0].text
        date['event'] = rows[d+1].find_all('td')[1].text
        date['url'] = rows[d+1].a['href']
        dates.append(date)

for day in dates:
    print(day['date'], day['event'], sep="\n")
    print()
