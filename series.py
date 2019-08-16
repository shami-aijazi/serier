import json
from new_series_menu_blocks import new_series_menu_blocks
from edit_series_menu_blocks import edit_series_menu_blocks
import copy

# Make a copy of the blocks so they can be reset to the new blocks if series is cancelled
current_series_menu_blocks = copy.deepcopy(new_series_menu_blocks)
current_edit_series_menu_blocks = copy.deepcopy(edit_series_menu_blocks)
# Console log for copy
# print("\n" + 70*"="  + "\nCopying new blocks to current blocks... \n" + 70*"=")

from datetime import datetime
from datetime import timedelta
import pytz
import sqlite3
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
        # The series_id is needed to update/delete series from db. It will be populated as necessary.
        self.series_id = None
        # Whether or not the new series creation workflow was inititated from the help message button
        # This is useful for knowing when to render a "back" button that returns to the help message
        self.isFromHelp = False

    def newSeries(self, ts, start_date, series_time, menu_tz, IsFromHelp):
        """
        # TODO Should this modify the series itself or return a new series with the changes??

        Set the state to be the default values that the series creation menu will show.

        Parameters
        ----------
        ts: str
            timestamp of the series creation menu message. This is needed to update the message.

        start_date: str
            the default starting date of the series.

        series_time: str
            the default time of the sessions in the series
        
        menu_tz: str
            the timezone associated with the date and time of the series.
        
        IsFromHelp: bool
            Whether or not the new series creation workflow was inititated from the help message button

        """
        self.state = {"title": "My Team's Weekly Brownbag",
                      "presenter": "Not Selected",
                      "topic_selection": "Not Selected",
                      "start_date": start_date,
                      "time": series_time,
                      "frequency": "Not Selected",
                      "num_sessions": 0,
                      "end_date": "N/A"
                    }
        self.menu_ts = ts
        self.timezone = menu_tz
        self.IsFromHelp = IsFromHelp


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

    def loadFromTuple(self, series_tuple, sessions_tuples):
        """
        Sets Series fields to match incoming series tuple.
        The series tuple will be in following format:
        (series_id, title, presenter, topic_selection, start_date, end_date,
         session_start, frequency, num_sessions, is_paused)

        The sessions_tuples will be a list of tuples in the following format:
        (session_id, series_id, session_start, presenter, topic, is_skipped,
         is_done, is_modified)

        TODO deal with is_paused,
        is_skipped, is_done, and is_modified modifiers

        This method will be used to load a series into memory
        from an sqlite database query result set tuple.
        """
        self.state = {"title": series_tuple[1],
                "presenter": series_tuple[2],
                "topic_selection": series_tuple[3],
                "start_date": series_tuple[4],
                "end_date": series_tuple[5],
                "time": series_tuple[6],
                "frequency": series_tuple[7],
                "num_sessions": series_tuple[8],
                
            }
        self.menu_ts = None
        self.timezone = None
        self.series_id = series_tuple[0]

        # Empty the sessions object, ready for refill
        self.sessions = []
        for session_tuple in sessions_tuples:

            next_session = {
                "session_id" : session_tuple[0],
                "ts": session_tuple[2],
                "presenter": session_tuple[3],
                "topic": session_tuple[4]
            }
            self.sessions.append(next_session)


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
        global current_edit_series_menu_blocks

        # Console log for comparing current series menu to a new one
        # print("\n" + 70*"="  + "\nInside resetSeries...\ncurrent and new menu blocks are identical? \n", current_series_menu_blocks == new_series_menu_blocks, "\n" + 70*"=")
        
        # reset the current series menu blocks
        current_series_menu_blocks = copy.deepcopy(new_series_menu_blocks)
        current_edit_series_menu_blocks = copy.deepcopy(edit_series_menu_blocks)

        self.state = {}
        self.menu_ts = ""
        self.timezone = ""
        self.series_id = None
        # self.sessions = []
        


    def getLastSession(self):
        """
        Calculate and update end date based on Start Date date,
        number of sessions, and frequency.
        
        Return end date?
        """

        # Start at the start_date, formatted to be a datetime object
        end_date = datetime.strptime(self.state["start_date"], "%Y-%m-%d")
        
        # Extract frequency and num_sessions
        frequency = self.state["frequency"]
        num_sessions = int(self.state["num_sessions"])


        # Subtract numsessions by 1 to avoid overcounting
        num_sessions -= 1

        if frequency == "every-day":
            # format this correctly
            end_date += timedelta(days=num_sessions)

        elif frequency == "every-weekday":
            # every weekday sequence
            while num_sessions > 0:
                end_date = end_date + timedelta(days=1)
                weekday = end_date.weekday()
                if weekday >= 5: # saturday = 5, sunday = 6
                    continue
                num_sessions -= 1

        elif frequency == "every-week":
            # every week sequence
            end_date += timedelta(days=7*num_sessions)

        elif frequency == "every-2-weeks":
            # every 2 weeks sequence
            end_date += timedelta(days=14*num_sessions)

        elif frequency == "every-3-weeks":
            # every 3 weeks sequence
            end_date += timedelta(days=21*num_sessions)

        elif frequency == "every-month":
            # every month sequency
            end_date += timedelta(days=28*num_sessions)
        
        # Format the datetime object
        end_date = end_date.strftime("%Y-%m-%d")

        # Store the result in state
        self.state["end_date"] = end_date

    def getCreationMenuBlocks(self, fromHelp=False):
        """
        Generate the blocks that the series creation menu will be composed of. 
        These blocks will be based on the current state.

        Parameters
        ----------
        fromHelp: bool
            True if the new series creation workflow came from the help message button,
            False otherwise.


        Returns the blocks JSON dict object
        """
        # Console log series menu completeness
        # print("\n" + 70*"="  + "\nRunning getCreationMenuBlocks... \n" + "series.state=\n", self.state, "\n" + 70*"=")



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

        # If presenter still has not been selected
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


        # ==================== Update Start Date ====================
        # 1- === Update datepicker ===
        current_series_menu_blocks[10]["elements"][0]["initial_date"] = self.state["start_date"]

        
        # 2- === Update summary context ===
        # Format it correctly
        if self.state["start_date"] != "Not Selected":
            current_series_menu_blocks[-2]["elements"][3]["text"] = "*Start Date*: " + datetime.strptime(self.state["start_date"], "%Y-%m-%d").strftime("%m/%d/%Y")

        # ==================== Update Time ====================
        
        # 1- === Update select menu ===
        current_series_menu_blocks[10]["elements"][1]["initial_option"] = {
            "text":
                {"type": "plain_text",
                "text": datetime.strptime(self.state["time"], '%H:%M').strftime('%I:%M %p'),
                "emoji": True},
                # Format the time for the "value" parameter
                "value": "time-" + datetime.strptime(self.state["time"], '%H:%M').strftime('%H%M')
            }
        
        # 2- === Update summary context ===
        current_series_menu_blocks[-2]["elements"][4]["text"] = "*Time*: " + datetime.strptime(self.state["time"], '%H:%M').strftime('%I:%M %p')

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
                    
        # ==================== Update End Date ====================
        # If the frequency and the num_sessions has not been selected
        if self.state["frequency"] != "Not Selected" and self.state["num_sessions"] != 0:
            self.getLastSession()
            current_series_menu_blocks[-2]["elements"][6]["text"] = "*End Date*: " + datetime.strptime(self.state["end_date"], "%Y-%m-%d").strftime("%m/%d/%Y")
        

        # ==================== Add Back Button if Coming From Help====================
        # If this workflow was initiated from the help message (as indicated by fromHelp param)

        if self.IsFromHelp:
            back_to_help_button = {
				"type": "button",
				"action_id": "back_to_help",
				"text": {
					"type": "plain_text",
					"text": "Back",
					"emoji": True
				},
				"value": "from_help_message"
            }
            
            # Add the start button to the menu (if it doesn't already exist)
            if (current_series_menu_blocks[-1]["elements"][0]["action_id"] != "back_to_help" and
                    len(current_series_menu_blocks[-1]["elements"]) < 2):
                current_series_menu_blocks[-1]["elements"].insert(0, back_to_help_button)
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
            
            # Console log for buttons in menu
            # print("\n" + 70*"="  + "\ncurrent_series_menu_blocks[-1][\"elements\"] \n", current_series_menu_blocks[-1]["elements"], "\n" + 70*"=")
            
            # Add the start button to the menu (if it doesn't already exist)
            if (current_series_menu_blocks[-1]["elements"][0]["action_id"] != "start_series" and
                    len(current_series_menu_blocks[-1]["elements"]) < 3):
                current_series_menu_blocks[-1]["elements"].insert(0, start_series_button)
        # else:
        #     # Console log series menu completeness
        #     print("\n" + 70*"="  + "\nSeries menu is NOT complete... \n" + 70*"=")

        # Return it after modifications
        return current_series_menu_blocks

    def getEditMenuBlocks(self):
        """
        Generate the blocks that the series edit menu will be composed of. 
        These blocks will be based on the current state.

        Returns the blocks JSON dict object
        """
        # Console log series menu completeness
        # print("\n" + 70*"="  + "\nRunning getEditMenuBlocks... \n" + "series.state=\n", self.state, "\n" + 70*"=")



        # Update the series edit menu as state changes


        # ==================== Update Title ====================
        # 1- === Update title section ===
        current_edit_series_menu_blocks[3]["text"]["text"] = "*" + self.state["title"] + "*"

        # 2- === Update summary context ===
        current_edit_series_menu_blocks[-2]["elements"][0]["text"] = "*Title*: " + self.state["title"] 

        # ==================== Update Presenter ====================
        # 1- === Update users select menu ===

        current_edit_series_menu_blocks[6]["accessory"]["initial_user"] = self.state["presenter"]

        # 2- === Update summary context ===
        current_edit_series_menu_blocks[-2]["elements"][1]["text"] = "*Presenter*: " +  "<@" + self.state["presenter"] + ">"

        
        # ==================== Update Topic Selection ====================
        
        if self.state["topic_selection"] != "Not Selected":
            
            # 1- === Update select menu ===
            current_edit_series_menu_blocks[7]["accessory"]["initial_option"] = {
                "text":
                    {"type":"plain_text",
                    "text":"Pre-determined",
                    "emoji":True},
                    "value":"pre-determined"
                }

            # 2- === Update summary context ===
            current_edit_series_menu_blocks[-2]["elements"][2]["text"] = "*Topic Selection*: Pre-determined"
            
            # 1- === Update select menu ===
            current_edit_series_menu_blocks[7]["accessory"]["initial_option"] = {
                "text":
                    {"type":"plain_text",
                    "text":"Presenter's Choice",
                    "emoji":True},
                    "value":"presenter_choice"
                }

            # 2- === Update summary context ===
            current_edit_series_menu_blocks[-2]["elements"][2]["text"] = "*Topic Selection*: Presenter's Choice"


        # ==================== Update Start Date ====================
        # 1- === Update datepicker ===
        current_edit_series_menu_blocks[10]["elements"][0]["initial_date"] = self.state["start_date"]

        
        # 2- === Update summary context ===
        # Format it correctly
        current_edit_series_menu_blocks[-2]["elements"][3]["text"] = "*Start Date*: " + datetime.strptime(self.state["start_date"], "%Y-%m-%d").strftime("%m/%d/%Y")

        # ==================== Update Time ====================
        
        # 1- === Update select menu ===
        current_edit_series_menu_blocks[10]["elements"][1]["initial_option"] = {
            "text":
                {"type": "plain_text",
                "text": datetime.strptime(self.state["time"], '%H:%M').strftime('%I:%M %p'),
                "emoji": True},
                # Format the time for the "value" parameter
                "value": "time-" + datetime.strptime(self.state["time"], '%H:%M').strftime('%H%M')
            }
        
        # 2- === Update summary context ===
        current_edit_series_menu_blocks[-2]["elements"][4]["text"] = "*Time*: " + datetime.strptime(self.state["time"], '%H:%M').strftime('%I:%M %p')

        # ==================== Update Frequency ====================
        # 1- === Update select menu ===
        current_edit_series_menu_blocks[11]["elements"][0]["initial_option"] = {
                "text":
                    {"type": "plain_text",
                    "text": self.state["frequency"].replace("-", " ").title(),
                    "emoji": True},
                    # Format the time for the "value" parameter
                    "value": self.state["frequency"]
                }
                    
        # 2- === Update summary context ===
        current_edit_series_menu_blocks[-2]["elements"][5]["text"] = "*Frequency*: " + self.state["frequency"].replace("-", " ").title()

        # ==================== Update Num_sessions ====================
        # 1- === Update select menu ===
        current_edit_series_menu_blocks[11]["elements"][1]["initial_option"] = {
                "text":
                    {"type": "plain_text",
                    "text": str(self.state["num_sessions"]),
                    "emoji": True},
                    # Format the string for the value parameter
                    "value": "numsessions-" + str(self.state["num_sessions"])
                }
                    
        # ==================== Update End Date ====================
        # Calculate the last session date.
        self.getLastSession()
        current_edit_series_menu_blocks[-2]["elements"][6]["text"] = "*End Date*: " + datetime.strptime(self.state["end_date"], "%Y-%m-%d").strftime("%m/%d/%Y")


        # ==================== Add Update Button If Series Modified ==================== ?
        # TODO If series menu has been modified, add the UPDATE confirmation button?

        # Return it after modifications
        return current_edit_series_menu_blocks

    def createSessions(self, series_id):
        """
        Generate a list of session objects corresponding to the sessions that the series will be composed of.
        Store this list on the Series object.
        Serialize the sessions and commit them to a table in the database

        These sessions will be computed and populated based on the values in the series state.
        Since this method assumes that the series state is full this method should only be called after
        making sure the series menu is complete.
        """
        # Console log for sessions
        print("\n" + 70*"="  + "\nInside createSessions...currentSeries.state = \n", self.state, "\n"+ 70*"=")

        # Extract the frequency and the num_sessions from the series state
        frequency = self.state["frequency"]
        num_sessions = int(self.state["num_sessions"])

        # Extract the series time from state
        series_time = datetime.strptime(self.state["time"],"%H:%M")

        # Get the datetime of the Start Date
        next_session_dt = datetime.strptime(self.state["start_date"], "%Y-%m-%d")
        next_session_dt = next_session_dt.replace(hour=series_time.hour, minute=series_time.minute)

        # Localize the time to the user's timezone (to avoid weekend confusion)
        user_tz = pytz.timezone(self.timezone)
        next_session_dt = pytz.utc.localize(next_session_dt)
        next_session_dt = next_session_dt.astimezone(user_tz)


        # If the frequency is every day
        if frequency == "every-day":
            for session_number in range (1, num_sessions+1):

                # Create a new session for each day, including the first day
                # TODO Topic should only be populated if the series topic selection option is "pre-determined"
                next_session = {
                "ts": str(int(next_session_dt.astimezone(pytz.utc).timestamp())),
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

                # For the Start Date, just add it.
                if session_number == 0:
                    session_number+=1
                    next_session = {
                    "ts": str(int(next_session_dt.astimezone(pytz.utc).timestamp())),
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
                    "ts": str(int(next_session_dt.astimezone(pytz.utc).timestamp())),
                    "presenter": self.state["presenter"],
                    "topic": "Not Selected"
                    }
                    self.sessions.append(next_session)

                

        # If the frequency is every week
        elif frequency == "every-week":
            for session_number in range (1, num_sessions+1):

                # Topic will only be populated if the series topic selection option is "pre-determined"
                next_session = {
                "ts": str(int(next_session_dt.astimezone(pytz.utc).timestamp())),
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
                "ts": str(int(next_session_dt.astimezone(pytz.utc).timestamp())),
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
                "ts": str(int(next_session_dt.astimezone(pytz.utc).timestamp())),
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
                "ts": str(int(next_session_dt.astimezone(pytz.utc).timestamp())),
                "presenter": self.state["presenter"],
                "topic": "Not Selected"
                }

                self.sessions.append(next_session)
                # 28 days
                next_session_dt += timedelta(days=28)

        
        # Now that all the sessions have been created, commit them to a db
        # Console log for sessions
        # print("\n" + 70*"="  + "\nAbout to serialize sessions...currentSeries.sessions = \n", self.sessions, "\n"+ 70*"=")
        
        # TODO Put these in subroutines (make it resuable)
        # DATABASE OPERATIONS
        # First, connect to the sqlite3 database
        con = sqlite3.connect("serier.db")
        
        # Create a cursor
        cur = con.cursor()

        # Iterate through the sessions list and add them to the database.
        # TODO: Later, probably just want to commit them to db AS we are creating them (a few lines up in the code)
        for session in self.sessions:
            
            # Prepare the statement and the values
            session_record = (series_id, session["ts"], session["presenter"], session["topic"],
                            0, 0, 0) # The last three 0s are the boolean false for is_skipped, is_done, and is_modified respectively

            sql_statement = ''' INSERT INTO sessions(series_id,session_start,presenter,topic,
                                                    is_skipped, is_done, is_modified)
                VALUES(?,?,?,?,?,?,?) '''

            # Execute the insertion
            cur.execute(sql_statement, session_record)

            # Store the session_id of the session that was just serialized on the session object.
            session["session_id"] = cur.lastrowid


        # commit and close the database connection
        con.commit()
        con.close()
    def deleteSessions(self, series_id):
        """

        Delete the sessions associated with a series from database.

        NOTE: This method is useful during edit of a series. First, all the
        sessions will be deleted, and then they will be repopulated with new updated properties.
        """
        # Console log for sessions
        print("\n" + 70*"="  + "\nInside deleteSessions...currentSeries.state = \n", self.state, "\n"+ 70*"=")
        print("deleting sessions from series with series_id =", self.series_id, "| type of series_id =", type(series_id))
        
        
        # TODO Put these in subroutines (make it resuable)
        # DATABASE OPERATIONS
        # First, connect to the sqlite3 database
        con = sqlite3.connect("serier.db")
        
        # Create a cursor
        cur = con.cursor()

            
        # Prepare the statement and the values
        session_record = (str(series_id),)

        sql_statement = ''' DELETE FROM sessions
                            WHERE series_id = ''' + str(series_id)
        # Execute the insertion
        cur.execute(sql_statement)


        # commit and close the database connection
        con.commit()
        con.close()

        # Then, clear the sessions from memory
        self.sessions = []

    def getScheduleBlocks(self, series_title, sessions, isFromConfirmation):
        """
        Generate the blocks that the series schedule will be composed of. 
        These blocks will be based on the sessions parameter.

        Set the state to be the default values that the series creation menu will show.

        Parameters
        ----------
        series_title: str
            title of the series the schedule is for

        sessions: list of dicts
            a list of JSON session objects
        
        isFromConfirmation: bool
            (Optional) Whether or not the schedule printing request came from the series creation confirmation.

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
        # print("\n" + 70*"="  + "\nsessions object:... \n", sessions, "\n"+ 70*"=")

        # Start appending the sessions

        # This will number the sessions
        session_index = 0
        for session in sessions:
            # 1- append the divider
            series_schedule_blocks.append({
                "type": "divider"
                })

            # 2- append the session number
            series_schedule_blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        # Increment the session number by one to shift zero-indexing
                        "text": "*Session " + str(session_index + 1) + "*"
                        }
                })

            # 3- append the date and time
            series_schedule_blocks.append({
                "type": "section",
		        "text": {
			        "type": "mrkdwn",  
                    #  Using Slack's date formatting, only need a timestamp
			        "text": ":calendar: <!date^" + str(session["ts"]) + "^{date_short_pretty} at {time}|" + datetime.fromtimestamp(int(session["ts"])).strftime("%b %d, %Y at %I:%M %p") + ">"
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
                    "action_id": "change_session_presenter",
			        "text": {
                        "type": "plain_text",
                        "text": "Change Presenter",
                        "emoji": True
                        },
                    
                    # Format of value string: session_index-(session_index)   Example: session_index-1 OR session_index-13
                    "value": "session_index-" + str(session_index)
                    }
                })

            # 5- append the topic
            series_schedule_blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": ":bookmark_tabs:" + session["topic"]
                    },
                "accessory": {
                    "type": "button",
                    "action_id": "change_session_topic",
                    "text": {
                        "type": "plain_text",
                        "text": "Change Topic",
                        "emoji": True
                        },
                    "value": "session_index-" + str(session_index)
                }
                })

            # Increment the session counter
            session_index += 1

        # Appendage to the schedule message that contains the button to go back and the button to hide the message.

        # Do not add a "back" button if the schedle reqeust workflow came via the button in the series creation confirmation message
        if isFromConfirmation:
            appendage_blocks = [  
                {  
                    "type":"divider"
                },
                {  
                    "type":"section",
                    "text":{  
                    "type":"mrkdwn",
                    "text":"*End of schedule message.*"
                    }
                },
                {  
                    "type":"actions",
                    "elements":[{  
                            "type":"button",
                            "action_id":"hide_schedule_message",
                            "text":{  
                            "type":"plain_text",
                            "text":"Hide Schedule",
                            "emoji":True
                            },
                            "value":"hide_schedule_message"
                        }
                    ]
                }
                ]
        else:
            appendage_blocks = [  
            {  
                "type":"divider"
            },
            {  
                "type":"section",
                "text":{  
                "type":"mrkdwn",
                "text":"*End of schedule message.*"
                }
            },
            {  
                "type":"actions",
                "elements":[  
                    {  
                        "type":"button",
                        "action_id":"back_to_view",
                        "text":{  
                        "type":"plain_text",
                        "text":"Back",
                        "emoji":True
                        },
                        "value":"from_schedule_message"
                    },
                    {  
                        "type":"button",
                        "action_id":"hide_schedule_message",
                        "text":{  
                        "type":"plain_text",
                        "text":"Hide Schedule",
                        "emoji":True
                        },
                        "value":"hide_schedule_message"
                    }
                ]
            }
            ]


        series_schedule_blocks.extend(appendage_blocks)


        return series_schedule_blocks

            

