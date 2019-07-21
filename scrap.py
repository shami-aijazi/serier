
import json
from datetime import datetime
from datetime import timedelta

def date_after_adding_weekdays(current_date, num_weekdays):
    """
    Increment the current_date by a specified number of weekdays.

    Parameters
    current_date: datetime object
        date to start counting from
    num_weekdays: int
        number of weekdays to add to the date

    Return the date n weekdays later.
    """

    while num_weekdays > 0:
        current_date += timedelta(days=1)
        weekday = current_date.weekday()
        if weekday >= 5: # sunday = 6
            continue
        num_weekdays -= 1
    return current_date

def date_after_adding_days(current_date, num_days):
    """
    Increment the current_date by a specified number of days.

    Parameters
    current_date: datetime object
        date to start counting from
    num_weekdays: int
        number of days to add to the date

    Return the date n days later.
    """

    return current_date + timedelta(days=num_days)

def date_after_adding_weeks(current_date, num_weeks):
    """
    Increment the current_date by a specified number of weeks.

    Parameters
    current_date: datetime object
        date to start counting from
    num_weeks: int
        number of weeks to add to the date

    Return the date n weeks later.
    """

    return current_date + timedelta(days=7*num_weeks)


print("8 days from today: ", date_after_adding_days(datetime.today(), 8))
print ('10 business days from today:', date_after_adding_weekdays(datetime.today(), 10))

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