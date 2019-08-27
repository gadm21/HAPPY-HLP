import time
import datetime


def date_to_timestamp(date):
    return int(time.mktime(datetime.datetime.strptime(date, "%Y-%m-%d").timetuple()))
