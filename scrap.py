
import json
from datetime import datetime

# "%Y-%m-%d"
aDate = "1998-09-30"
newDate = datetime.strptime(aDate, "%Y-%m-%d").strftime("%m/%d/%Y")

print(newDate)

#  = datetime.today().date().strftime("%m-%d-%Y")

# todayf = str(datetime.strptime(today, "%Y-%m-%d").strftime("%m-%d-%Y"))

print("Today:", type(datetime.today().date().strftime("%Y-%m-%d")))

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