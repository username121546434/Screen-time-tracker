from constants import TimePeriod, DATE_FMT
from datetime import datetime
from PySide6.QtCore import QDate


def get_title(time: TimePeriod, date: QDate):
    if time == 'All Time':
        return 'All Time Screen Time'
    elif time == 'Day':
        day = date.toPython() # this returns a datetime.date object
        day = datetime(day.year, day.month, day.day)
        return f'Screen time for {day:{DATE_FMT}}'
    elif time == 'Month':
        return f'Screen time for {datetime(date.year(), date.month(), date.day()-1):%B %Y}'
    elif time == 'Year':
        return f'Screen time for {date.year()}'