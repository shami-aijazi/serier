"""
Python Slack Bot class for use with series organizer app
"""
import os
import message

from slackclient import SlackClient

# To remember which teams have authorized your app and what tokens are
# associated with each team, we can store this information in memory on
# as a global object. When your bot is out of development, it's best to
# save this in a more persistant memory store.
authed_teams = {}

class Bot(object):
    """ Instatiates a Bot object to handle Slack interactions"""
    def __init__(self):
        super(Bot, self).__init__()
        self.name = "bronby"
        # When we instantiate a new bot object, we can access the app
        # credentials we set earlier in our local development environment.
        self.oauth = {"client_id": os.environ.get("CLIENT_ID"),
                      "client_secret": os.environ.get("CLIENT_SECRET"),
                      # Scopes provide and limit permissions to what our app
                      # can access. It's important to use the most restricted
                      # scope that your app will need.
                      "scope": "bot"}
        self.verification = os.environ.get("VERIFICATION_TOKEN")
        self.emoji = ":smile:"

        # NOTE: Python-slack requires a client connection to generate
        # an oauth token. We can connect to the client without authenticating
        # by passing an empty string as a token and then reinstantiating the
        # client with a valid OAuth token once we have one.

        # TODO it is hardcoded for now. Fix it later
        self.client = SlackClient("xoxb-362487356881-688022100224-t1Tktzjdj7k5kIxVcBVtRJLB")

    def open_dm(self, user_id):
        """
        Open a DM to send a greeting message to a new installing user

        Parameters
        ----------
        user_id : str
            id of the Slack user associated with the installation

        Returns
        ----------
        dm_id : str
            id of the DM channel opened by this method
        """
        new_dm = self.client.api_call("im.open",
                                      user=user_id)

        # console log for the new_dm im.open response object
        print "\n===============\nnew_dm =\n", new_dm, "\n==============="

        dm_id = new_dm["channel"]["id"]
        return dm_id


    def greeting_message(self, user_id, team_id=""):
        """
        Create and send a welcome message to a new user upon installation.
        :param user_id: str
            id of the Slack user associated with the incoming event
        :param team_id: str
            id of the Slack team associated with the incoming event

        """

        # create a Greeting message Message object
        # set the appropiate channel_id to the Message object (use im.open?)
        # connect to the right slack client token
        # post the message

        message_obj = message.Greeting()
        # Then we'll set the message object's channel attribute to the IM
        # channel of the user we'll communicate with. We'll find this using
        # the open_dm function, which uses the im.open API call.
        message_obj.channel = self.open_dm(user_id)

        post_message = self.client.api_call("chat.postMessage",
                                            channel=message_obj.channel,
                                            username=self.name,
                                            icon_emoji=self.emoji,
                                            text=message_obj.text,
                                            # attachments=message_obj.attachments
                                            )

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
        auth_response = self.client.api_call(
                            "oauth.access",
                            client_id=self.oauth["client_id"],
                            client_secret=self.oauth["client_secret"],
                            code=code
                            )
        # To keep track of authorized teams and their associated OAuth tokens,
        # we will save the team ID and bot tokens to the global authed_teams object
        # TODO WRITE authed_teams object to database?
        team_id = auth_response["team_id"]
        authed_teams[team_id] = {"bot_token":
                                 auth_response["bot"]["bot_access_token"]}
        # Then we'll reconnect to the Slack Client with the correct team's
        # bot token
        # self.client = SlackClient(authed_teams[team_id]["bot_token"])
        # TODO we might have to do this before every api call to support multiple teams
        # TODO query from database to connect to the client?

        # TODO send a greeting message to the installer
        # HOW CAN WE KNOW WHICH CHANNEL TO DM THE INSTALLER ON WITH BOT SCOPE?
        # Try the im.open slack api call?
