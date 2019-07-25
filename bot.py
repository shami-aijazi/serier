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
        self.emoji = ":space_invader:"

        # NOTE: Python-slack requires a client connection to generate
        # an oauth token. We can connect to the client without authenticating
        # by passing an empty string as a token and then reinstantiating the
        # client with a valid OAuth token once we have one.
        self.client = WebClient("")

    def client_connect(self, team_id):
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
                                            icon_emoji=self.emoji,
                                            text=message_obj.text,
                                            blocks=message_obj.blocks
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

        # create a Greeting message Message object

        message_obj = message.DMResponse()

        # Then we'll set the message object's channel attribute to the IM
        # channel of the user we'll communicate with. We'll find this using
        # the open_dm function, which uses the im.open API call.
        message_obj.channel = channel_id

        post_message = self.client.chat_postMessage(
                                            channel=message_obj.channel,
                                            username=self.name,
                                            icon_emoji=self.emoji,
                                            text=message_obj.text,
                                            blocks=message_obj.blocks
                                            )
                                            
    def help_message(self, channel_id):
        """
        Create and send a response message to a user who DM's the bot.
        :param team_id: str
            id of the Slack team associated with the incoming event
        :param user_id: str
            id of the Slack user associated with the incoming event

        """

        # create a Help message Message object

        message_obj = message.Help()

        # Then we'll set the message object's channel
        message_obj.channel = channel_id

        post_message = self.client.chat_postMessage(
                                            channel=message_obj.channel,
                                            username=self.name,
                                            icon_emoji=self.emoji,
                                            text=message_obj.text,
                                            blocks=message_obj.blocks
                                            )










                                        
# ============================= SERIES BOT LOGIC =============================
    def new_series_menu(self, channel_id, ts, user_id):
        """
        Create new series. Update message with parameter ts to show the new series
        creation menu. Use the user_id to get the timezone of the user and update the
        series state's datetime accordingly.
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
        series_time = now_user_tz.strftime('%I:%M %p')

        # Populate the series object with default values
        # Save the timestamp of the menu message on the series object
        currentSeries.newSeries(ts, series_start_date, series_time, user_tz)



        update_message = self.client.chat_update(
                                            channel=channel_id,
                                            username=self.name,
                                            icon_emoji=self.emoji,
                                            text="Create new series",
                                            ts=currentSeries.menu_ts,
                                            blocks=currentSeries.getMenuBlocks()
                                            )

    def confirm_new_series(self, channel_id, organizer_id, message_ts):
        """
        Confirm the creation of the new series. Check if the time and date set is not in the
        past. Commit the series to db and send an acknowledgement message.

        """
        # Get the timezone of the creating user at the time of series creation
        user_tz = pytz.timezone(currentSeries.timezone)

        # Create a datetime object from the series data
        series_time = datetime.strptime(currentSeries.state["time"], '%I:%M %p')
        first_session_date = datetime.strptime(currentSeries.state["first_session"], "%Y-%m-%d")
        first_session_dt = first_session_date.replace(hour=series_time.hour, minute=series_time.minute)
        
        # Use the timezone and the series data to convert the time to UTC
        user_local_dt = user_tz.localize(first_session_dt)
        utc_dt = user_local_dt.astimezone(pytz.utc)


        # Compare the scheduled time to the time now
        utc_now = datetime.now(pytz.utc)
        # console log for datetimes
        # print("\n" + 70*"="  + "\nSchedulued Datetime=\n", utc_dt, "\nNow Datetime=\n", utc_now, "\n" + 70*"=")
        

        if utc_dt < utc_now:
            # If the series is scheduled for the past
            # Send a warning message
            post_message = self.client.chat_postMessage(
                                            channel=channel_id,
                                            username=self.name,
                                            icon_emoji=self.emoji,
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

            # TODO commit the series to db
            
            # TODO edit the series state to be what we want to serialize
            # Update time and first session to be UTC
            currentSeries.state["time"] = utc_dt.time().strftime("%I:%M %p")
            currentSeries.state["first_session"] = utc_dt.date().strftime("%Y-%m-%d")

            # Update last_session to be UTC
            last_session_date = datetime.strptime(currentSeries.state["last_session"], "%m/%d/%Y")
            user_local_dt = user_tz.localize(last_session_date)
            last_session_utc = user_local_dt.astimezone(pytz.utc)
            currentSeries.state["last_session"] = last_session_utc.strftime("%Y-%m-%d")


            # series_dict = {organizer_id: [currentSeries.state]}
        


            # TODO Serialize this to a file locally
            # Open the file, read it in, update it (organizer already has a series)
            # or add it (new organizer).
            # Write the file back in
            with open('series.txt', 'r+') as series_file: 
                try: 
                    series_dict = json.load(series_file)

                
                # ValueError is raised when the series file is empty. This should only trigger for first series
                except ValueError: 
                    # Each organizer user has a list of series associated with them
                    # Each series is a dictionary representing its state
                    series_dict = {organizer_id: []}
                   
                
                series_dict[organizer_id].append({"series_state":currentSeries.state})
                
                # rewrite the file with newly added series
                series_file.seek(0)
                json.dump(series_dict, series_file)

            
            # Send a confirmation message to the user that their series has been created
            update_message = self.client.chat_update(
                                            channel=channel_id,
                                            username=self.name,
                                            icon_emoji=self.emoji,
                                            ts=currentSeries.menu_ts,
                                            text="Your Series *" + currentSeries.state["title"] + "* has been created",
                                            blocks=[
                                                {
                                                    "type": "section",
                                                    "text": {
                                                        "type": "mrkdwn",
                                                        "text": "Your series *" + currentSeries.state["title"] + "* has been succesfully created!\n"
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
            # Console log for populating sessions
            # print("\n" + 70*"="  + "\nAbout to set the sessions...\ncurrentSeries.state=\n", currentSeries.state, "\n" + 70*"=")
            # Now that the series has the go ahead, create the sessions
            currentSeries.setSessions()

            

            # TODO untidy hacking fix here. Clean this up later. (lol as if this is the only section of code like that)
            # Extract the title from state before resetting the series. This is needed
            # to display the schedule. This is to fix the situation where the schedule
            # message crashes because of exceeding the 50-block message limit. In that
            # situation the series wouldn't reset and it would cause problems when
            # making creating a series again.
            series_title = currentSeries.state["title"]

            # At the end of the creation and serialization, reset the series in memory
            # NOTE: this does NOT reset the sessions object on memory. This object is needed to send
            # the schedule. This object will be reset LATER.
            currentSeries.resetSeries()

            # Then, post the schedule message
            post_message = self.client.chat_postMessage(
                                            channel=channel_id,
                                            username=self.name,
                                            icon_emoji=self.emoji,
                                            text="Here's the schedule for your series *" + series_title + "*",
                                            blocks=currentSeries.getScheduleBlocks(series_title)
                                        )

            # Reset the sessions in the end
            currentSeries.sessions = []


    def cancel_new_series(self, channel_id):
        """
        Cancel a new series. Update message with parameter ts to show the series
        canellation confirmation. Revert series state to default
        """

        update_message = self.client.chat_update(
                                            channel=channel_id,
                                            username=self.name,
                                            icon_emoji=self.emoji,
                                            text="Your series has been successfully cancelled",
                                            ts=currentSeries.menu_ts,
                                            blocks=[{"type": "section",
                                                    "text": {
                                                    "type": "mrkdwn",
                                                    "text": "Your series has been succesfully cancelled."
                                                        }
                                                    }
                                                ]
                                            )

        # Reset the series state
        currentSeries.resetSeries()
        
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

        update_message = self.client.chat_update(
                                            channel=channel_id,
                                            username=self.name,
                                            icon_emoji=self.emoji,
                                            text="Your series title has been updated",
                                            ts=currentSeries.menu_ts,
                                            blocks=currentSeries.getMenuBlocks()
                                            )

    def update_series_presenter(self, channel_id, user_id):
        """
        Update the series presenter. Make user_id parameter the presenter for the series
        """
        # Update the series presenter
        currentSeries.updateSeries("presenter", user_id)

        # Console log of updated series presenter
        # print("\n" + 70*"="  + "\nUpdating Series Presenter...\ncurrentSeries.state=\n", currentSeries.state, "\n" + 70*"=")

        update_message = self.client.chat_update(
                                            channel=channel_id,
                                            username=self.name,
                                            icon_emoji=self.emoji,
                                            text="Your series presenter has been updated",
                                            ts=currentSeries.menu_ts,
                                            blocks=currentSeries.getMenuBlocks()
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

        update_message = self.client.chat_update(
                                            channel=channel_id,
                                            username=self.name,
                                            icon_emoji=self.emoji,
                                            text="Your series topic selection has been updated",
                                            ts=currentSeries.menu_ts,
                                            blocks=currentSeries.getMenuBlocks()
                                            )

    def update_series_time(self, channel_id, series_time):
        """
        Update the series time. series_time str format: '%I:%M %p'
        """
        # Update the series state time
        currentSeries.updateSeries("time", series_time)

        # Console log of updated series time
        # print("\n" + 70*"="  + "\nUpdating Series Time...\ncurrentSeries.state=\n", currentSeries.state, "\n" + 70*"=")

        update_message = self.client.chat_update(
                                            channel=channel_id,
                                            username=self.name,
                                            icon_emoji=self.emoji,
                                            text="Your series time has been updated",
                                            ts=currentSeries.menu_ts,
                                            blocks=currentSeries.getMenuBlocks()
                                            )
        
    def update_series_frequency(self, channel_id, series_frequency):
        """
        Update the series frequency.
        """
        # Update the series state frequency
        currentSeries.updateSeries("frequency", series_frequency)

        # Console log of updated series topic_selection
        # print("\n" + 70*"="  + "\nUpdating Series Frequency...\ncurrentSeries.state=\n", currentSeries.state, "\n" + 70*"=")

        update_message = self.client.chat_update(
                                            channel=channel_id,
                                            username=self.name,
                                            icon_emoji=self.emoji,
                                            text="Your series frequency has been updated",
                                            ts=currentSeries.menu_ts,
                                            blocks=currentSeries.getMenuBlocks()
                                            )

    def update_series_numsessions(self, channel_id, series_numsessions):
        """
        Update the series number of sessions. series_numsessions parameter is an int.
        """
                # Update the series state frequency
        currentSeries.updateSeries("num_sessions", series_numsessions)

        # Console log of updated series num_sessions
        # print("\n" + 70*"="  + "\nUpdating Series Numsessions...\ncurrentSeries.state=\n", currentSeries.state, "\n" + 70*"=")

        # For now, decided not to show this to frontend
        update_message = self.client.chat_update(
                                            channel=channel_id,
                                            username=self.name,
                                            icon_emoji=self.emoji,
                                            text="Your series numsessions has been updated",
                                            ts=currentSeries.menu_ts,
                                            blocks=currentSeries.getMenuBlocks()
                                            )

    def update_series_menu_date(self, channel_id, series_date):
        """
        Update the series first session date.
        series_date is in the format "%Y-%m-%d"
        """
        currentSeries.updateSeries("first_session", series_date)
        # Console log of updated series first_sessions
        # print("\n" + 70*"="  + "\nUpdating Series First sesh date...\ncurrentSeries.state=\n", currentSeries.state, "\n" + 70*"=")

        # Update the menu message to reflect the change
        update_message = self.client.chat_update(
                                            channel=channel_id,
                                            username=self.name,
                                            icon_emoji=self.emoji,
                                            text="Your series first session date has been updated",
                                            ts=currentSeries.menu_ts,
                                            blocks=currentSeries.getMenuBlocks()
                                            )

    def acknowledge_notification(self, channel_id, message_ts):
        """
        Delete the message with specified timestamp.
        This is used primarily for notifications that a user can dismiss.
        """
        delete_message = self.client.chat_delete(
                                            channel=channel_id,
                                            ts=message_ts,
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
        # Then, send the installing user the onboarding (greeting) message.
        self.client_connect(team_id)
        user_id = auth_response["user_id"]
        self.onboarding_message(user_id)
