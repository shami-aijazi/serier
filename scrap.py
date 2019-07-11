# import json

# with open('authed_teams.txt', 'r+') as authed_teams_file: 
#     print authed_teams_file.read()
#     # try: 
#     authed_teams = json.load(authed_teams_file)

#     # Console log for reinstallation process
#     print "\n===============\nauthed_teams=\n", authed_teams, "\n==============="
#     print "\n===============\nauthed_teams already exists, updating... =\n", "\n==============="
#     # except ValueError: 
#         # authed_teams = {}
#         # Console log for reinstallation process
#         # print "\n===============\nauthed_teams does not already exist, creating new... =\n", "\n==============="

#     # team_id = auth_response["team_id"]
#     # authed_teams[team_id] = {"bot_token":
#         # auth_response["bot"]["bot_access_token"]}
    
#     json.dump(authed_teams, authed_teams_file)



# Log all the oauth env variables
import os
print "CLIENT_ID = ", os.environ['CLIENT_ID']
print "CLIENT_SECRET = ", os.environ['CLIENT_SECRET']
print "VERIFICATION_TOKEN = ", os.environ['VERIFICATION_TOKEN']

