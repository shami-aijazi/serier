
import json
from datetime import datetime
import pytz
from datetime import timedelta

# <!date^1577751600.0^{date_pretty}{time}|fallback_text>

tz = pytz.timezone('America/Los_Angeles')

selected_time = datetime.strptime("04:20 PM", '%I:%M %p')
selected_date = datetime.strptime("2019-12-30", "%Y-%m-%d")
selected_dt = selected_date.replace(hour=selected_time.hour, minute=selected_time.minute)


# Localize the datetime we have.
local_dt = tz.localize(selected_dt)
print("Local timezone after making it aware:", local_dt)
print("local timestamp:", local_dt.timestamp())

utc_dt = local_dt.astimezone(pytz.utc)
print("UTC time:", utc_dt)
print("utc from local timestamp:", utc_dt.timestamp())



# def date_after_adding_weekdays(current_date, num_weekdays):
#     """
#     Increment the current_date by a specified number of weekdays.

#     Parameters
#     current_date: datetime object
#         date to start counting from
#     num_weekdays: int
#         number of weekdays to add to the date

#     Return the date n weekdays later.
#     """

#     while num_weekdays > 0:
#         current_date += timedelta(days=1)
#         weekday = current_date.weekday()
#         if weekday >= 5: # sunday = 6
#             continue
#         num_weekdays -= 1
#     return current_date

# def date_after_adding_weekdays_v2(current_date, num_weekdays):
#     """
#     Increment the date by number of weekdays, including today.

#     Parameters
#     current_date: datetime object
#         date to start counting from
#     num_weekdays: int
#         number of weekdays to add to the date

#     Return the date n weekdays later.
#     """
#     day_number = 1

#     while num_weekdays > day_number:

#         if day_number == 1:
#             print("Inside adding weekdays function...")
#             print("day_number:", day_number)
#             print("Current datetime:", current_date)
#             print(50*"=" + "\n")        
            
#         current_date += timedelta(days=1) 

#         if current_date.weekday() < 5: # sunday = 6
#             day_number += 1
#             print("Inside adding weekdays function...")
#             print("day_number:", day_number)
#             print("Current datetime:", current_date)
#             print(50*"=" + "\n")
#     return current_date


# print("4 weekdays from now:", date_after_adding_weekdays_v2(datetime.now(), 4))

# def date_after_adding_days(current_date, num_days):
#     """
#     Increment the current_date by a specified number of days.

#     Parameters
#     current_date: datetime object
#         date to start counting from
#     num_days: int
#         number of days to add to the date

#     Return the date n days later.
#     """

#     return current_date + timedelta(days=num_days)

# def date_after_adding_weeks(current_date, num_weeks):
#     """
#     Increment the current_date by a specified number of weeks.

#     Parameters
#     current_date: datetime object
#         date to start counting from
#     num_weeks: int
#         number of weeks to add to the date

#     Return the date n weeks later.
#     """

#     return current_date + timedelta(days=7*num_weeks)


# print("numsessions-8"[12:])

# A messy loop to make a list of times.

# strminute = ""
# strhour = ""
# ampm=""

# options = []
# for hour in range (24):
#     if hour < 12:
#         if hour == 0:
#             hour = 12
#         ampm = "AM"
#         for minute in range (0, 60, 15):
#             if minute == 0:
#                 strminute = "00"
#             else:
#                 strminute = str(minute)

#             if hour <= 9:
#                 strhour = "0" + str(hour)
#             elif hour == 12:
#                 strhour = "00"
#             else:
#                 strhour= str(hour)
            

#             options.append({"text": {"type": "plain_text","text": str(hour) + ":" + strminute + " " + ampm, "emoji": True},"value": "time-" + strhour+ strminute})

#     elif hour >= 12:
#         if hour != 12:
#             hour -= 12  
#         ampm = "PM"
#         for minute in range (0, 60, 15):
#             if minute == 0:
#                 strminute = "00"
#             else:
#                 strminute = str(minute)
            
#             if hour != 12:
#                 strhour= str(hour+12)
            

#             options.append({"text": {"type": "plain_text","text": str(hour) + ":" + strminute + " " + ampm, "emoji": True},"value": "time-" + strhour+ strminute})

# jsonresult = json.dumps(options)
# print(jsonresult)


# A messy loop to make the number of sessions (max 50)
# {"text":{"type":"plain_text","text":"Choice 1","emoji":true},"value":"value-0"}


# options = []

# for i in range(1, 51):
#     options.append({"text":{"type":"plain_text","text":str(i),"emoji":True},"value":"numsessions-"+ str(i)})

# jsonresult = json.dumps(options)
# print(jsonresult)