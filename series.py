import json
from new_series_menu_blocks import new_series_menu_blocks
import copy

# Make a copy of the blocks so they can be reset to the new blocks if series is cancelled
current_series_menu_blocks = copy.deepcopy(new_series_menu_blocks)
# Console log for copy
# print("\n" + 70*"="  + "\nCopying new blocks to current blocks... \n" + 70*"=")


from datetime import datetime
from datetime import timedelta
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
        self.menu_ts ={}

    def newSeries(self, ts):
        """
        # TODO Should this modify the series itself or return a new series with the changes??


        Set the state to be the default values that the series creation menu will show.
        Also, save the timestamp of the original message menu on the object (needed to update it)
        """
        self.state = {"title": "My Team's Weekly Brownbag",
                      "presenter": "Not Selected",
                      "topic_selection": "Not Selected",
                      "first_session": datetime.today().date().strftime("%Y-%m-%d"),
                      "time": "Not Selected",
                      "frequency": "Not Selected",
                      "num_sessions": 0,
                      "last_session": "N/A"
                    }
        self.menu_ts = ts

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


        if frequency == "every-day":
            # format this correctly
            last_session += timedelta(days=num_sessions)

        elif frequency == "every-weekday":
            # every weekday sequence
            while num_sessions > 0:
                last_session = last_session + timedelta(days=1)
                weekday = last_session.weekday()
                if weekday >= 5: # sunday = 6
                    continue
                num_sessions -= 1

        elif frequency == "every-2-weeks":
            # every 2 weeks sequence
            last_session = last_session + timedelta(days=14*num_sessions)

        elif frequency == "every-3-weeks":
            # every 3 weeks sequence
            last_session = last_session + timedelta(days=21*num_sessions)

        elif frequency == "every-month":
            # every month sequency
            last_session = last_session + timedelta(days=28*num_sessions)
        
        # Format the datetime object
        last_session = last_session.strftime("%m/%d/%Y")

        # Store the result in state
        self.state["last_session"] = last_session

    def getBlocks(self):
        """
        Generate the blocks that the series creation menu will be composed of. 
        These blocks will be based on the current state.

        Returns the blocks JSON dict object
        """
        # TODO You probably want to change the fields themselves. Not just the sumamry context.
        # You want the team name field to change, you want the datpicker selected date to reflect
        # state, and so on.

        # NOTE As state changes, the thing that changes is the summary of the series
        # creation menu message. This is a context section (which is the second last section
        # before the submit and cancel buttons)

        # ==================== Update Title ====================
        # 1- === Update title section ===
        current_series_menu_blocks[3]["text"]["text"] = "*" + self.state["title"] + "*"

        # 2- === Update summary context ===
        current_series_menu_blocks[-2]["elements"][0]["text"] = "*Title*: " + self.state["title"] 

        # ==================== Update Presenter ====================
        # 1- === Update users select menu ===
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
                        "text":"Presenter's choice",
                        "emoji":True},
                        "value":"presenter_choice"
                    }

                # 2- === Update summary context ===
                current_series_menu_blocks[-2]["elements"][2]["text"] = "*Topic Selection*: Presenter's choice"


        # ==================== Update First Session Date ====================
        # 1- === Update datepicker ===
        if self.state["first_session"] != "Not Selected":
            current_series_menu_blocks[10]["elements"][0]["initial_date"] = self.state["first_session"]

        
        # 2- === Update summary context ===
        # Format it correctly
        if self.state["first_session"] != "Not Selected":
            current_series_menu_blocks[-2]["elements"][3]["text"] = "*First Session*: " + datetime.strptime(self.state["first_session"], "%Y-%m-%d").strftime("%m/%d/%Y")

        # ==================== Update Time ====================
        
        # 1- === Update select menu ===
        if self.state["time"] != "Not Selected":
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
        print("frequency = ", self.state["frequency"])
        print("num_sessions = ", self.state["num_sessions"])

        if self.state["frequency"] != "Not Selected" and self.state["num_sessions"] != 0:
            self.getLastSession()
        current_series_menu_blocks[-2]["elements"][6]["text"] = "*Last Session*: " + self.state["last_session"]


        # Return it after modifications
        return current_series_menu_blocks

