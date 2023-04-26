import asyncio
from globals import *
from time import sleep
from datetime import date, datetime

from apscheduler.schedulers.background import BlockingScheduler, BackgroundScheduler
from apscheduler import events
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_MISSED, JobExecutionEvent
from apscheduler.triggers.date import DateTrigger

from discord.ext import commands
from calendar.academic_cal import events_from_webpage, convert_d

class AcadCal(commands.Cog) :
    def __init__(self, bot):
        self.bot = bot
        self.schedule = BlockingScheduler(timezone = "America/New_York")
    
    async def send_to_channel(self, channel_id: int, event: str) -> None:
        channel = self.bot.get_channel(channel_id)
        await channel.send(str)

    async def read_dates(self):
        channel_id = 1099112664724152490
        dates = events_from_webpage()

        # await self.schedule.add_job(self.send_to_channel, 'date', run_date = "2023-4-25 21:45:00",
        #             kwargs={ "channel_id" : channel_id, "event" : "hhh"})

        for date in dates:
            dateRange = convert_d(date['date'])

            for day in dateRange:
                await self.schedule.add_job(await self.send_to_channel, 'date', run_date = day,
                                kwargs={ "channel_id" : channel_id, "event" : date['event']})
        await self.schedule.start()

async def setup(bot):
    await bot.add_cog(AcadCal(bot))
