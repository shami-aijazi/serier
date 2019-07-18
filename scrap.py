
import json
from new_series_menu_blocks import new_series_menu_blocks


summary_title = new_series_menu_blocks[-2]["elements"][0]["text"]

print (summary_title)












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