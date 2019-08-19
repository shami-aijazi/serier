"""
Slack Bot class for use with series organizer app
"""
import os
import message
import json

from slack import WebClient
from datetime import datetime
from datetime import timedelta
import pytz

import sqlite3

# import the series class and construct an empty Series object
from series import Series
currentSeries = Series()

# To remember which teams have authorized your app and what tokens are
# associated with each team, we can store this information in memory on
# as a global object. When your bot is out of development, it's best to
# save this in a more persistant memory store.
authed_teams = {}

class Bot(object):
    """ Instatiates a Bot object to handle Slack interactions"""
    def __init__(self):
        super(Bot, self).__init__()
        self.name = "Serier"
        # When we instantiate a new bot object, we can access the app
        # credentials we set earlier in our local development environment.
        self.oauth = {"client_id": os.environ.get("CLIENT_ID"),
                      "client_secret": os.environ.get("CLIENT_SECRET"),
                      # Scopes provide and limit permissions to what our app
                      # can access. It's important to use the most restricted
                      # scope that your app will need.
                      "scope": "bot"}
        self.signing_secret = os.environ.get("SIGNING_SECRET")
        # self.emoji = ":space_invader:"

        # NOTE: Python-slack requires a client connection to generate
        # an oauth token. We can connect to the client without authenticating
        # by passing an empty string as a token and then reinstantiating the
        # client with a valid OAuth token once we have one.
        self.client = WebClient("")

    def client_connect(self, team_id):
        # TODO make this connect to database instead of file
        """
        Connect to the Slack web client corresponding to the team.

        Parameters
        ----------
        team_id : str
            id of the Slack team associated with incoming event

        Returns
        ----------
        connected : bool
            True if connection successful, False otherwise.

        """
        # Read the authed_teams from file
        with open('authed_teams.txt', 'r') as authed_teams_file:  
            authed_teams = json.load(authed_teams_file)

        if authed_teams.get(team_id, False):
          self.client = WebClient(authed_teams[team_id]["bot_token"])
          return True

        else: #team_id not found in authed_teams
        # TODO helpful error message
          return False


# ============================= BASIC BOT STUFF =============================
    def open_dm(self, user_id):
        """
        Open a DM channel with a user.

        Parameters
        ----------
        team_id : str
            id of the Slack team associated with event
        user_id : str
            id of the Slack user to open DM with 

        Returns
        ----------
        dm_id : str
            id of the DM channel opened by this method
        """
        new_dm = self.client.im_open(
                                    user=user_id
                                    )

        # console log for the new_dm im.open response object
        # print("\n" + 70*"="  + "\nnew_dm=\n", new_dm, "\n" + 70*"=")

        dm_id = new_dm["channel"]["id"]
        return dm_id

    def onboarding_message(self, user_id):
        """
        Create and send a welcome message to a new user upon installation.
        :param team_id: str
            id of the Slack team associated with the incoming event
        :param user_id: str
            id of the Slack user associated with the incoming event

        """

        # create a Greeting message Message object

        message_obj = message.Onboarding()

        # Then we'll set the message object's channel attribute to the IM
        # channel of the user we'll communicate with. We'll find this using
        # the open_dm function, which uses the im.open API call.
        message_obj.channel = self.open_dm(user_id)

        post_message = self.client.chat_postMessage(
                                            channel=message_obj.channel,
                                            username=self.name,
                                            # icon_emoji=self.emoji,
                                            text=message_obj.text,
                                            blocks=message_obj.blocks
                                            )
    def greeting_message(self, user_id, channel_id):
        """
        Create and send a response to a user saying hi.
        :param user_id: str
            id of the Slack user to send the greeting message to
        :param channel_id: str
            id of the Slack channel to send the greeting on
        """

        # create a Greeting message Message object

        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Hi, <@" + user_id + "> :wave:"
                }
            }
        ]

        post_message = self.client.chat_postMessage(
                                            channel=channel_id,
                                            username=self.name,
                                            # icon_emoji=self.emoji,
                                            text="Hi!",
                                            blocks=blocks
                                            )


    def dm_response_message(self, channel_id):
        """
        Create and send a default response message to a user who DM's the bot.
        This is the default message that is sent when the bot doesn't understand
        what the user said.
        :param team_id: str
            id of the Slack team associated with the incoming event
        :param channel_id: str
            id of the Slack channel associated with the incoming event

        """

        # Create the message blocks
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Sorry, I didn't get that. You can type `help` to find out what I can do!"
                }
            }
        ]

        post_message = self.client.chat_postMessage(
                                            channel=channel_id,
                                            username=self.name,
                                            # icon_emoji=self.emoji,
                                            text="Sorry, I didn't get that. You can type `help` to find out what I can do!",
                                            blocks=blocks
                                            )
                                            
    def send_help_message(self, channel_id, message_ts=0):
        """
        Create and send a response message to a user who DM's the bot.

        Parameters
        ----------
        channel_id: str
            id of the Slack channel associated with the incoming event

        NOTE: the timestamp parameter is defaulted to zero. If one is passed, then
        this will be the result of the "back" button pressed in the help. 
        Otherwise, the help is being initiated from a message/slashcommand.
        """
        blocks = [
            {
                "type":"section",
                "text":{
                    "type":"mrkdwn",
                    "text":"Hi! This is Serier. Serier can help you manage a bookclub or a brownbag series :books:\nHere's how:"
                }
            },
            {
                "type":"section",
                "text":{
                    "type":"mrkdwn",
                    "text":"*Start a Series*\nYou can start a series with `/serier create` or by pressing this button:"
                }
            },
            {
                "type":"actions",
                "elements":[
                    {
                        "type":"button",
                        "action_id":"create_new_series",
                        "text":{
                            "type":"plain_text",
                            "text":"Start a Series",
                            "emoji":True
                        },
                        "value":"from_help_message"
                    }
                ]
            },
            {
                "type":"divider"
            },
            {
                "type":"section",
                "text":{
                    "type":"mrkdwn",
                    "text":"*Edit a Series*\nYou can edit an ongoing series with `/serier edit` or by pressing this button:"
                }
            },
            {
                "type":"actions",
                "elements":[
                    {
                        "type":"button",
                        "action_id":"back_to_editing",
                        "text":{
                            "type":"plain_text",
                            "text":"Edit a Series",
                            "emoji":True
                        },
                        "value":"from_help_message"
                    }
                ]
            },
            {
                "type":"divider"
            },
            {
                "type":"section",
                "text":{
                    "type":"mrkdwn",
                    "text":"*View Schedule*\nYou can view the schedule for an ongoing series with `/serier schedule` or by pressing this button:"
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
                            "text":"View Series Schedule",
                            "emoji":True
                        },
                        "value":"from_help_message"
                    }
                ]
            },
            {
                "type":"divider"
            },
            {
                "type":"divider"
            },
            {
                "type":"section",
                "text":{
                    "type":"mrkdwn",
                    "text":"*More:*"
                }
            },
            {
                "type":"actions",
                "elements":[
                    {
                        "type":"button",
                        "action_id":"show_app_commands",
                        "text":{
                            "type":"plain_text",
                            "text":"Serier Commands",
                            "emoji":True
                        },
                        "value":"from_help_message"
                    },
                    {
                        "type":"button",
                        "action_id":"close_help_message",
                        "text":{
                            "type":"plain_text",
                            "text":"Close Help",
                            "emoji":True
                        },
                        "value":"from_help_message"
                    }
                ]
            }
        ]
        # If the help message is being initiated, post a help message.
        if message_ts == 0:
            post_message = self.client.chat_postMessage(
                                            channel=channel_id,
                                            username=self.name,
                                            # icon_emoji=self.emoji,
                                            text="Serier Help Message",
                                            blocks=blocks
                                        )
        
        # If the user pressed back in the next step (a ts is provided), 
        # then update the message
        else:
            update_message = self.client.chat_update(
                                channel=channel_id,
                                ts=message_ts,
                                username=self.name,
                                # icon_emoji=self.emoji,
                                text="Serier Help Message",
                                blocks=blocks
                            )


                                        
# ============================= SERIES BOT LOGIC =============================
    def new_series_menu(self, channel_id, user_id, ts=0, isFromHelp=False):
        """
        Create new series. Update message with parameter ts to show the new series
        creation menu. Use the user_id to get the timezone of the user and update the
        series state's datetime accordingly.

        Parameters
        ----------
        channel_id : str
            id of the Slack channel associated with incoming event
        
        user_id : str
            id of the user_id creating the new series

        ts : str
            timestamp of the series creation button message, if that's how the
            the user is creating a new series. If series is being created from
            a slash command, this is disregarded.

        isFromHelp : bool
            Whether or not the series creation workflow is from the help message button.
        """

        # Get the user's info to extract the timezone
        user_info = self.client.users_info(
                                            user=user_id
                                            )
        # Console log for user info
        # print("\n" + 70*"="  + "\nuser_info=\n", user_info, "\n" + 70*"=")

        # The PyTZ timezone string
        user_tz = user_info["user"]["tz"]
        # Console log for user timezone
        # print("\n" + 70*"="  + "\nuser_tz=\n", user_tz, "\n" + 70*"=")


        now_user_tz = datetime.now(pytz.timezone(user_tz))

        # Find difference from nearest future 15 minute mark
        delta = 15 - now_user_tz.minute % 15

        # Add that amount of minutes so the time is to the nearest 15 mins
        now_user_tz += timedelta(minutes=delta)

        # Set the series start date and series_time
        series_start_date = now_user_tz.strftime("%Y-%m-%d")
        series_time = now_user_tz.strftime('%H:%M')

        # Populate the series object with default values
        # Save the timestamp of the menu message on the series object
        # NOTE: the ts might be zero.
        currentSeries.newSeries(ts, series_start_date, series_time, user_tz, isFromHelp)

        # Update the last message if the timestamp is not 0. (it's from button NOT slash)
        if ts != 0:
            update_message = self.client.chat_update(
                                            channel=channel_id,
                                            username=self.name,
                                            # icon_emoji=self.emoji,
                                            text="Create new series",
                                            ts=currentSeries.menu_ts,
                                            blocks=currentSeries.getCreationMenuBlocks()
                                            )
        
        else:
            # If the ts is not zero AKA the series creation was via slash command.
            post_message = self.client.chat_postMessage(
                                            channel=channel_id,
                                            username=self.name,
                                            # icon_emoji=self.emoji,
                                            text="Create new series",
                                            blocks=currentSeries.getCreationMenuBlocks()
                                            )

            # set the series menu timestamp to the post_message ts for menu editing
            currentSeries.menu_ts = post_message["ts"]


    def confirm_new_series(self, channel_id, organizer_id, message_ts):
        """
        Confirm the creation of the new series. Check if the time and date set is not in the
        past. Commit the series to db and send an acknowledgement message.

        """
        # Get the timezone of the creating user at the time of series creation
        user_tz = pytz.timezone(currentSeries.timezone)

        # Create a datetime object from the series data
        series_time = datetime.strptime(currentSeries.state["time"], '%H:%M')
        start_date_date = datetime.strptime(currentSeries.state["start_date"], "%Y-%m-%d")
        start_date_dt = start_date_date.replace(hour=series_time.hour, minute=series_time.minute)

        # Use the timezone and the series data to convert the time to UTC
        user_local_dt = user_tz.localize(start_date_dt)
        utc_dt = user_local_dt.astimezone(pytz.utc)

        
        # Compare the scheduled time to the time now
        utc_now = datetime.now(pytz.utc)

        if utc_dt < utc_now:
            # If the series is scheduled for the past
            # Send a warning message
            post_message = self.client.chat_postMessage(
                                            channel=channel_id,
                                            username=self.name,
                                            # icon_emoji=self.emoji,
                                            text="Series schedule for the past",
                                            blocks=[  
                                            {  
                                                "type":"section",
                                                "text":{  
                                                "type":"mrkdwn",
                                                "text":":warning:Your series is scheduled to start in the past. Please pick a time in the future."
                                                }
                                            },
                                            {  
                                                "type":"actions",
                                                "elements":[  
                                                {  
                                                    "type":"button",
                                                    "action_id":"past_schedule_ok",
                                                    "text":{  
                                                    "type":"plain_text",
                                                    "text":"OK",
                                                    "emoji":True
                                                    },
                                                    "value":"past_schedule_ok"
                                                }
                                                ]
                                            }
                                            ]
                                        )

        # If there is no problem with the series state
        # Give the go ahead
        else:
            
            # TODO edit the series state to be what we want to serialize
            # Update time and first session to be UTC

            currentSeries.state["time"] = utc_dt.time().strftime("%H:%M")
            currentSeries.state["start_date"] = utc_dt.date().strftime("%Y-%m-%d")



            # Update end_date to be UTC
            end_date_date = datetime.strptime(currentSeries.state["end_date"], "%Y-%m-%d")
            user_local_dt = user_tz.localize(end_date_date)
            end_date_utc = user_local_dt.astimezone(pytz.utc)
            currentSeries.state["end_date"] = end_date_utc.strftime("%Y-%m-%d")


            # series_dict = {organizer_id: [currentSeries.state]}


            # TODO Put these in subroutines (make it resuable)
            # DATABASE OPERATIONS
            # First, connect to the sqlite3 database
            con = sqlite3.connect("serier.db")
            # Create a cursor
            cur = con.cursor()

            # First, insert the series into the series table.
            # Prepare the statement and the values
            series_record = (currentSeries.state["title"], currentSeries.state["presenter"], currentSeries.state["topic_selection"],
                            currentSeries.state["start_date"], currentSeries.state["end_date"], currentSeries.state["time"],
                            currentSeries.state["frequency"], currentSeries.state["num_sessions"], 0) # The last 0 is the boolean false for is_paused

            sql_statement = ''' INSERT INTO series(title,presenter,topic_selection,start_date,end_date,
                                                   session_start, frequency, num_sessions, is_paused)
              VALUES(?,?,?,?,?,?,?,?,?) '''

            # Execute the insertion
            cur.execute(sql_statement, series_record)

            # Save the ID of the series that was just inserted
            current_series_id = cur.lastrowid

            # Second, insert the organizer into the organizers table
            # Prepare the statement and the values
            organizer_record = (organizer_id, current_series_id)
            sql_statement = ''' INSERT INTO organizers(user_id,series_id)
              VALUES(?,?) '''

            # Execute the insertion
            cur.execute(sql_statement, organizer_record)


            # commit and close the database connection
            con.commit()
            con.close()

            # Console log for database
            # print("\n" + 70*"="  + "\nJust inserted the series to database...series_id=\n", current_series_id, "\n" + 70*"=")
            

            
            # Send a confirmation message to the user that their series has been created
            update_message = self.client.chat_update(
                                            channel=channel_id,
                                            username=self.name,
                                            # icon_emoji=self.emoji,
                                            ts=currentSeries.menu_ts,
                                            text="Your Series *" + currentSeries.state["title"] + "* has been created",
                                            blocks=[
                                                {
                                                    "type": "section",
                                                    "text": {
                                                        "type": "mrkdwn",
                                                        "text": "Your series *" + currentSeries.state["title"] + "* has been successfully created!\n"
                                                    }
                                                },
                                                {
                                                    "type": "actions",
                                                    "elements": [
                                                        {
                                                            "type": "button",
                                                            "action_id": "series_creation_ok",
                                                            "text": {
                                                                "type": "plain_text",
                                                                "text": "OK",
                                                                "emoji": True
                                                            },
                                                            "value": "series_creation_ok"
                                                        },
                                                        # Add a button to show the schedule of the series that was just created
                                                        {
                                                            "type": "button",
                                                            "action_id": "confirm_view_series",
                                                            "text": {
                                                                "type": "plain_text",
                                                                "text": "View Schedule",
                                                                "emoji": True
                                                            },
                                                            # The value is in the format: "series-id-{series_id}" example: "series_id-3230"
                                                            "value": "series_id-" + str(current_series_id)
                                                        }
                                                    ]
                                                }
                                            ]
                                        )

            # Console log for populating sessions
            # print("\n" + 70*"="  + "\nAbout to set the sessions...\ncurrentSeries.state=\n", currentSeries.state, "\n" + 70*"=")
            # Now that the series has the go ahead, create the sessions
            # This method creates and serializes a list of JSON session objects.
            # It stores these sessions on the Series object.
            # TODO Unnecessary to store it on Series object right?
            currentSeries.createSessions(current_series_id)

    
    def printSchedule(self, channel_id, message_ts, isFromConfirmation=False):
        """
        Print the schedule associated with all the sessions in currentSeries object.
        Assumes that the currentSeries object that is set is the series whose schedule needs to be shown.

        Parameters
        ----------
        channel_id : str
            ID of the Slack channel to send the schedule to
        message_ts : str
            Timestamp of the slack message to update
        isFromConfirmation : bool
            (Optional) Whether or not the schedule printing request came from the series creation confirmation.

        """

        series_title = currentSeries.state["title"]

        # Then, post the schedule message
        update_message = self.client.chat_update(
                                        channel=channel_id,
                                        username=self.name,
                                        # icon_emoji=self.emoji,
                                        text="Here's the schedule for your series *" + series_title + "*",
                                        ts=message_ts,
                                        blocks=currentSeries.getScheduleBlocks(series_title, currentSeries.sessions, isFromConfirmation)
                                    )



    def cancel_new_series(self, channel_id):
        """
        Cancel a new series. Update message with parameter ts to show the series
        canellation confirmation. Revert series state to default
        """

        update_message = self.client.chat_update(
                                            channel=channel_id,
                                            username=self.name,
                                            # icon_emoji=self.emoji,
                                            text="Your series has been successfully cancelled",
                                            ts=currentSeries.menu_ts,
                                            blocks=[{"type": "section",
                                                    "text": {
                                                    "type": "mrkdwn",
                                                    "text": "Your series has been successfully cancelled."
                                                        }
                                                    }
                                                ]
                                            )

        # Reset the series state
        currentSeries.resetSeries()
        currentSeries.sessions = []
        
    def edit_series_title_dialog(self, trigger_id):
        """
        Open the edit series title dialog

        Parameters
        ----------
        trigger_id : str
            trigger_id of the edit series action to open a dialog

        """

        dialog_data = {
                "callback_id": "update_series_title",
                "title": "Edit Title",
                "elements": [
                    {
                        "type": "text",
                        "value": currentSeries.state["title"],
                        "label": "Edit Title",
                        "name": "series_title"
                    }
                ]
            }

        open_dialog =  self.client.dialog_open(
                                            dialog=dialog_data,
                                            trigger_id=trigger_id
                                            )

    def update_series_title(self, channel_id, series_title):
        """
        Update the series title. Make the series_title parameter the title of the series
        """
        # Update the series presenter
        currentSeries.updateSeries("title", series_title)

        # Console log of updated series title
        # print("\n" + 70*"="  + "\nUpdating Series Title...\ncurrentSeries.state=\n", currentSeries.state, "\n" + 70*"=")


        # If the currentSeries is being updated NOT created from scratch.
        # The currentSeries object only has a series_id field if it is being
        # updated. NOT if it is being created for the first time. The series_id
        # field is only populated if the series is loaded from an SQL query.
        # This will determine which blocks to load.
        if not currentSeries.series_id:
            blocks = currentSeries.getCreationMenuBlocks()
        
        else:
            blocks = currentSeries.getEditMenuBlocks()

        update_message = self.client.chat_update(
                                            channel=channel_id,
                                            username=self.name,
                                            # icon_emoji=self.emoji,
                                            text="Your series title has been updated",
                                            ts=currentSeries.menu_ts,
                                            blocks=blocks
                                            )

    def update_series_presenter(self, channel_id, user_id):
        """
        Update the series presenter. Make user_id parameter the presenter for the series
        """
        # Update the series presenter
        currentSeries.updateSeries("presenter", user_id)

        # Console log of updated series presenter
        # print("\n" + 70*"="  + "\nUpdating Series Presenter...\ncurrentSeries.state=\n", currentSeries.state, "\n" + 70*"=")

        # If the currentSeries is being updated NOT created from scratch.
        # The currentSeries object only has a series_id field if it is being
        # updated. NOT if it is being created for the first time. The series_id
        # field is only populated if the series is loaded from an SQL query.
        # This will determine which blocks to load.
        if not currentSeries.series_id:
            blocks = currentSeries.getCreationMenuBlocks()
        
        else:
            blocks = currentSeries.getEditMenuBlocks()

        update_message = self.client.chat_update(
                                            channel=channel_id,
                                            username=self.name,
                                            # icon_emoji=self.emoji,
                                            text="Your series title has been updated",
                                            ts=currentSeries.menu_ts,
                                            blocks=blocks
                                            )

    def update_topic_selection(self, channel_id, topic_selection):
        """
        Update the series topic selection method. The topic_selection is either
        "pre-determined" or "presenter_choice"
        """
        # Update the series presenter
        currentSeries.updateSeries("topic_selection", topic_selection)

        # Console log of updated series topic_selection
        # print("\n" + 70*"="  + "\nUpdating Series Topic Selection...\ncurrentSeries.state=\n", currentSeries.state, "\n" + 70*"=")

        # If the currentSeries is being updated NOT created from scratch.
        # The currentSeries object only has a series_id field if it is being
        # updated. NOT if it is being created for the first time. The series_id
        # field is only populated if the series is loaded from an SQL query.
        # This will determine which blocks to load.
        if not currentSeries.series_id:
            blocks = currentSeries.getCreationMenuBlocks()
        
        else:
            blocks = currentSeries.getEditMenuBlocks()

        update_message = self.client.chat_update(
                                            channel=channel_id,
                                            username=self.name,
                                            # icon_emoji=self.emoji,
                                            text="Your series title has been updated",
                                            ts=currentSeries.menu_ts,
                                            blocks=blocks
                                            )

    def update_series_time(self, channel_id, series_time):
        """
        Update the series time. series_time str format: '%I:%M %p'
        """
        # Update the series state time

        # Convert the series time to "%H:%M" and store it in state
        series_time = datetime.strptime(series_time, '%I:%M %p').strftime('%H:%M')
        currentSeries.updateSeries("time", series_time)

        # Console log of updated series time
        # print("\n" + 70*"="  + "\nUpdating Series Time...\ncurrentSeries.state=\n", currentSeries.state, "\n" + 70*"=")

        # If the currentSeries is being updated NOT created from scratch.
        # The currentSeries object only has a series_id field if it is being
        # updated. NOT if it is being created for the first time. The series_id
        # field is only populated if the series is loaded from an SQL query.
        # This will determine which blocks to load.
        if not currentSeries.series_id:
            blocks = currentSeries.getCreationMenuBlocks()
        
        else:
            blocks = currentSeries.getEditMenuBlocks()

        update_message = self.client.chat_update(
                                            channel=channel_id,
                                            username=self.name,
                                            # icon_emoji=self.emoji,
                                            text="Your series title has been updated",
                                            ts=currentSeries.menu_ts,
                                            blocks=blocks
                                            )
    def update_series_frequency(self, channel_id, series_frequency):
        """
        Update the series frequency.
        """
        # Update the series state frequency
        currentSeries.updateSeries("frequency", series_frequency)

        # Console log of updated series topic_selection
        # print("\n" + 70*"="  + "\nUpdating Series Frequency...\ncurrentSeries.state=\n", currentSeries.state, "\n" + 70*"=")

        # If the currentSeries is being updated NOT created from scratch.
        # The currentSeries object only has a series_id field if it is being
        # updated. NOT if it is being created for the first time. The series_id
        # field is only populated if the series is loaded from an SQL query.
        # This will determine which blocks to load.
        if not currentSeries.series_id:
            blocks = currentSeries.getCreationMenuBlocks()
        
        else:
            blocks = currentSeries.getEditMenuBlocks()

        update_message = self.client.chat_update(
                                            channel=channel_id,
                                            username=self.name,
                                            # icon_emoji=self.emoji,
                                            text="Your series title has been updated",
                                            ts=currentSeries.menu_ts,
                                            blocks=blocks
                                            )

    def update_series_numsessions(self, channel_id, series_numsessions):
        """
        Update the series number of sessions. series_numsessions parameter is an int.
        """
                # Update the series state frequency
        currentSeries.updateSeries("num_sessions", series_numsessions)

        # Console log of updated series num_sessions
        # print("\n" + 70*"="  + "\nUpdating Series Numsessions...\ncurrentSeries.state=\n", currentSeries.state, "\n" + 70*"=")

        # If the currentSeries is being updated NOT created from scratch.
        # The currentSeries object only has a series_id field if it is being
        # updated. NOT if it is being created for the first time. The series_id
        # field is only populated if the series is loaded from an SQL query.
        # This will determine which blocks to load.
        if not currentSeries.series_id:
            blocks = currentSeries.getCreationMenuBlocks()
        
        else:
            blocks = currentSeries.getEditMenuBlocks()

        update_message = self.client.chat_update(
                                            channel=channel_id,
                                            username=self.name,
                                            # icon_emoji=self.emoji,
                                            text="Your series title has been updated",
                                            ts=currentSeries.menu_ts,
                                            blocks=blocks
                                            )

    def update_series_menu_date(self, channel_id, series_date):
        """
        Update the series first session date.
        series_date is in the format "%Y-%m-%d"
        """
        currentSeries.updateSeries("start_date", series_date)
        # Console log of updated series start_dates
        # print("\n" + 70*"="  + "\nUpdating Series First sesh date...\ncurrentSeries.state=\n", currentSeries.state, "\n" + 70*"=")

        # If the currentSeries is being updated NOT created from scratch.
        # The currentSeries object only has a series_id field if it is being
        # updated. NOT if it is being created for the first time. The series_id
        # field is only populated if the series is loaded from an SQL query.
        # This will determine which blocks to load.
        if not currentSeries.series_id:
            blocks = currentSeries.getCreationMenuBlocks()
        
        else:
            blocks = currentSeries.getEditMenuBlocks()

        update_message = self.client.chat_update(
                                            channel=channel_id,
                                            username=self.name,
                                            # icon_emoji=self.emoji,
                                            text="Your series title has been updated",
                                            ts=currentSeries.menu_ts,
                                            blocks=blocks
                                            )

    def delete_message(self, channel_id, message_ts):
        """
        Delete the message with specified timestamp.
        This is used primarily for notifications that a user can dismiss.
        """
        return self.client.chat_delete(
                                            channel=channel_id,
                                            ts=message_ts,
                                            )

# ============================= SLASH COMMAND LOGIC =============================

    def view_series_message(self, channel_id, user_id, message_ts=0, isFromHelp=False):
        """
        TODO this has a lot of overlap with the edit_series_message, merge them?

        This method shows a menu for the user to view their series.
        Send the user a message showing the list of series they have. The user
        will select the series they want to view.

        Parameters
        ----------
        channel_id : str
            the Slack channel ID to send the message on
        user_id: int
            the Slack user_id of the user checking for their list of series
        message_ts: str
            (Optional) the timestamp of the original schedule message, this will be passed as state.
            If it is passed then the message will update the latest message, if it
            is not passed, it will post a new message.
        isFromHelp :  bool
            (Optional) Whether or not the user came from the help message. This will 
            decide whether or not to render a "back to help" button.
        
        """


        """
        Pseudocode:
        -Connect to SQL database.
        -Query for all series associated with the user id. (and team_id?)
        -Use the results of the query to create a list of options for the 
         select menu (using the title of the series for the text and the 
         series_id as the value)
        -Post the message with the blocks
        """

        # DATABASE OPERATIONS
        # First, connect to the sqlite3 database
        con = sqlite3.connect("serier.db")
        # Create a cursor
        cur = con.cursor()


        # SQL statement to select all series that the user is organizing
        sql_statement = '''SELECT series_id, title FROM series
        WHERE series_id IN (SELECT series_id FROM organizers
        WHERE user_id =\''''  + user_id + "')"


        # Store the result in a list of tuples of the format (series_id, title)
        res = cur.execute(sql_statement).fetchall()

        # Close the connection
        con.close()

        # check if result set res is empty. If it is empty, user has no series.
        if len(res) <= 0:
            blocks = [
                {
                    "type":"section",
                    "text":{
                    "type":"mrkdwn",
                    "text":"You have no series to view."
                    }
                },
                {
                    "type":"section",
                    "text":{
                    "type":"mrkdwn",
                    "text":"You can create one using the `/serier create` command."
                    }
                },
                {
                    "type":"actions",
                    "elements":[
                    {
                        "type":"button",
                        "action_id":"no_series_view_ok",
                        "text":{
                        "type":"plain_text",
                        "text":"OK",
                        "emoji":True
                        },
                        "value":"no_series_view_ok"
                    }
                    ]
                }
                ]

        # The user has series
        # Populate the select menu with the series associated with the user
        else:
            blocks = [
                {  
                    "type":"section",
                    "text":{
                        "type":"mrkdwn",
                        "text":"Select a series to view its schedule:"
                    }
                },
                {  
                    "type":"actions",
                    "elements":[  
                    {  
                        "type":"static_select",
                        "action_id":"select_series_view",
                        "placeholder":{
                            "type":"plain_text",
                            "text":"Select a series",
                            "emoji":True
                        },
                        "options":[
                            # Insert here. This format:
                        #     {
                        # 	"text": {
                        # 		"type": "plain_text",
                        # 		"text": "<series_title>",
                        # 		"emoji": True
                        # 	},
                        # 	"value": "series_id-<series_id>"
                        # }
                        ]
                    }
                    ]
                },
                {  
                    "type":"actions",
                    "elements":[  
                    {  
                        "type":"button",
                        "action_id":"cancel_view_series",
                        "text":{  
                        "type":"plain_text",
                        "text":"Cancel",
                        "emoji":True
                        },
                        "value":"cancel_view_series"
                    }
                    ]
                }
            ]


            for series in res:
                series_id, series_title = series[0], series[1]
                next_series = {
                            "text": {
                                "type": "plain_text",
                                "text": series_title,
                                "emoji": True
                            },
                            "value": "series_id-" + str(series_id)
                        }

                blocks[1]["elements"][0]["options"].append(next_series)
        
        # If the edit is being initiated, then post a new message.
        if message_ts == 0:
            post_message = self.client.chat_postMessage(
                                            channel=channel_id,
                                            username=self.name,
                                            # icon_emoji=self.emoji,
                                            text="Select a series to view its schedule",
                                            blocks=blocks
                                        )
        
        # If the user pressed back in the next step (a ts is provided), 
        # Or if the user entered this workflow from the button in the help message
        # then update the message
        else:
            # If the user is coming from the help message, insert a "back to help" button block
            if isFromHelp:
                back_to_help_button = {
                    "type": "button",
                    "action_id": "back_to_help",
                    "text": {
                        "type": "plain_text",
                        "text": "Back",
                        "emoji": True
                    },
                    "value": "from_view_series_message"
                }

                blocks[-1]["elements"].insert(0, back_to_help_button)

            update_message = self.client.chat_update(
                                channel=channel_id,
                                ts=message_ts,
                                username=self.name,
                                # icon_emoji=self.emoji,
                                text="Select a series to view its schedule",
                                blocks=blocks
                            )

    def update_view_series_message(self, channel_id, message_ts, message_blocks):
        """
        Updates the view series message to show a confirm button when the user
        selects a series to view. Use the parameter message_ts to chat.update
        the message.
        """
        confirm_view_button =  {  
                        "type":"button",
                        "action_id":"confirm_view_series",
                        "text":{  
                        "type":"plain_text",
                        "text":"View Schedule",
                        "emoji":True
                        },
                        "style":"primary",
                        "value":"confirm_view_series"
                    }

        # If the initial blocks don't already contain a confirm button.
        if message_blocks[-1]["elements"][0]["action_id"] != "confirm_view_series":
            message_blocks[-1]["elements"].insert(0, confirm_view_button)
        
        update_message = self.client.chat_update(
                                channel=channel_id,
                                username=self.name,
                                # icon_emoji=self.emoji,
                                text="Selected series to view its schedule",
                                ts=message_ts,
                                blocks=message_blocks
                                )

    def edit_series_message(self, channel_id, user_id, message_ts=0, isFromHelp=False):
        """
        TODO this has a lot of overlap with the view_series_message, merge them?

        Send the user a message showing the list of series they have. The user
        will select the series they want to edit.

        Parameters
        ----------
        channel_id : str
            the Slack channel ID to send the message on
        user_id: int
            the Slack user_id of the user checking for their list of series
        message_ts: str
            the timestamp of the original schedule message, this will be passed as state.
            Optional, if it is passed then the message will update the latest message, if it
            is not passed, it will post a new message.
        isFromHelp :  bool
            Whether or not the user came from the help message. Optional, this will 
            decide whether or not to render a "back to help" button.
        
        """

        """
        Pseudocode:
        -Connect to SQL database.
        -Query for all series associated with the user id. (and team_id?)
        -Use the results of the query to create a list of options for the 
         select menu (using the title of the series for the text and the 
         series_id as the value)
        -Post the message with the blocks
        """

        # DATABASE OPERATIONS
        # First, connect to the sqlite3 database
        con = sqlite3.connect("serier.db")
        # Create a cursor
        cur = con.cursor()


        # SQL statement to select all series that the user is organizing
        sql_statement = '''SELECT series_id, title FROM series
        WHERE series_id IN (SELECT series_id FROM organizers
        WHERE user_id =\''''  + user_id + "')"


        # Store the result in a list of tuples of the format (series_id, title)
        res = cur.execute(sql_statement).fetchall()

        # Close the connection
        con.close()

        # check if result set res is empty. If it is empty, user has no series.
        if len(res) <= 0:
            blocks = [
                {
                    "type":"section",
                    "text":{
                    "type":"mrkdwn",
                    "text":"You have no series to edit."
                    }
                },
                {
                    "type":"section",
                    "text":{
                    "type":"mrkdwn",
                    "text":"You can create one using the `/serier create` command."
                    }
                },
                {
                    "type":"actions",
                    "elements":[
                    {
                        "type":"button",
                        "action_id":"no_series_edit_ok",
                        "text":{
                        "type":"plain_text",
                        "text":"OK",
                        "emoji":True
                        },
                        "value":"no_series_edit_ok"
                    }
                    ]
                }
                ]

        # The user has series
        # Populate the select menu with the series associated with the user
        else:
            blocks = [
                {  
                    "type":"section",
                    "text":{
                        "type":"mrkdwn",
                        "text":"Select a series to edit:"
                    }
                },
                {  
                    "type":"actions",
                    "elements":[  
                    {  
                        "type":"static_select",
                        "action_id":"select_series_edit",
                        "placeholder":{
                            "type":"plain_text",
                            "text":"Select a series",
                            "emoji":True
                        },
                        "options":[
                            # Insert here. This format:
                        #     {
                        # 	"text": {
                        # 		"type": "plain_text",
                        # 		"text": "<series_title>",
                        # 		"emoji": True
                        # 	},
                        # 	"value": "series_id-<series_id>"
                        # }
                        ]
                    }
                    ]
                },
                {  
                    "type":"actions",
                    "elements":[  
                    {  
                        "type":"button",
                        "action_id":"cancel_edit_series",
                        "text":{  
                        "type":"plain_text",
                        "text":"Cancel",
                        "emoji":True
                        },
                        "value":"cancel_edit_series"
                    }
                    ]
                }
            ]


            for series in res:
                series_id, series_title = series[0], series[1]
                next_series = {
                            "text": {
                                "type": "plain_text",
                                "text": series_title,
                                "emoji": True
                            },
                            "value": "series_id-" + str(series_id)
                        }

                blocks[1]["elements"][0]["options"].append(next_series)


        # If the edit is being initiated, then post a new message.
        if message_ts == 0:
            post_message = self.client.chat_postMessage(
                                            channel=channel_id,
                                            username=self.name,
                                            # icon_emoji=self.emoji,
                                            text="Select a series to edit",
                                            blocks=blocks
                                        )
        
        # If the user pressed back in the next step (a ts is provided), 
        # then update the message.
        # (OR IF THE USER IS COMING FROM THE HELP MESSAGE)
        else:

            # If the user is coming from the help message, insert a "back to help" button block
            if isFromHelp:
                back_to_help_button = {
                    "type": "button",
                    "action_id": "back_to_help",
                    "text": {
                        "type": "plain_text",
                        "text": "Back",
                        "emoji": True
                    },
                    "value": "from_edit_series_message"
                }

                blocks[-1]["elements"].insert(0, back_to_help_button)

            update_message = self.client.chat_update(
                                channel=channel_id,
                                ts=message_ts,
                                username=self.name,
                                # icon_emoji=self.emoji,
                                text="Select a series to edit",
                                blocks=blocks
                            )

    def update_edit_series_message(self, channel_id, message_ts, message_blocks):
        """
        Updates the edit series message to show a confirm button when the user
        selects a series to edit. Use the parameter message_ts to chat.update
        the message.
        """
        # TODO add this block
        confirm_edit_button =  {  
                        "type":"button",
                        "action_id":"confirm_edit_series",
                        "text":{  
                        "type":"plain_text",
                        "text":"Edit",
                        "emoji":True
                        },
                        "style":"primary",
                        "value":"confirm_edit_series"
                    }

        # If the initial blocks don't already contain a confirm button.
        # Add one.
        if message_blocks[-1]["elements"][0]["action_id"] != "confirm_edit_series":
            message_blocks[-1]["elements"].insert(0, confirm_edit_button)
        
        update_message = self.client.chat_update(
                                channel=channel_id,
                                username=self.name,
                                # icon_emoji=self.emoji,
                                text="Selected series to edit",
                                ts=message_ts,
                                blocks=message_blocks
                                )

    def edit_series_menu(self, channel_id, user_id, message_ts):
        """
        Display the series configuration menu that the user will use to edit
        the series.


        Parameters
        ----------
        channel_id : str
            id of the Slack channel associated with incoming event
        
        user_id : str
            id of the user_id updatingseries

        ts : str
            timestamp of the series edit message.
        
        """

        # Get the user's info to extract the timezone
        user_info = self.client.users_info(
                                            user=user_id
                                            )
        # Console log for user info
        # print("\n" + 70*"="  + "\nuser_info=\n", user_info, "\n" + 70*"=")

        # The PyTZ timezone string
        user_tz = user_info["user"]["tz"]
        # Console log for series state
        # print("\n" + 70*"="  + "\ncurrentSeries.state=\n", currentSeries.state, "\n" + 70*"=")
        
        # Set the display timezone to be the user's local timezone
        currentSeries.timezone = user_tz

        # Convert the timezone string to a pytz timezone object
        user_tz = pytz.timezone(user_tz)

        # Adjust the dates and times on the currentSeries object
        # to be in the user's local timezone.

        # get dt object for start date.
        series_start_date = datetime.strptime(currentSeries.state["start_date"], "%Y-%m-%d")
        # Get dt object for session_start
        series_session_start = datetime.strptime(currentSeries.state["time"], '%H:%M')
        # combine two into one dt object
        start_date_dt = series_start_date.replace(hour=series_session_start.hour, minute=series_session_start.minute)
        # Localize to utc time
        utc_series_dt = pytz.utc.localize(start_date_dt)
        # translate to user local timezone
        user_local_dt = utc_series_dt.astimezone(user_tz)
        # update start date to be the date part of the resulting dt object (string)
        currentSeries.state["start_date"] = user_local_dt.strftime("%Y-%m-%d")
        # update session_start to be the time part of the resulting object (string)
        currentSeries.state["time"] = user_local_dt.strftime('%H:%M')
        # Repeat for end_date
        series_end_date = datetime.strptime(currentSeries.state["end_date"], "%Y-%m-%d")
        end_date_dt = series_end_date.replace(hour=series_session_start.hour, minute=series_session_start.minute)
        utc_series_dt = pytz.utc.localize(end_date_dt)
        user_local_dt = utc_series_dt.astimezone(user_tz)
        currentSeries.state["end_date"] = user_local_dt.strftime("%Y-%m-%d")



        # Update the last message to show the menu blocks
        update_message = self.client.chat_update(
                                        channel=channel_id,
                                        username=self.name,
                                        # icon_emoji=self.emoji,
                                        text="Edit a series",
                                        ts=message_ts,
                                        blocks=currentSeries.getEditMenuBlocks()
                                        )
        # Update the currentSeries menu timestamp so that the menu can be updated
        currentSeries.menu_ts = update_message["ts"]


    def confirm_series_edit(self, channel_id, organizer_id, message_ts):
        """
        Confirm the edit of the series. Execute and SQL query to edit the series
        and the sessions in the relevant tables.
        """
        # FIRST, check if the datetime the user set is in the past.

        # Get the timezone of the creating user at the time of series creation
        user_tz = pytz.timezone(currentSeries.timezone)

        # Create a datetime object from the series data
        series_time = datetime.strptime(currentSeries.state["time"], '%H:%M')
        start_date_date = datetime.strptime(currentSeries.state["start_date"], "%Y-%m-%d")
        start_date_dt = start_date_date.replace(hour=series_time.hour, minute=series_time.minute)

        # Use the timezone and the series data to convert the time to UTC
        user_local_dt = user_tz.localize(start_date_dt)
        utc_dt = user_local_dt.astimezone(pytz.utc)

        
        # TODO WHY ARE WE COMPARING IT TO NOW? THIS IS AN ALREADY EXISTING SERIES, IT COULD
        # VERY WELL BE LEGALLY STARTING IN THE PAST.
        # Compare the scheduled time to the time now
        utc_now = datetime.now(pytz.utc)

        if utc_dt < utc_now:
            # If the series is scheduled for the past
            # Send a warning message
            post_message = self.client.chat_postMessage(
                                            channel=channel_id,
                                            username=self.name,
                                            # icon_emoji=self.emoji,
                                            text="Series schedule for the past",
                                            blocks=[  
                                            {  
                                                "type":"section",
                                                "text":{  
                                                "type":"mrkdwn",
                                                "text":":warning:Your series is scheduled to start in the past. Please pick a time in the future."
                                                }
                                            },
                                            {  
                                                "type":"actions",
                                                "elements":[  
                                                {  
                                                    "type":"button",
                                                    "action_id":"past_schedule_ok",
                                                    "text":{  
                                                    "type":"plain_text",
                                                    "text":"OK",
                                                    "emoji":True
                                                    },
                                                    "value":"past_schedule_ok"
                                                }
                                                ]
                                            }
                                            ]
                                        )

        # If there is no problem with the series state
        # Give the go ahead
        else:
            
            # Update time and first session to be UTC

            currentSeries.state["time"] = utc_dt.time().strftime("%H:%M")
            currentSeries.state["start_date"] = utc_dt.date().strftime("%Y-%m-%d")



            # Update end_date to be UTC
            end_date_date = datetime.strptime(currentSeries.state["end_date"], "%Y-%m-%d")
            user_local_dt = user_tz.localize(end_date_date)
            end_date_utc = user_local_dt.astimezone(pytz.utc)
            currentSeries.state["end_date"] = end_date_utc.strftime("%Y-%m-%d")

            # TODO Put these in subroutines (make it resuable)
            # DATABASE OPERATIONS
            # First, connect to the sqlite3 database
            con = sqlite3.connect("serier.db")
            # Create a cursor
            cur = con.cursor()

            # First, update the series in the series table.
            # Prepare the statement and the values
            series_record = (currentSeries.state["title"], currentSeries.state["presenter"], currentSeries.state["topic_selection"],
                            currentSeries.state["start_date"], currentSeries.state["end_date"], currentSeries.state["time"],
                            currentSeries.state["frequency"], currentSeries.state["num_sessions"],
                            currentSeries.series_id) # The last element is the series_id which will go in the WHERE clause

            sql_statement = ''' UPDATE series
                                SET title = ?, presenter = ?, topic_selection = ?, start_date = ?,
                                    end_date = ?, session_start = ?, frequency = ?, num_sessions = ?
                                WHERE series_id = ?'''

            # Execute the insertion
            cur.execute(sql_statement, series_record)


            # commit and close the database connection
            con.commit()
            con.close()


            
            # Send a confirmation message to the user that their series has been edited
            update_message = self.client.chat_update(
                                            channel=channel_id,
                                            username=self.name,
                                            # icon_emoji=self.emoji,
                                            ts=currentSeries.menu_ts,
                                            text="Your Series *" + currentSeries.state["title"] + "* has been edited",
                                            blocks=[
                                                {
                                                    "type": "section",
                                                    "text": {
                                                        "type": "mrkdwn",
                                                        "text": "Your series *" + currentSeries.state["title"] + "* has been successfully edited!\n"
                                                    }
                                                },
                                                {
                                                    "type": "actions",
                                                    "elements": [
                                                        {
                                                            "type": "button",
                                                            "action_id": "series_creation_ok",
                                                            "text": {
                                                                "type": "plain_text",
                                                                "text": "OK",
                                                                "emoji": True
                                                            },
                                                            "value": "series_creation_ok"
                                                        }
                                                    ]
                                                }
                                            ]
                                        )

            
            # Now, update the sessions of the series.
            # This is done by first deleting all the sessions in the series, and then creating them again.
            # It stores these sessions on the Series object.
            # TODO Unnecessary to store it on Series object right?
            currentSeries.deleteSessions(currentSeries.series_id)
            currentSeries.createSessions(currentSeries.series_id)
            

    def delete_series(self, channel_id, user_id, message_ts):
        """
        Deletes the currentSeries that is in memory from the db and clears it from memory
        """

        # TODO Put these in subroutines (make it resuable)
        # DATABASE OPERATIONS
        # First, connect to the sqlite3 database
        con = sqlite3.connect("serier.db")
        # Create a cursor
        cur = con.cursor()

        # First, delete the series in the series table.
        # Prepare the statement and the values
        # The series_id of the series we want to delete
        series_record = (currentSeries.series_id,)

        sql_statement = ''' DELETE FROM series
                            WHERE series_id = ?'''

        # Execute the deletion
        cur.execute(sql_statement, series_record)

        # Second, delete the sessions associated with that series from sessions table.
        # Prepare the statement and the values
        sql_statement = ''' DELETE FROM sessions
                            WHERE series_id = ?'''
        # Execute the deletion
        cur.execute(sql_statement, series_record)

        # Third, remove series from organizer associated with that series from organizers table.
        # Prepare the statement and the values
        sql_statement = ''' DELETE FROM organizers
                            WHERE series_id = ?'''
        # Execute the deletion
        cur.execute(sql_statement, series_record)


        # commit and close the database connection
        con.commit()
        con.close()


        # Notify the user about successful series deletion
        update_message = self.client.chat_update(
                                    channel=channel_id,
                                    username=self.name,
                                    # icon_emoji=self.emoji,
                                    text="Your series has been successfully deleted",
                                    ts=message_ts,
                                    blocks=[
                                        {
                                            "type": "section",
                                            "text": {
                                                "type": "mrkdwn",
                                                "text": "Your series *" + currentSeries.state["title"] + "* was successfully deleted."
                                            }
                                        },
                                        {
                                            "type": "actions",
                                            "elements": [
                                                {
                                                    "type": "button",
                                                    "action_id": "delete_series_ok",
                                                    "text": {
                                                        "type": "plain_text",
                                                        "text": "OK",
                                                        "emoji": True
                                                    },
                                                    "value": "delete_series_ok"
                                                }
                                            ]
                                        }
                                    ]
                                )
        
        # Finally, clear currentSeries from memory
        self.reset_currentSeries()


    def change_session_presenter_dialog(self, trigger_id, session_index, message_ts):
        """
        Open a dialog to change the presenter for a session.

        Parameters
        ----------
        trigger_id : str
            trigger_id of the edit series action to open a dialog
        session_index: int
            the session number of the session associated with the change.
        message_ts: str
            the timestamp of the original schedule message, this will be passed as state.
        """
        # Cast the session_index string to int
        dialog_data = {
                "callback_id": "update_session_presenter",
                "title": "Change Session Presenter",
                # Update state in the following format: schedule_ts,sesion_index, 
                "state": message_ts + "," + str(session_index),
                "elements": [
                    {
                    "label": "Presenter",
                    "name": "session_presenter",
                    "type": "select",
                    "data_source": "users",
                    # Set the defaulted option to the session's presenter
                    "value": currentSeries.sessions[session_index]["presenter"]
                    }
                ]
            }

        open_dialog =  self.client.dialog_open(
                                            dialog=dialog_data,
                                            trigger_id=trigger_id
                                            )

    def change_session_topic_dialog(self, trigger_id, session_index, message_ts):
        """
        Open a dialog to change the topic for a session.

        Parameters
        ----------
        trigger_id : str
            trigger_id of the edit series action to open a dialog
        session_index: str
            the session number of the session associated with the change.
        message_ts: str
            the timestamp of the original schedule message, this will be passed as state.
       
        """
        session_index = int(session_index)

        # If a topic has not been selected yet, default to blank field.
        if currentSeries.sessions[session_index]["topic"] == "Not Selected":
            dialog_data = {
                    "callback_id": "update_session_topic",
                    "title": "Edit Topic",
                    # Update state in the following format: schedule_ts,sesion_index, 
                    "state": message_ts + "," + str(session_index),
                    "elements": [
                        {
                            "type": "text",
                            "label": "Topic",
                            "name": "session_topic"
                        }
                    ]
                }
        else: # If a topic has been selected, make it the default.
            dialog_data = {
                    "callback_id": "update_session_topic",
                    "title": "Edit Topic",
                    # Update state in the following format: schedule_ts,sesion_index, 
                    "state": message_ts + "," + str(session_index),
                    "elements": [
                        {
                            "type": "text",
                            "label": "Topic",
                            "name": "session_topic",
                            # Set the default value to be the current topic
                            "value": currentSeries.sessions[session_index]["topic"]
                        }
                    ]
                }

        open_dialog =  self.client.dialog_open(
                                            dialog=dialog_data,
                                            trigger_id=trigger_id
                                            )

    def update_session_presenter(self, session_index, session_presenter, channel_id, message_ts):
        """
        Updates the presenter for the session with specified session index.
        Renders message with new schedule blocks, reflecting the change in presenter.

        """
        # Update the session presenter in memory
        currentSeries.sessions[session_index]["presenter"] = session_presenter

        # Render the schedule
        self.printSchedule(channel_id, message_ts)
        

        # Then, update the session data in the database.
        session_id =  currentSeries.sessions[session_index]["session_id"]

        # DATABASE OPERATIONS
        # First, connect to the sqlite3 database
        con = sqlite3.connect("serier.db")
        # Create a cursor
        cur = con.cursor()


        session_record = (session_presenter, session_id)

        # Update the session with specified session_id
        sql_statement = '''UPDATE sessions
        SET presenter = ?
        WHERE session_id = ?'''


        cur.execute(sql_statement, session_record)

        # Close the connection
        con.commit()
        con.close()


    def update_session_topic(self, session_index, session_topic, channel_id, message_ts):
        """
        Updates the topic for the session with specified session index.
        Renders message with new schedule blocks, reflecting the change in topic.

        """
        # Update the session topic in memory
        currentSeries.sessions[session_index]["topic"] = session_topic

        # Render the schedule
        self.printSchedule(channel_id, message_ts)
        

        # Then, update the session data in the database.
        session_id =  currentSeries.sessions[session_index]["session_id"]

        # DATABASE OPERATIONS
        # First, connect to the sqlite3 database
        con = sqlite3.connect("serier.db")
        # Create a cursor
        cur = con.cursor()


        session_record = (session_topic, session_id)

        # Update the session with specified session_id
        sql_statement = '''UPDATE sessions
        SET topic = ?
        WHERE session_id = ?'''


        cur.execute(sql_statement, session_record)

        # Close the connection
        con.commit()
        con.close()

        
    def reset_currentSeries(self):
        """
        resets the currentSeries object in memory.
        """
        currentSeries.resetSeries()
        currentSeries.sessions = []

    def setSeries(self, series_id):
        """
        sets currentSeries (the series in memory) to be the series with a specified
        series_id.
        """
        # DATABASE OPERATIONS
        # First, connect to the sqlite3 database
        con = sqlite3.connect("serier.db")
        # Create a cursor
        cur = con.cursor()


        # SQL statement to select the series with specified series_id
        sql_statement = '''SELECT * FROM series
        WHERE series_id = ''' + series_id


        # Store the result as a tuple in the following format:
        # (series_id, title, presenter, topic_selection, start_date, end_date,
        # session_start, frequency, num_sessions, is_paused)
        series = cur.execute(sql_statement).fetchone()

        # TODO query for all sessions with that series_id too

        # Query for all sessions with the specified series_id
        sql_statement = '''SELECT * FROM sessions
        WHERE series_id = ''' + series_id


        # Store the result as a list of tuples with following format:
        # [(session_id, series_id, session_start, presenter, topic, is_skipped,
        #  is_done, is_modified)]
        sessions = cur.execute(sql_statement).fetchall()

        # Close the connection
        con.close()

        # Load current series from the query result
        currentSeries.loadFromTuple(series, sessions)

    def show_app_commands(self, channel_id, message_ts=0):
        """
        Show the user a list of the app's slash commands
        NOTE: the timestamp parameter is defaulted to zero. If one is passed, then
        this will be the result of the "commands" button being pressed from the help message.
        Otherwise, the edit is being initiated from the slash command.
        """
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Here's the list of commands for what Serier can do*:\n*Command*\t\t\t\t\t\t\t\t\t\t*Description*\n_/serier create_\t\t\t\t\t\t\t\t\t Start a series\n_/serier schedule_\t\t\t\t\t\t\t\t View a series schedule\n_/serier edit_\t\t\t\t\t\t\t\t\t\t Edit a series\n_/serier help_\t\t\t\t\t\t\t\t\t\tGet help\n_/serier commands_\t\t\t\t\t\t\t  View this commands list"
                }
            },
            {
                "type": "divider"
            }
        ]
        
        # If the commands list was requested from the help message button (ts != 0)
        if message_ts:
            blocks.append(
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "action_id": "back_to_help",
                            "text": {
                                "type": "plain_text",
                                "text": "Back",
                                "emoji": True
                            },
                            "value": "click_me_123"
                        },
                        {
                            "type": "button",
                            "action_id": "close_help_message",
                            "text": {
                                "type": "plain_text",
                                "text": "Close Help",
                                "emoji": True
                            },
                            "value": "from_help_message"
                        }
                    ]
                }
            )

            # Update the message
            update_message = self.client.chat_update(
                channel=channel_id,
                ts=message_ts,
                username=self.name,
                # icon_emoji=self.emoji,
                text="Select a series to edit",
                blocks=blocks
            )

        # If the commands list was requested from the slash command (ts == 0)
        else:
            blocks.append(
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "action_id": "commands_list_ok",
                            "text": {
                                "type": "plain_text",
                                "text": "OK",
                                "emoji": True
                            },
                            "value": "from_slash_command"
                        }
                    ]
                }
            )

            # Post the message
            post_message = self.client.chat_postMessage(
                channel=channel_id,
                username=self.name,
                # icon_emoji=self.emoji,
                text="Select a series to edit",
                blocks=blocks
            )


# ============================= AUTHORIZATION =============================
    def auth(self, code):
        """
        Authenticate with OAuth and assign correct scopes.
        Save a dictionary of authed team information in memory on the bot
        object.

        :param code: str
            temporary authorization code sent by Slack to be exchanged for an
            OAuth token.
        """
        # After the user has authorized this app for use in their Slack team,
        # Slack returns a temporary authorization code that we'll exchange for
        # an OAuth token using the oauth.access endpoint
        auth_response = self.client.oauth_access(
                            client_id=self.oauth["client_id"],
                            client_secret=self.oauth["client_secret"],
                            code=code
                            )

        # Console log of oauth.access
        # print("\n" + 70*"="  + "\nauth_response=\n", auth_response, "\n" + 70*"=")


        # To keep track of authorized teams and their associated OAuth tokens,
        # we will save the team ID and bot tokens to the global authed_teams object

        # TODO The following deserialization of the bot token works, but is it most efficient?
        # It reads in the whole list, and then rewrites it.

        # Open the file, read it in, update it (if already exists) or add it (new team).
        # Write the file back in
        with open('authed_teams.txt', 'r+') as authed_teams_file: 
            try: 
                authed_teams = json.load(authed_teams_file)

                # Console log for reinstallation process
                # print("\n" + 70*"="  + "\nauthed_teams =\n", authed_teams, "\n" + 70*"=")
                # print("\n" + 70*"="  + "\nauthed_teams already exists, updating... =\n", "\n" + 70*"=")
            
            # ValueError is raised when the authed_teams file is empty. This should only trigger for first installer
            except ValueError: 
                authed_teams = {}
                # Console log for installation process
                # print ("\n" + 70*"="  + "\nauthed_teams does not already exist, creating new... =\n" + 70*"=")

            team_id = auth_response["team_id"]
            authed_teams[team_id] = {"bot_token":
                auth_response["bot"]["bot_access_token"]}
            
            # rewrite the file with newly added bot token
            authed_teams_file.seek(0)
            json.dump(authed_teams, authed_teams_file)


        # Then we'll reconnect to the Slack Client with the correct team's bot token.
        # Then, send the installing user the onboarding help message
        self.client_connect(team_id)
        user_id = auth_response["user_id"]
        self.send_help_message(self.open_dm(user_id))
