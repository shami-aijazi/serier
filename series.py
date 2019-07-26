import json
from new_series_menu_blocks import new_series_menu_blocks
import copy

# Make a copy of the blocks so they can be reset to the new blocks if series is cancelled
current_series_menu_blocks = copy.deepcopy(new_series_menu_blocks)
# Console log for copy
# print("\n" + 70*"="  + "\nCopying new blocks to current blocks... \n" + 70*"=")

from datetime import datetime
from datetime import timedelta
import pytz
"""
Slack Series class to represent series for the series organizer app.
"""
class Series(object):
    """ Instatiates a Series object to represent the state of a series"""
    def __init__(self):
        super(Series, self).__init__()
        # Storing the state associated with a new series being created. This will be continuously
        # updated as user inputs information about new series. It will start off with default values.
        self.state = {}
        # Store the timestamp of the original series creation menu message. This will allow us
        # to alter the message as the state changes.
        self.menu_ts = ""
        # Store the timezone that the datetime of the series was created in.
        # Stored as a timezone string (example: America/Los_Angeles)
        # This is so it can be stored in the backend as UTC or POSIX.
        self.timezone = ""
        # A list of session JSON objects. Each session has an id, a POSIX ts, a presenter, and a topic.
        self.sessions = []

    def newSeries(self, ts, first_session, series_time, menu_tz):
        """
        # TODO Should this modify the series itself or return a new series with the changes??

        Set the state to be the default values that the series creation menu will show.

        Parameters
        ----------
        ts: str
            timestamp of the series creation menu message. This is needed to update the message.

        first_session: str
            the default date of the first session in the series.

        series_time: str
            the default time of the sessions in the series
        
        menu_tz: str
            the timezone associated with the date and time of the series.

        """
        self.state = {"title": "My Team's Weekly Brownbag",
                      "presenter": "Not Selected",
                      "topic_selection": "Not Selected",
                      "first_session": first_session,
                      "time": series_time,
                      "frequency": "Not Selected",
                      "num_sessions": 0,
                      "last_session": "N/A"
                    }
        self.menu_ts = ts
        self.timezone = menu_tz


    def isComplete(self):
        """
        Check if Series state is complete. If all required fields have been filled,
        return true, else return false.
        """
        # Console log for series menu elements
        # print("\n" + 70*"="  + "\nSeries menu completeness check... \n")
        # print("Presenter Selected:", self.state["presenter"] != "Not Selected")
        # print("Topic Selection Selected:", self.state["topic_selection"] != "Not Selected")
        # print("Time Selected:", self.state["time"] != "Not Selected")
        # print("Frequency Selected:", self.state["frequency"] != "Not Selected")
        # print("Num_Sessions Selected:", self.state["num_sessions"] != 0)
        # print(70*"=")


        return (self.state["presenter"] != "Not Selected" and self.state["topic_selection"]!= "Not Selected"
        and self.state["time"] != "Not Selected" and self.state["frequency"] != "Not Selected" and
        self.state["num_sessions"] != 0)


    def updateSeries(self, field, newValue):
        """
        Update one of the state's fields.

        Parameters
        ----------
        field : str
            state field to be changed.

        newValue: str
            the new value of the field to be updated.
        """
        self.state[field] = newValue
    
    def resetSeries(self):
        """
        Empty series state.
        """
        global current_series_menu_blocks

        # Console log for comparing current series menu to a new one
        # print("\n" + 70*"="  + "\nInside resetSeries...\ncurrent and new menu blocks are identical? \n", current_series_menu_blocks == new_series_menu_blocks, "\n" + 70*"=")
        
        # reset the current series menu blocks
        current_series_menu_blocks = copy.deepcopy(new_series_menu_blocks)

        self.state = {}
        self.menu_ts = ""
        self.timezone = ""
        # self.sessions = []
        


    def getLastSession(self):
        """
        Calculate and update last session date based on first session date,
        number of sessions, and frequency.

        Return last session date
        """

        # Start at the start_date, formatted to be a datetime object
        last_session = datetime.strptime(self.state["first_session"], "%Y-%m-%d")
        
        # Extract frequency and num_sessions
        frequency = self.state["frequency"]
        num_sessions = int(self.state["num_sessions"])


        # Subtract numsessions by 1 to avoid overcounting
        num_sessions -= 1

        if frequency == "every-day":
            # format this correctly
            last_session += timedelta(days=num_sessions)

        elif frequency == "every-weekday":
            # every weekday sequence
            while num_sessions > 0:
                last_session = last_session + timedelta(days=1)
                weekday = last_session.weekday()
                if weekday >= 5: # saturday = 5, sunday = 6
                    continue
                num_sessions -= 1

        elif frequency == "every-week":
            # every week sequence
            last_session += timedelta(days=7*num_sessions)

        elif frequency == "every-2-weeks":
            # every 2 weeks sequence
            last_session += timedelta(days=14*num_sessions)

        elif frequency == "every-3-weeks":
            # every 3 weeks sequence
            last_session += timedelta(days=21*num_sessions)

        elif frequency == "every-month":
            # every month sequency
            last_session += timedelta(days=28*num_sessions)
        
        # Format the datetime object
        last_session = last_session.strftime("%m/%d/%Y")

        # Store the result in state
        self.state["last_session"] = last_session

    def getMenuBlocks(self):
        """
        Generate the blocks that the series creation menu will be composed of. 
        These blocks will be based on the current state.

        Returns the blocks JSON dict object
        """
        # Console log series menu completeness
        # print("\n" + 70*"="  + "\nRunning getMenuBlocks... \n" + "series.state=\n", self.state, "\n" + 70*"=")



        # Update the series creation menu as state changes


        # ==================== Update Title ====================
        # 1- === Update title section ===
        current_series_menu_blocks[3]["text"]["text"] = "*" + self.state["title"] + "*"

        # 2- === Update summary context ===
        current_series_menu_blocks[-2]["elements"][0]["text"] = "*Title*: " + self.state["title"] 

        # ==================== Update Presenter ====================
        # 1- === Update users select menu ===

        # console log for series_menu_blocks. Check if there is an initial_option carried over
        # from last run
        # print("\n" + 70*"="  + "\nseries_menu_blocks=\n", current_series_menu_blocks, "\n" + 70*"=")

        # If presenter still has already been selected
        if self.state["presenter"] != "Not Selected":
            current_series_menu_blocks[6]["accessory"]["initial_user"] = self.state["presenter"]

        # 2- === Update summary context ===
        # If the presenter still has not been selected
        if self.state["presenter"] == "Not Selected":
            current_series_menu_blocks[-2]["elements"][1]["text"] = "*Presenter*: " +  self.state["presenter"]
        else:
            current_series_menu_blocks[-2]["elements"][1]["text"] = "*Presenter*: " +  "<@" + self.state["presenter"] + ">"

        
        # ==================== Update Topic Selection ====================
        
        if self.state["topic_selection"] != "Not Selected":
            
            # 1- === Update select menu ===
            if self.state["topic_selection"] == "pre-determined":
                current_series_menu_blocks[7]["accessory"]["initial_option"] = {
                    "text":
                        {"type":"plain_text",
                        "text":"Pre-determined",
                        "emoji":True},
                        "value":"pre-determined"
                    }

                # 2- === Update summary context ===
                current_series_menu_blocks[-2]["elements"][2]["text"] = "*Topic Selection*: Pre-determined"
            
            # 1- === Update select menu ===
            elif self.state["topic_selection"] == "presenter_choice":
                current_series_menu_blocks[7]["accessory"]["initial_option"] = {
                    "text":
                        {"type":"plain_text",
                        "text":"Presenter's Choice",
                        "emoji":True},
                        "value":"presenter_choice"
                    }

                # 2- === Update summary context ===
                current_series_menu_blocks[-2]["elements"][2]["text"] = "*Topic Selection*: Presenter's Choice"


        # ==================== Update First Session Date ====================
        # 1- === Update datepicker ===
        current_series_menu_blocks[10]["elements"][0]["initial_date"] = self.state["first_session"]

        
        # 2- === Update summary context ===
        # Format it correctly
        if self.state["first_session"] != "Not Selected":
            current_series_menu_blocks[-2]["elements"][3]["text"] = "*First Session*: " + datetime.strptime(self.state["first_session"], "%Y-%m-%d").strftime("%m/%d/%Y")

        # ==================== Update Time ====================
        
        # 1- === Update select menu ===
        current_series_menu_blocks[10]["elements"][1]["initial_option"] = {
            "text":
                {"type": "plain_text",
                "text": self.state["time"],
                "emoji": True},
                # Format the time for the "value" parameter
                "value": "time-" + datetime.strptime(self.state["time"], '%I:%M %p').strftime('%H%M')
            }
        
        # 2- === Update summary context ===
        current_series_menu_blocks[-2]["elements"][4]["text"] = "*Time*: " + self.state["time"]

        # ==================== Update Frequency ====================
        # 1- === Update select menu ===
        if self.state["frequency"] != "Not Selected":
            current_series_menu_blocks[11]["elements"][0]["initial_option"] = {
                    "text":
                        {"type": "plain_text",
                        "text": self.state["frequency"].replace("-", " ").title(),
                        "emoji": True},
                        # Format the time for the "value" parameter
                        "value": self.state["frequency"]
                    }
                    
        # 2- === Update summary context ===
        current_series_menu_blocks[-2]["elements"][5]["text"] = "*Frequency*: " + self.state["frequency"].replace("-", " ").title()

        # ==================== Update Num_sessions ====================
        # 1- === Update select menu ===
        if self.state["num_sessions"] != 0:
            current_series_menu_blocks[11]["elements"][1]["initial_option"] = {
                    "text":
                        {"type": "plain_text",
                        "text": str(self.state["num_sessions"]),
                        "emoji": True},
                        # Format the string for the value parameter
                        "value": "numsessions-" + str(self.state["num_sessions"])
                    }
                    
        # ==================== Update Last Session Date ====================
        # If the frequency and the num_sessions has not been selected
        if self.state["frequency"] != "Not Selected" and self.state["num_sessions"] != 0:
            self.getLastSession()
        current_series_menu_blocks[-2]["elements"][6]["text"] = "*Last Session*: " + self.state["last_session"]


        # ==================== Add Start Button When Series Complete ====================
        # If series menu is complete
        if self.isComplete():
            # Console log series menu completeness
            # print("\n" + 70*"="  + "\nSeries menu is complete... \n" + 70*"=")


            # show "start series" button
            start_series_button = {
				"type": "button",
				"action_id": "start_series",
				"text": {
					"type": "plain_text",
					"text": "Start",
					"emoji": True
				},
				"style": "primary",
				"value": "start"
			}

            # Add the start button to the menu (if it doesn't already exist)
            if len(current_series_menu_blocks[-1]["elements"]) == 1 :
                current_series_menu_blocks[-1]["elements"].insert(0, start_series_button)
        # else:
        #     # Console log series menu completeness
        #     print("\n" + 70*"="  + "\nSeries menu is NOT complete... \n" + 70*"=")

        # Return it after modifications
        return current_series_menu_blocks

    def setSessions(self):
        """
        Generate a list of session objects corresponding to the sessions that the series will be composed of.
        Store this list on the Series object.
        These sessions will be computed and populated based on the values in the series state.
        Since this method assumes that the series state is full this method should only be called after
        making sure the series menu is complete.
        """
        frequency = self.state["frequency"]
        num_sessions = int(self.state["num_sessions"])

        series_time = datetime.strptime(self.state["time"],"%I:%M %p")


        next_session_dt = datetime.strptime(self.state["first_session"], "%Y-%m-%d")

        # Get the datetime of the first session
        next_session_dt = next_session_dt.replace(hour=series_time.hour, minute=series_time.minute)

        # Localize the time to utc
        next_session_dt = pytz.utc.localize(next_session_dt)


        # If the frequency is every day
        if frequency == "every-day":
            for session_number in range (1, num_sessions+1):

                # Create a new session for each day, including the first day
                # Topic will only be populated if the series topic selection option is "pre-determined"
                next_session = {
                "session_id": "session-" + str(session_number),
                "ts": str(int(next_session_dt.timestamp())),
                "presenter": self.state["presenter"],
                "topic": "Not Selected"
                }

                self.sessions.append(next_session)

                # Increment the datetime by one day
                next_session_dt += timedelta(days=1)


        # If the frequency is every weekday
        elif frequency == "every-weekday":

            session_number = 0
            while num_sessions > session_number:

                # For the first session
                if session_number == 0:
                    session_number+=1
                    # TODO append here
                    next_session = {
                    "session_id": "session-" + str(session_number),
                    "ts": str(int(next_session_dt.timestamp())),
                    "presenter": self.state["presenter"],
                    "topic": "Not Selected"
                    }
                    self.sessions.append(next_session)
                    
                

                # Increment the datetime by one day
                next_session_dt += timedelta(days=1) 

                # If it is a weekday
                if next_session_dt.weekday() < 5: # sunday = 6
                    session_number+=1
                    next_session = {
                    "session_id": "session-" + str(session_number),
                    "ts": str(int(next_session_dt.timestamp())),
                    "presenter": self.state["presenter"],
                    "topic": "Not Selected"
                    }
                    self.sessions.append(next_session)
                    

                


        # If the frequency is every week
        elif frequency == "every-week":
            for session_number in range (1, num_sessions+1):

                # Topic will only be populated if the series topic selection option is "pre-determined"
                next_session = {
                "session_id": "session-" + str(session_number),
                "ts": str(int(next_session_dt.timestamp())),
                "presenter": self.state["presenter"],
                "topic": "Not Selected"
                }

                self.sessions.append(next_session)

                # 7 days
                next_session_dt += timedelta(days=7)

        # Every 2 weeks
        elif frequency == "every-2-weeks":
            for session_number in range (1, num_sessions+1):

                # Topic will only be populated if the series topic selection option is "pre-determined"
                next_session = {
                "session_id": "session-" + str(session_number),
                "ts": str(int(next_session_dt.timestamp())),
                "presenter": self.state["presenter"],
                "topic": "Not Selected"
                }

                self.sessions.append(next_session)

                # 14 days
                next_session_dt += timedelta(days=14)

        elif frequency == "every-3-weeks":
            for session_number in range (1, num_sessions+1):

                # Topic will only be populated if the series topic selection option is "pre-determined"
                next_session = {
                "session_id": "session-" + str(session_number),
                "ts": str(int(next_session_dt.timestamp())),
                "presenter": self.state["presenter"],
                "topic": "Not Selected"
                }

                self.sessions.append(next_session)

                # 21 days
                next_session_dt += timedelta(days=21)

        elif frequency == "every-month":
            for session_number in range (1, num_sessions+1):

                # Topic will only be populated if the series topic selection option is "pre-determined"
                next_session = {
                "session_id": "session-" + str(session_number),
                "ts": str(int(next_session_dt.timestamp())),
                "presenter": self.state["presenter"],
                "topic": "Not Selected"
                }

                self.sessions.append(next_session)
                # 28 days
                next_session_dt += timedelta(days=28)

    def getScheduleBlocks(self, series_title):
        """
        Generate the blocks that the series schedule will be composed of. 
        These blocks will be based on the sessions object stored on the current object.

        # TODO hackfix add series_title to be able to display it in schedule message
        Returns the blocks JSON dict object
        """
        # The blocks object starts off empty
        series_schedule_blocks = []

        # Before anything elese, append the title section
        series_schedule_blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Here's the schedule for *" + series_title + "*"
                }
                })


        # Console log for sessions
        print("\n" + 70*"="  + "\nsessions object:... \n", self.sessions, "\n"+ 70*"=")

        # Start appending the sessions
        for session in self.sessions:
            # 1- append the divider
            series_schedule_blocks.append({
                "type": "divider"
                })

            # 2- append the session number
            series_schedule_blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Session " + session["session_id"][8:] + "*"
                        }
                })

            # 3- append the date and time
            series_schedule_blocks.append({
                "type": "section",
		        "text": {
			        "type": "mrkdwn",  
                    #  Using Slack's date formatting, only need a timestamp
			        "text": ":calendar: <!date^" + session["ts"] + "^{date_short_pretty} at {time}|" + datetime.fromtimestamp(int(session["ts"])).strftime("%b %d, %Y at %I:%M %p") + ">"
                    }
                })
            # 4- append the presenter
            series_schedule_blocks.append({
                "type": "section",
		        "text": {
			        "type": "mrkdwn",
			        "text": "\n:microphone: " + "<@" + session["presenter"] + ">"
                        },
                "accessory": {
                    "type": "button",
                    "action_id": "change_presenter_session_" + session["session_id"][8:],
			        "text": {
                        "type": "plain_text",
                        "text": "Change Presenter",
                        "emoji": True
                        },
                    "value": "change_presenter_session_" + session["session_id"][8:]
                    }
                })

            # 5- append the topic
            series_schedule_blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": ":bookmark_tabs: Not Selected"
                    },
                "accessory": {
                    "type": "button",
                    "action_id": "change_topic_session_" + session["session_id"][8:],
                    "text": {
                "type": "plain_text",
                "text": "Change Topic",
                "emoji": True
                },
                "value": "change_presenter_session_" + session["session_id"][8:]
                }
                })

        return series_schedule_blocks

            

