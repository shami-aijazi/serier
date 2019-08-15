"""
A routing layer for the series organizer bot.

"""

import json
import bot
from flask import Flask, request, make_response, render_template
from slackeventsapi import SlackEventAdapter

from time import time
import hmac
import hashlib

pyBot = bot.Bot()

app = Flask(__name__)

# Connect to Slack's Events API adapter to receive actions via the Events API
# bind it to the existing Flask server (called "app") with the "/events" endpoint.
slack_signing_secret = pyBot.signing_secret
slack_events_adapter = SlackEventAdapter(slack_signing_secret, "/events", app)

@slack_events_adapter.on("message")
def handle_message(slack_event):
    """
    "message" Event listener. Parse message events and route them to bot for action.
    """
    # console log for the event
    # print("\n" + 70*"="  + "\nslack_event=\n", json.dumps(slack_event), "\n" + 70*"=")

    # parse team_id and connect to client
    team_id = slack_event["team_id"]
    pyBot.client_connect(team_id)


    # Check if it is a direct message
    if slack_event["event"]['channel_type'] == 'im':

        # Check if the message is a user message (don't count the bot's own messages.)
        if "client_msg_id" in slack_event["event"]:
             # Parse channel_id and incoming message text
            message_text = slack_event["event"]["text"]
            channel_id = slack_event["event"]["channel"]

            # === User sent a greeting ===
            if (message_text.lower() == "hi" or
                    message_text.lower() == "hello" or
                    message_text.lower() == "hey" or
                    message_text.lower() == "greetings" or
                    message_text.lower() == "serier"):

                    user_id = slack_event["event"]["user"]
                    pyBot.greeting_message(user_id, channel_id)
                    return make_response("Greeting DM Sent", 200,)
                

            # === User asked for help ===
            elif message_text[:4].lower()=="help":
                pyBot.send_help_message(channel_id)
                return make_response("Help DM Sent", 200,)


            # === Bot didn't understand ===
            # Reply with the default response message
            pyBot.dm_response_message(channel_id)
            return make_response("Default Response DM Sent", 200,)

def verify_signature(timestamp, signature, request_body):

    """
    Verify the request signature of a request sent from slack.

    Parameters
    ----------
    timestamp : str
        timestamp of incoming slack request
    signature : str
        signing signature of incoming slack request
    request_body: str
        The raw request body from incoming slack request

    Returns
    ----------
    isValid : bool
        true if it matches the signing secret
        false otherwise.
    """
    if abs(time() - int(timestamp)) > 60 * 5:
    # The request timestamp is more than five minutes from local time.
    # It could be a replay attack.
        return False
    
    sig_basestring = str.encode('v0:' + str(timestamp) + ':') + request_body

    request_hash = 'v0=' + hmac.new(
                str.encode(pyBot.signing_secret),
                sig_basestring, hashlib.sha256
            ).hexdigest()
    
    # Compare the generated hash and incoming request signature
    return hmac.compare_digest(request_hash, signature)

def _action_handler (payload, action_type, action_id):
    """
    A helper function that routes user interactive actions to our Bot
    by action type and and action id.
    """

    # console log for the payload
    # print("\n" + 70*"="  + "\ninteractive event payload=\n", json.dumps(payload), "\n" + 70*"=")

    # Extract the original message channel_id
    # in order to update the message as the state of the series changes.

    if action_type == "dialog_submission":
        channel_id = payload["channel"]["id"]
    else:
        channel_id = payload["container"]["channel_id"]
        user_id = payload["user"]["id"]


    # ==================== BUTTON ACTIONS ====================
    if action_type == "button":
        # If the user is creating a new series
        if action_id == "create_new_series":   
            message_ts = payload["container"]["message_ts"]
            isFromHelp = False
            if payload["actions"][0]["value"] == "from_help_message":
                isFromHelp = True

            pyBot.new_series_menu(channel_id, user_id, message_ts, isFromHelp)

            return make_response("New Series Created", 200)
        
        # If the user is editing the title of a series
        elif action_id == "edit_series_title":
            # Parse the trigger id needed to open a dialog
            trigger_id = payload["trigger_id"]
            pyBot.edit_series_title_dialog(trigger_id)

            return make_response("New Series Title edited", 200)
        
        # If the user is confirming the creation of a series
        elif action_id == "start_series":
            message_ts = payload["container"]["message_ts"]  
            pyBot.confirm_new_series(channel_id, user_id, message_ts)
            return make_response("New Series Confirmed", 200)
        
        # If the user cancels the creation of the new series
        elif action_id == "cancel_series":
            pyBot.cancel_new_series(channel_id)
            return make_response("New Series Cancelled", 200)
        
        # TODO write make_response return statements for the rest of the actions
        # If the user acknowledges warning about schedule being in the past
        elif action_id == "past_schedule_ok":
            message_ts = payload["container"]["message_ts"] 
            pyBot.delete_message(channel_id, message_ts)

        # If the user acknowledges message about successful series creation
        elif action_id == "series_creation_ok":
            message_ts = payload["container"]["message_ts"] 
            pyBot.delete_message(channel_id, message_ts)

        # If the user acknowledges message about having no series to read
        elif action_id == "no_series_read_ok":
            message_ts = payload["container"]["message_ts"] 
            pyBot.delete_message(channel_id, message_ts)

        # If the user cancels when reading a series
        elif action_id == "cancel_read_series":
            message_ts = payload["container"]["message_ts"]
            pyBot.reset_currentSeries()
            pyBot.delete_message(channel_id, message_ts)
        
        # If the user confirms the read for the series, go ahead and load the schedule.
        elif action_id == "confirm_read_series":
            message_ts = payload["container"]["message_ts"] 
            pyBot.printSchedule(channel_id, message_ts)

        # TODO If the user hits the button to go back to the Series Read menu
        elif action_id == "back_to_read":
            message_ts = payload["container"]["message_ts"] 
            pyBot.read_series_message(channel_id, user_id, message_ts)

        # If the user hits button to hide the schedule message
        # And clear the series on memory
        elif action_id == "hide_schedule_message":
            message_ts = payload["container"]["message_ts"] 
            pyBot.reset_currentSeries()
            pyBot.delete_message(channel_id, message_ts)
        
        # If the user confirms that they want to update the series go ahead and 
        # load the series configuration menu
        elif action_id == "confirm_update_series":
            message_ts = payload["container"]["message_ts"] 
            pyBot.updation_series_menu(channel_id, user_id, message_ts)  

        elif action_id == "cancel_update_series":
            message_ts = payload["container"]["message_ts"] 
            pyBot.reset_currentSeries()
            pyBot.delete_message(channel_id, message_ts)

        # If the user confirms the updation of the series
        elif action_id == "complete_update_series":    
            message_ts = payload["container"]["message_ts"]  
            pyBot.confirm_series_updation(channel_id, user_id, message_ts)
            return make_response("New Series Confirmed", 200)
        
        # If the user hit the back button in the series updation workflow
        elif action_id == "back_to_updation":
            message_ts = payload["container"]["message_ts"] 
            pyBot.updation_series_message(channel_id, user_id, message_ts)

        # If the user pushes the delete series button
        elif action_id == "delete_series":
            message_ts = payload["container"]["message_ts"]
            pyBot.delete_series(channel_id, user_id, message_ts)
            return make_response("Series Deleted", 200)

        # If the user acknowledged the series deletion notification
        elif action_id == "delete_series_ok":
            message_ts = payload["container"]["message_ts"] 
            pyBot.delete_message(channel_id, message_ts)

        # If the user wants to change the presenter for a session
        elif action_id == "change_session_presenter":
            # Exctract the message timestamp to dynamically update the message
            message_ts = payload["container"]["message_ts"] 
            # Extracting the session_index to display default values
            session_index = int(payload["actions"][0]["value"][14:])
            trigger_id = payload["trigger_id"]
            pyBot.change_session_presenter_dialog(trigger_id, session_index, message_ts)

        # If the user wants to change the topic for a session
        elif action_id == "change_session_topic":
            message_ts = payload["container"]["message_ts"] 
            # Extracting the session_index to display default values
            session_index = int(payload["actions"][0]["value"][14:])
            trigger_id = payload["trigger_id"]
            pyBot.change_session_topic_dialog(trigger_id, session_index, message_ts)
        
        # If the user hits the "close help" button
        elif action_id == "close_help_message":
            message_ts = payload["container"]["message_ts"] 
            pyBot.delete_message(channel_id, message_ts) 
        
        # If the user hits the "OK" button in the commands list menu
        elif action_id == "commands_list_ok":
            message_ts = payload["container"]["message_ts"] 
            pyBot.delete_message(channel_id, message_ts) 
        
        # If the user hits the "Serier Commands" button in the help message
        elif action_id == "show_app_commands":
            message_ts = payload["container"]["message_ts"]
            pyBot.show_app_commands(channel_id, message_ts)
        
        # If the user hits the button to go back the help message
        elif action_id == "back_to_help":
            message_ts = payload["container"]["message_ts"]
            pyBot.send_help_message(channel_id, message_ts)



    # ==================== DIALOG SUBMISSION ACTIONS ====================
    # If the user submitted a dialog

    elif action_type == "dialog_submission":
        if action_id == "update_series_title":

            # Update the series state to reflect the new title
            series_title = payload["submission"]["series_title"]
            pyBot.update_series_title(channel_id, series_title)

            # console log for the payload
            # print("\n" + 70*"="  + "\ninteractive event payload=\n", json.dumps(payload), "\n" + 70*"=")
            # A-OK
            return make_response("", 200)

        elif action_id == "update_session_presenter":
            # Extract the new session presenter
            session_presenter = payload["submission"]["session_presenter"]
            # The timestamp and the session_index is in the state string delimited by a comma
            message_ts, session_index = payload["state"].split(",")
            session_index = int(session_index)
            # Extract the channel_id to send the newly updated message
            channel_id = payload["channel"]["id"]
            pyBot.update_session_presenter(session_index, session_presenter, channel_id, message_ts)

            # console log for the payload
            # print("\n" + 70*"="  + "\ninteractive event payload=\n", json.dumps(payload), "\n" + 70*"=")
            # A-OK
            return make_response("", 200)

        elif action_id == "update_session_topic":
            # Extract the new session topic
            session_topic = payload["submission"]["session_topic"]
            # The timestamp and the session_index is in the state string delimited by a comma
            message_ts, session_index = payload["state"].split(",")
            session_index = int(session_index)
            # Extract the channel_id to send the newly updated message
            channel_id = payload["channel"]["id"]
            pyBot.update_session_topic(session_index, session_topic, channel_id, message_ts)


            return make_response("", 200)
    # ==================== USER_SELECT ACTIONS ====================
    # If the user picked an option from a user_select menu
    elif action_type == "users_select":
        if action_id == "select_series_presenter":
        # TODO do something with the payload["actions"]["selected_user"]
            series_presenter = payload["actions"][0]["selected_user"]

            pyBot.update_series_presenter(channel_id, series_presenter)
            return make_response("New Series Presenter Selected", 200)


    # ==================== STATIC_SELECT MENU ACTIONS ====================
    # If the user picked an option from a static select menu
    elif action_type == "static_select":
        if action_id == "select_topic_selection":
            # TODO do something with the payload["actions"]["selected_option"]["value"]. 
            # It is either "pre-determined" OR "presenter_choice"
            topic_selection = payload["actions"][0]["selected_option"]["value"]

            pyBot.update_topic_selection(channel_id, topic_selection)
            return make_response("New Series Topic Selection updated", 200)

        # If the user picked a series time
        elif action_id == "select_series_time":
            # Format for the time: '%I:%M %p'
            # Might want to convert this to python time format later in backend
            series_time = payload["actions"][0]["selected_option"]["text"]["text"]
            
            pyBot.update_series_time(channel_id, series_time)
            return make_response("New Series Time updated", 200)

        # If the user selected a frequency for the series
        elif action_id == "select_series_frequency":
            # TODO do something with the payload["actions"]["selected_option"]["value"]
            # Format: it will be the string option except delimited by "-" and lowercase.
            # Examples: "every-day", "every-2-weeks"
            series_frequency = payload["actions"][0]["selected_option"]["value"]

            pyBot.update_series_frequency(channel_id, series_frequency)
            return make_response("New Series Frequency Updated", 200)

        # If the user selected the number of sessions in the series
        elif action_id == "select_series_numsessions":
            # It will be in format "numsessions-num". Example: "numsessions-8".
            series_numsesions = int(payload["actions"][0]["selected_option"]["value"][12:])
            pyBot.update_series_numsessions(channel_id, series_numsesions)
            return make_response("New Series Numsessions Updated", 200)

        # If the user selected the series they want to read, make it the current
        # Series
        elif action_id == "select_series_read":
            # console log for the payload
            # print("\n" + 70*"="  + "\ninteractive event payload=\n", json.dumps(payload), "\n" + 70*"=")

            # update the read menu message to show a confirm button
            message_ts = payload["container"]["message_ts"]
            # Parse original message blocks to update
            message_blocks = payload["message"]["blocks"]
            pyBot.update_read_series_message(channel_id, message_ts, message_blocks)

            # Extract the series id from the payload
            series_id = payload["actions"][0]["selected_option"]["value"][10:]
            # Update the series in memory to be the one that the user selected
            pyBot.setSeries(series_id)

        # If the user selected the series they want to update, make it the current
        # Series
        elif action_id == "select_series_update":
            # console log for the payload
            # print("\n" + 70*"="  + "\ninteractive event payload=\n", json.dumps(payload), "\n" + 70*"=")

            # update the read menu message to show a confirm button
            message_ts = payload["container"]["message_ts"]
            # Parse original message blocks to update
            message_blocks = payload["message"]["blocks"]
            pyBot.update_updation_series_message(channel_id, message_ts, message_blocks)

            # Extract the series id from the payload
            series_id = payload["actions"][0]["selected_option"]["value"][10:]
            # Update the series in memory to be the one that the user selected
            pyBot.setSeries(series_id)


    # ==================== DATEPICKER ACTIONS ====================
    # If the user picked a date
    elif action_type == "datepicker":
        if action_id == "pick_series_date":
            # Date format: "%Y-%m-%d"
            # Example: 2019-07-27"
            series_date = payload["actions"][0]["selected_date"]

            pyBot.update_series_menu_date(channel_id, series_date)
            return make_response("New Series Date updated", 200)


    # If there is an action event that the app can not handle
    # Return an error message
    return make_response("App not equipped for this event", 200, {"X-Slack-No-Retry": 1})



@app.route("/actions", methods=["POST"])
def action():
    """
    This is the endpoint Slack will send interactive events to
    """
    # First, verify that the request is coming from Slack by checking the Signing Secret
    # To verify the signature, extract the relevant information from the request
    timestamp = request.headers['X-Slack-Request-Timestamp']
    signature = request.headers['X-Slack-Signature']
    request_body = request.get_data()

    # If it doesn't pass verification, stop it right there
    if not verify_signature(timestamp, signature, request_body):
        return make_response("Invalid Signing Signature on Request", 403)

    # Now that the request is verified, extract the payload.
    payload = json.loads(request.form["payload"])

    # console log for the payload
    # print("\n" + 70*"="  + "\ninteractive event payload=\n", json.dumps(payload), "\n" + 70*"=")

    # Parse the payload for the team_id to connect to the client
    # TODO Are we connecting to the client on EVERY action?? Isn't that a lot? Slow?
    team_id = payload["team"]["id"]
    pyBot.client_connect(team_id)


    action_type, action_id = "", ""
    # If the action is a dialog submission
    if payload["type"] == "dialog_submission":
        # Parse the payload for the action type and the action id
        action_type = "dialog_submission"
        action_id = payload["callback_id"]

    # Otherwise it is a block action
    else: 
        action_type = payload["actions"][0]["type"]
        action_id = payload["actions"][0]["action_id"]

    # console log for the data collected from payload
    # print("\n" + 70*"="  + "\nNEW ACTION RECEIVED\n(action_type, action_id)=\n", (action_type, action_id), "\n" + 70*"=")

    # Pass on the action event to the action handler routing function
    return _action_handler(payload, action_type, action_id)


def _slash_handler(payload, slash_command, slash_text):
    """
    Helper method to handle Slack slash commands. 
    Route incoming slash commands to the bot by slash command and text

    """
    channel_id = payload["channel_id"]
    user_id = payload["user_id"]
    # If the user paged the bot with empty text or with the word help
    # then send the user the help message
    if slash_text == "" or slash_text == "help":
        pyBot.send_help_message(channel_id)
        return make_response("", 200)

    # TODO NAME THESE BETTER

    # If the user wants to create a new series
    elif slash_text == "create":
        pyBot.new_series_menu(channel_id, user_id)
        return make_response("", 200)
    # If the user wants to see already existing series.
    elif slash_text == "read":
        pyBot.read_series_message(channel_id, user_id)
        return make_response("", 200)

    elif slash_text == "update":
        pyBot.updation_series_message(channel_id, user_id)
        return make_response("", 200)
    
    elif slash_text == "commands":
        pyBot.show_app_commands(channel_id)
        return make_response("", 200)

    # if the command was none of the above.
    else:
        # TODO add helpful reroute here. Like the boilerplate DM response message
        # or a help message.
        pyBot.dm_response_message(channel_id)
        return make_response("", 200)

@app.route("/slash", methods=["POST"])
def serier():
    """
    This is the slash command endpoint.
    """
    # First, verify that the request is coming from Slack by checking the Signing Secret
    # To verify the signature, extract the relevant information from the request
    timestamp = request.headers['X-Slack-Request-Timestamp']
    signature = request.headers['X-Slack-Signature']
    request_body = request.get_data()

    # If it doesn't pass verification, stop it right there
    if not verify_signature(timestamp, signature, request_body):
        return make_response("Invalid Signing Signature on Request", 403)

    # Extract the payload from the slash command
    payload = dict(request.form)

    # Extract the team_id and connect to client
    # TODO Are we connecting to the client on EVERY action?? Isn't that a lot? Slow?
    team_id = payload["team_id"]
    pyBot.client_connect(team_id)


    # Extract the slash command the parameter text
    slash_command = payload["command"]
    slash_text = payload["text"].strip().lower() # remove whitespace and make it lowercase

    return _slash_handler(payload, slash_command, slash_text)

@app.route("/install", methods=["GET"])
def pre_install():
    """This route renders the installation page with 'Add to Slack' button."""
    # Since we've set the client ID and scope on our Bot object, we can change
    # them more easily while we're developing our app.
    client_id = pyBot.oauth["client_id"]
    scope = pyBot.oauth["scope"]
    # Our template is using the Jinja templating language to dynamically pass
    # our client id and scope
    return render_template("install.html", client_id=client_id, scope=scope)

@app.route("/thanks", methods=["GET", "POST"])
def thanks():
    """This route is called by Slack after the user installs our app. It will
    exchange the temporary authorization code Slack sends for an OAuth token
    which we'll save on the Bot object to use later.
    To let the user know what's happened it will also render a thank you page.
    """
    # Grab the temporary authorization code Slack's sent us from
    # the request's parameters.
    code_arg = request.args.get("code")
    # console log for the payload
    # print("\n" + 70*"="  + "\nOAuth temporary code =\n", code_arg, "\n" + 70*"=")

    # The Bot's auth method handles exchanging the code for an OAuth token
    pyBot.auth(code_arg)
    return render_template("thanks.html")


if __name__ == '__main__':
    app.run(debug=True)