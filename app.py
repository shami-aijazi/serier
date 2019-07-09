"""
A routing layer for the series organizer bot.
Code inspired by pythOnboarding tutorial by Slack.

"""

import json
import bot
from flask import Flask, request, make_response, render_template

pyBot = bot.Bot()

slack = pyBot.client  # Where is this ever used in this file?

app = Flask(__name__)

def _event_handler(event_type, slack_event):
    """
    A helper function that routes events from Slack to the Bot
    by event type and subtype
    :param event_type: str
        type of event received from Slack
    :param slack_event: dict
        JSON response from a Slack event
    :return: obj
        Response object with 200 - OK or 500 - No Event Handler error
    """
    # TODO watch this space. Might need team_id later down the line to handle multiple workspaces
    team_id = slack_event["team_id"]

    # ================ IM Events ===============
    # When the user sends a message to the bot on a direct message channel
    if event_type == "message" and slack_event["event"]['channel_type'] == 'im':
        # console log for the event
        # print "\n===============\nslack_event =\n", slack_event, "\n==============="

        # If the message is a user message. Don't count the bot's own message.
        if "client_msg_id" in slack_event["event"]:
            # user_id = slack_event["event"].get("user")
            user_id = slack_event["event"]["user"]


            # Send the greeting message
            pyBot.greeting_message(team_id, user_id)
            return make_response("Hello DM Sent", 200,)


    # ============= Event Type Not Found! ============= #
    # If the event_type does not have a handler
    message = "App not equipped to handle this %s event" % event_type
    # Return a helpful error message
    return make_response(message, 200, {"X-Slack-No-Retry": 1})

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
    # The Bot's auth method handles exchanging the code for an OAuth token
    pyBot.auth(code_arg)
    return render_template("thanks.html")

@app.route("/listening", methods=["GET", "POST"])
def hears():
    """
    This route listens for incoming events from Slack and uses the event
    handler helper function to route events to the Bot
    """
    slack_event = json.loads(request.data)

    # ============= Slack URL Verification ============ #
    # In order to verify the url of our endpoint, Slack will send a challenge
    # token in a request and check for this token in the response our endpoint
    # sends back.
    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type":
                                                                 "application/json"
                                                             })
    # ============ Slack Token Verification =========== #
    # Verify that the request is coming from Slack by checking that the
    # verification token in the request matches our app's settings
    if pyBot.verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s \npyBot has: \
                   %s\n\n" % (slack_event["token"], pyBot.verification)
        # By adding "X-Slack-No-Retry" : 1 to our response headers, we turn off
        # Slack's automatic retries during development.
        make_response(message, 403, {"X-Slack-No-Retry": 1})


    # ====== Process Incoming Events from Slack ======= #
    # If the incoming request is an Event we've subscribed to
    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        # Then handle the event by event_type and have the Bot respond
        return _event_handler(event_type, slack_event)
    # If our bot hears things that are not events we've subscribed to,
    # send an error response
    return make_response("[NO EVENT IN SLACK REQUEST]", 404, {"X-Slack-No-Retry": 1})

if __name__ == '__main__':
    app.run(debug=True)