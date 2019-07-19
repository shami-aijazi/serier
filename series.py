import json
from new_series_menu_blocks import new_series_menu_blocks
from datetime import datetime
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
                      "first_session": "Not Selected",
                      "time": "Not Selected",
                      "frequency": "Not Selected",
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
        self.state = {}

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
        new_series_menu_blocks[3]["text"]["text"] = "*" + self.state["title"] + "*"

        # 2- === Update summary context ===
        new_series_menu_blocks[-2]["elements"][0]["text"] = "*Title*: " + self.state["title"] 

        # ==================== Update Presenter ====================
        # 1- === Update users select menu ===
        # If presenter still has already been selected
        if self.state["presenter"] != "Not Selected":
            new_series_menu_blocks[6]["accessory"]["initial_user"] = self.state["presenter"]

        # 2- === Update summary context ===
        # If the presenter still has not been selected
        if self.state["presenter"] == "Not Selected":
            new_series_menu_blocks[-2]["elements"][1]["text"] = "*Presenter*: " +  self.state["presenter"]
        else:
            new_series_menu_blocks[-2]["elements"][1]["text"] = "*Presenter*: " +  "<@" + self.state["presenter"] + ">"

        
        # ==================== Update Topic Selection ====================
        
        if self.state["topic_selection"] != "Not Selected":
            
            # 1- === Update select menu ===
            if self.state["topic_selection"] == "pre-determined":
                new_series_menu_blocks[7]["accessory"]["initial_option"] = {
                    "text":
                        {"type":"plain_text",
                        "text":"Pre-determined",
                        "emoji":True},
                        "value":"pre-determined"
                    }

                # 2- === Update summary context ===
                new_series_menu_blocks[-2]["elements"][2]["text"] = "*Topic Selection*: Pre-determined"
            
            # 1- === Update select menu ===
            elif self.state["topic_selection"] == "presenter_choice":
                new_series_menu_blocks[7]["accessory"]["initial_option"] = {
                    "text":
                        {"type":"plain_text",
                        "text":"Presenter's choice",
                        "emoji":True},
                        "value":"presenter_choice"
                    }

                # 2- === Update summary context ===
                new_series_menu_blocks[-2]["elements"][2]["text"] = "*Topic Selection*: Presenter's choice"


        # ==================== Update First Session Date ====================
        # 1- === Update datepicker ===
        if self.state["first_session"] != "Not Selected":
            new_series_menu_blocks[10]["elements"][0]["initial_date"] = self.state["first_session"]

        
        # 2- === Update summary context ===
        # Format it correctly
        if self.state["first_session"] != "Not Selected":
            new_series_menu_blocks[-2]["elements"][3]["text"] = "*First Session*: " + datetime.strptime(self.state["first_session"], "%Y-%m-%d").strftime("%m/%d/%Y")

        # ==================== Update Time ====================
        
        # 1- === Update select menu ===
        if self.state["time"] != "Not Selected":
            new_series_menu_blocks[10]["elements"][1]["initial_option"] = {
                "text":
                    {"type": "plain_text",
                    "text": self.state["time"],
                    "emoji": True},
                    # Format the time for the "value" parameter
                    "value": "time-" + datetime.strptime(self.state["time"], '%I:%M %p').strftime('%H%M')
                }
        
        # 2- === Update summary context ===
        new_series_menu_blocks[-2]["elements"][4]["text"] = "*Time*: " + self.state["time"]

        # ==================== Update Frequency ====================
        # 1- === Update select menu ===
        if self.state["frequency"] != "Not Selected":
            new_series_menu_blocks[11]["elements"][0]["initial_option"] = {
                    "text":
                        {"type": "plain_text",
                        "text": self.state["frequency"].replace("-", " ").title(),
                        "emoji": True},
                        # Format the time for the "value" parameter
                        "value": self.state["frequency"]
                    }
                    
        # 2- === Update summary context ===
        new_series_menu_blocks[-2]["elements"][5]["text"] = "*Frequency*: " + self.state["frequency"].replace("-", " ").title()

        # ==================== Update Last Session Date ====================
        new_series_menu_blocks[-2]["elements"][6]["text"] = "*Last Session*: " + self.state["last_session"]


        # Return it after modifications
        return new_series_menu_blocks

