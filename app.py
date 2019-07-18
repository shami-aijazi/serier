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
    # print("\n" + 70*"="  + "\nslack_event=\n", slack_event, "\n" + 70*"=")

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

            # === User asked for help ===
            if message_text[:4]=="help":
                pyBot.help_message(channel_id)
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
    req: str
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
    
    sig_basestring = str.encode('v0:' + str(timestamp) + ':') + request.get_data()

    request_hash = 'v0=' + hmac.new(
                str.encode(pyBot.signing_secret),
                sig_basestring, hashlib.sha256
            ).hexdigest()
    
    # Compare the generated hash and incoming request signature
    return hmac.compare_digest(request_hash, signature)

def _action_handler (payload, action_type, action_id):
#     """
#     A helper function that routes user interactive actions to our Bot
#     by action type and and action id.
#     """
#     # TODO actually write the pyBot functions that are assumed to be there

    # Extract the original message timestamp and channel_id
    # in order to update the message as the state of the series changes
    message_ts = payload["container"]["message_ts"]
    channel_id = payload["container"]["channel_id"]


    # ==================== BUTTON ACTIONS ====================
    if action_type == "button":
        # If the user is creating a new series
        if action_id == "create_new_series":     
            pyBot.new_series_menu(channel_id, message_ts)
        
    #     # If the user is editing the title of a series
    #     elif action_id == "edit_series_title":
    #         pyBot.edit_series_title_dialog()
        
    #     # If the user is confirming the creation of a series
    #     elif action_id == "start_series":
    #         pyBot.confirm_new_series()
        
    #     # If the user cancels the creation of the new series
        elif action_id == "cancel_series":
            pyBot.cancel_new_series(channel_id, message_ts)

    # # ==================== USER_SELECT ACTIONS ====================
    # # If the user picked an option from a user_select menu
    elif action_type == "users_select":
        if action_id == "select_series_presenter":
        # TODO do something with the payload["actions"]["selected_user"]
            series_presenter = payload["actions"][0]["selected_user"]

            pyBot.update_series_presenter(channel_id, message_ts, series_presenter)


    # # ==================== STATIC_SELECT MENU ACTIONS ====================
    # # If the user picked an option from a static select menu
    # elif action_type == "static_select":
    #     if action_id == "select_topic_selection":
    #         # TODO do something with the payload["actions"]["selected_option"]["value"]. 
    #         # It is either "pre-determined" OR "presenter_choice"
    #         pyBot.update_topic_selection()

    #     # If the user picked a series time
    #     elif action_id == "select_series_time":
    #         # TODO do something with the payload["actions"]["selected_option"]["value"]
    #         # this will be in "time-tttt" format. Example "time-0215" for 2:15 PM
    #         pyBot.update_series_time

    #     # If the user selected a frequency for the series
    #     elif action_id == "select_series_frequency":
    #         # TODO do something with the payload["actions"]["selected_option"]["value"]
    #         # Format: it will be the string option except delimited by "-" and lowercase.
    #         # Examples: "every-day", "every-2-weeks"
    #         pyBot.update_series_frequency

    #     # If the user selected the number of sessions in the series
    #     elif action_id == "select_series_numsessions":
    #         # TODO do something with the payload["actions"]["selected_option"]["value"]
    #         # It will be in format "numsessions-num". Example: "numsessions-8".
    #         pyBot.update_series_numsessions


    # # ==================== DATEPICKER ACTIONS ====================
    # # If the user picked a date
    # elif action_type == "datepicker":
    #     if action_id == "pick_series_date":
    #         pyBot.update_series_menu_date()



    return True


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
    team_id = payload["team"]["id"]
    pyBot.client_connect(team_id)

    # Parse the payload for the action type and the action id
    action_type = payload["actions"][0]["type"]
    action_id = payload["actions"][0]["action_id"]

    # console log for the data collected from payload
    print("\n" + 70*"="  + "\nNEW ACTION RECEIVED\n(action_type, action_id)=\n", (action_type, action_id), "\n" + 70*"=")

    # Pass on the action event to the action handler routing function
    _action_handler(payload, action_type, action_id)

    # Send an HTTP 200 response
    return make_response("Interaction Received", 200)


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
    print("\n" + 70*"="  + "\nOAuth temporary code =\n", code_arg, "\n" + 70*"=")

    # The Bot's auth method handles exchanging the code for an OAuth token
    pyBot.auth(code_arg)
    return render_template("thanks.html")


if __name__ == '__main__':
    app.run(debug=True)