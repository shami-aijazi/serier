
import json
from datetime import datetime
import pytz
from datetime import timedelta

if ('0'):
    print(" \'0\' is true")


# <!date^1577751600.0^{date_pretty}{time}|fallback_text>

tz = pytz.timezone('America/Los_Angeles')

selected_time = datetime.strptime("04:20 PM", '%I:%M %p')
selected_date = datetime.strptime("2019-12-30", "%Y-%m-%d")
selected_dt = selected_date.replace(hour=selected_time.hour, minute=selected_time.minute)


# Localize the datetime we have.
local_dt = tz.localize(selected_dt)
print("Local timezone after making it aware:", local_dt)
print("local timestamp:", local_dt.timestamp())

utc_dt = local_dt.astimezone(pytz.utc).timestamp()
print("UTC timestamp:", utc_dt)
# print("utc from local timestamp:", utc_dt.timestamp())
