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
			"text": "Hi! I'm Serier :wave: \nUnfortunately, I can't do much right now. I am working on it... :wrench: \nWatch this space!"
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
	},
	{
		"type": "section",
		"text": {
			"type": "mrkdwn",
			"text": "Pick a date for the start of the series."
		},
		"accessory": {
			"type": "datepicker",
			"initial_date": "2019-07-28",
			"placeholder": {
				"type": "plain_text",
				"text": "Select a date",
				"emoji": True
			}
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
					"text": "Submit"
				},
				"value": "submit_series_date",
                "style": "primary"
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
					"emoji": true,
					"text": "Organize a series"
				},
				"value": "organize_series"
			}
		]
	}
]