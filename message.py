"""
Slack Message class for use with the series organizer bot
"""
import json
from new_series_menu_blocks import new_series_menu_blocks


# ============================= BASIC BOT MESSAGES =============================
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
        self.blocks = [
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "Sorry, I didn't get that. Just say `help` to find out what I can do!"
        }
    }
]

class Help(object):
    """
    A help message object
    """
    def __init__(self):
        super(Help, self).__init__()
        self.channel = ""
        self.timestamp = ""
        self.text= "Help message"
        self.blocks = [
	{
		"type": "section",
		"text": {
			"type": "mrkdwn",
			"text": "Hi! I'm Serier :wave: \nI am still a work in progress :wrench: \nFor now, try hitting this button:"
		}
	},
	{
		"type": "actions",
		"elements": [
			{
				"type": "button",
				"action_id": "create_new_series",
				"text": {
					"type": "plain_text",
					"emoji": True,
					"text": "Organize a series"
				},
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
        self.text = "Hi! Welcome to this app"
        self.blocks = [
	{
		"type": "section",
		"text": {
			"type": "mrkdwn",
			"text": "Hi! Welcome to this app :wave: \nI can't do much right now. But in the future I will be able to help you organize and run your bookclub or brownbag series :books:"
		}
	},
	{
		"type": "actions",
		"elements": [
			{
				"type": "button",
				"action_id": "123",
				"text": {
					"type": "plain_text",
					"emoji": True,
					"text": "Organize a series"
				},
				"value": "organize_series"
			}
		]
	}
]