
# Log all the oauth env variables
# import os
# print("CLIENT_ID = ", os.environ['CLIENT_ID'])
# print("CLIENT_SECRET = ", os.environ['CLIENT_SECRET'])
# print("SIGNING_SECRET = ", os.environ['SIGNING_SECRET'])


# A messy loop to make a list of times.
import json
strminute = ""
strhour = ""
ampm=""

options = []
for hour in range (24):
    if hour < 12:
        if hour == 0:
            hour = 12
        ampm = "AM"
        for minute in range (0, 60, 15):
            if minute == 0:
                strminute = "00"
            else:
                strminute = str(minute)

            if hour <= 9:
                strhour = "0" + str(hour)
            elif hour == 12:
                strhour = "00"
            else:
                strhour= str(hour)
            

            options.append({"text": {"type": "plain_text","text": str(hour) + ":" + strminute + " " + ampm, "emoji": True},"value": "time-" + strhour+ strminute})

    elif hour >= 12:
        if hour != 12:
            hour -= 12  
        ampm = "PM"
        for minute in range (0, 60, 15):
            if minute == 0:
                strminute = "00"
            else:
                strminute = str(minute)
            
            if hour != 12:
                strhour= str(hour+12)
            

            options.append({"text": {"type": "plain_text","text": str(hour) + ":" + strminute + " " + ampm, "emoji": True},"value": "time-" + strhour+ strminute})

jsonresult = json.dumps(options)
print(jsonresult)
