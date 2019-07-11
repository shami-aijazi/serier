"""
A routing layer for the series organizer bot.
Code inspired by pythOnboarding tutorial by Slack.

"""

import json
import bot
from flask import Flask, request, make_response, render_template
from slackeventsapi import SlackEventAdapter

pyBot = bot.Bot()

slack = pyBot.client  # Where is this ever used in this file?

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
    # parse team_id to connect to client
    team_id = slack_event["team_id"]
    pyBot.client_connect(team_id)

    # Check if it is a direct message
    if slack_event["event"]['channel_type'] == 'im':
        # console log for the event
        # print "\n===============\nslack_event =\n", slack_event, "\n==============="

        # Check if the message is a user message (don't count the bot's own messages.)
        if "client_msg_id" in slack_event["event"]:
            user_id = slack_event["event"]["user"]
            # Send the greeting message to the user who sent it
            pyBot.greeting_message(user_id)
            return make_response("Hello DM Sent", 200,)

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


if __name__ == '__main__':
    app.run(debug=True)