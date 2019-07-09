"""
Python Slack Message class for use with the bot
"""

class Greeting(object):
    """
    A Message object to create and manage
    greeting messages for new installers
    """

    def __init__(self):
        super(Greeting, self).__init__()
        self.channel = ""
        self.timestamp = ""
        self.text = "Hi! Welcome to this app :wave: " +\
                    "\nI can help you organize and run your bookclub or brownbag series :books:"
        # self.attachments = [
        #    {
        #     "fallback": "You are unable to start a series",
        #     "callback_id": "series_organize_button",
        #     "color": "#778e83",
        #     "actions": [
        #         {
        #             "name": "series_organize_button",
        #             "text": "Organize a series",
        #             "type": "button",
        #             "value": "organize_series"
        #         }
        #     ]
        #    }
        #   ]