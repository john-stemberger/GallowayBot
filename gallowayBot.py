import re
import json
import time
import random
from slackclient import SlackClient

class Classroom:
	def __init__(self):
		self.questionIndex = 15
		self.tries=0
		self.refreshQuestion()

	def processMessage(self, slack_client, channelName, message_text):
		if re.match(r'quiz me', message_text, re.IGNORECASE):
			self.refreshQuestion()
			self.postNewQuestion(slack_client, channelName)
		elif romanji[self.questionIndex].lower() == message_text.lower(): 
			slack_client.api_call(
				"chat.postMessage",
				channel=channelName,
				text="CORRECT!",
				as_user=True)
			self.refreshQuestion()
			self.postNewQuestion(slack_client, channelName)
		elif self.tries +1< MAX_TRIES:
			self.tries = self.tries + 1
			slack_client.api_call(
				"chat.postMessage",
				channel=channelName,
				text="Not quite :( you have " + str(MAX_TRIES - self.tries) + " tries left",
				as_user=True)
			self.postNewQuestion(slack_client, channelName)
		else:
			slack_client.api_call(
				"chat.postMessage",
				channel=channelName,
				text="Sorry, the correct answer is " + romanji[self.questionIndex],
				as_user=True)
			self.refreshQuestion()
			self.postNewQuestion(slack_client, channelName)

	def postNewQuestion(self, slack_client, channelName): 
		question = "".join(["What is the sound that ", hiragana[self.questionIndex], " makes?"])
		slack_client.api_call(
			"chat.postMessage",
			channel=channelName,
			text=question,
			as_user=True)
	
	def refreshQuestion(self): 
		self.questionIndex = random.randint(0, len(hiragana)-1)
		self.tries = 0;


API_KEY_FILE = "slack_api_key.txt"

MAX_TRIES = 3
classrooms = {}
questionIndex = 15
tries=0

hiragana=[u'\u3042', u'\u3044', u'\u3046', u'\u3048', u'\u304a', 
u'\u304B', u'\u304D', u'\u304F', u'\u3051', u'\u3053', 
u'\u3055', u'\u3057', u'\u3059', u'\u305B', u'\u305D', 
u'\u305F', u'\u3061', u'\u3064', u'\u3066', u'\u3068', 
u'\u306A', u'\u306B', u'\u306C', u'\u306D', u'\u306E', 
u'\u306F', u'\u3072', u'\u3075', u'\u3078', u'\u307B', 
u'\u307E', u'\u307F', u'\u3080', u'\u3081', u'\u3082', 
u'\u3084',            u'\u3086',            u'\u3088', 
u'\u3089', u'\u308A', u'\u308B', u'\u308C', u'\u308D', 
u'\u308F',            u'\u3092',            u'\u3093', 
]

romanji=["a", "i", "u", "e", "o", 
"ka", "ki",  "ku",  "ke", "ko", 
"sa", "shi", "su",  "se", "so", 
"ta", "chi", "tsu", "te", "to", 
"na", "ni",  "nu",  "ne", "no", 
"ha", "hi",  "fu",  "he", "ho", 
"ma", "mi",  "mu",  "me", "mo", 
"ya",        "yu",        "yo", 
"ra", "ri",  "ru",  "re", "ro", 
"wa", "wo", "n"]

lines = [line.rstrip('\n') for line in open(API_KEY_FILE)]
slack_client = SlackClient(lines[0])

# Fetch your Bot's User ID
user_list = slack_client.api_call("users.list")
for user in user_list.get('members'):
	if user.get('name') == "pibot":
		slack_user_id = user.get('id')
		break

# Start connection
if slack_client.rtm_connect():
	print("Connected!")
	for i in range(0, len(hiragana)):
		print (hiragana[i] + " = " + romanji[i])
	while True:
		for message in slack_client.rtm_read():
			# print "Message received: %s" % json.dumps(message, indent=2)
			if 'text' in message and message['text'].startswith("<@%s>" % slack_user_id):
				print ("Message received: %s" % json.dumps(message, indent=2))
				if message['channel'] in classrooms.keys():
					print ("passing message to classroom")
					room = classrooms[message['channel']]
				else:
					print ("creating new classroom")
					room = Classroom()
					classrooms[message['channel']] = room

				message_text = message['text'].\
					split("<@%s>" % slack_user_id)[1].\
					strip()
				room.processMessage(slack_client, message['channel'], message_text)

		time.sleep(1)
