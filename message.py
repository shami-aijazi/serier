"""
Slack Message class for use with the series organizer bot
"""

class DMResponse(object):
    """
    A Message object to create and manage
    response messages to User DMs
    """

    def __init__(self):
        super(DMResponse, self).__init__()
        self.channel = ""
        self.timestamp = ""
        self.text = "Sorry, I didn't get that. Just say `help` to find out what I can do!"


class Help(object):
    """
    A help message object
    """
    def __init__(self):
        super(Help, self).__init__()
        self.channel = ""
        self.timestamp = ""
        self.text = "Hi! I'm Serier :wave: \n" +\
            "Unfortunately, I can't do much right now. I am working on it... :wrench: \n" +\
            "Watch this space!"
        self.attachments = [
            {
            "fallback": "You are unable to start a series",
            "callback_id": "series_organize_button",
            "color": "#778e83",
            "actions": [
                {
                    "name": "series_organize_button",
                    "text": "Organize a series",
                    "type": "button",
                    "value": "organize_series"
                }
            ]
            }
            ]

class Onboarding(object):
    """
    A Message object to create and manage
    onboarding messages for new installers
    """

    def __init__(self):
        super(Onboarding, self).__init__()
        self.channel = ""
        self.timestamp = ""
        self.text = "Hi! Welcome to this app :wave: " +\
                    "\nI can't do much right now. But in the future I will be able to " +\
                        "help you organize and run your bookclub or brownbag series :books:"
        self.attachments = [
           {
            "fallback": "You are unable to start a series",
            "callback_id": "series_organize_button",
            "color": "#778e83",
            "actions": [
                {
                    "name": "series_organize_button",
                    "text": "Organize a series",
                    "type": "button",
                    "value": "organize_series"
                }
            ]
           }
          ]