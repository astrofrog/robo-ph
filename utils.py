from __future__ import division

from datetime import datetime

def weekdays(start_date, end_date):

    if start_date.weekday() >= 5:
        raise ValueError("Start date should be a week day")

    if end_date.weekday() >= 5:
        raise ValueError("End date should be a week day")

    weekends = (end_date - start_date).days // 7

    if end_date.weekday() < start_date.weekday():
        weekends += 1

    weekdays = (end_date - start_date).days - weekends * 2 + 1

    return weekdays
