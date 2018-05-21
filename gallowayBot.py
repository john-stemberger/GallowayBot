import re
import json
import time
import random
from slackclient import SlackClient

class Classroom:
	def __init__(self):
		self.questions = None;
		self.answers = [];
		self.questionIndex = -1
		self.tries=0

	def processClassroomSetup(self, slack_client, channelName, message_text):
		print "processClassroomSetup " + message_text
		if self.questions == None:
			print "Classroom Introduction"
			self.questions = [];
			slack_client.api_call(
				"chat.postMessage",
				channel=channelName,
				text="Hello and welcome to my Classroom\n" + 
				      "What would you like to practice today?\n" + 
				      "1 - Hiragana\n" + 
				      "2 - Katakana\n" + 
				      "3 - Hiragana & Katakana\n" + 
				      "Make sure you say goodbye to me before you leave class",
				as_user=True)
		elif message_text == "1":
			print "Studying Hiragana"
			self.questions.extend(hiragana)
			self.answers.extend(romanji)
			self.refreshQuestion()
			self.postNewQuestion(slack_client, channelName)
		elif message_text == "2":
			print "Studying Katakana"
			self.questions.extend(katakana)
			self.answers.extend(romanji)
			self.refreshQuestion()
			self.postNewQuestion(slack_client, channelName)
		elif message_text == "3":
			print "Studying Hiragana & Katakana"
			self.questions.extend(hiragana)
			self.questions.extend(katakana)
			self.answers.extend(romanji) # one set for hiragana
			self.answers.extend(romanji) # one set for katakana
			self.refreshQuestion()
			self.postNewQuestion(slack_client, channelName)
		else:
			print "Classroom Introduction Take 2"
			slack_client.api_call(
				"chat.postMessage",
				channel=channelName,
				text="Sorry, I did not understand that\n" + 
				      "What would you like to practice today?\n" + 
				      "1 - Hiragana\n" + 
				      "2 - Katakana\n" + 
				      "3 - Hiragana & Katakana\n" + 
				      "Make sure you say goodbye to me before you leave class",
				as_user=True)

	def processMessage(self, slack_client, channelName, message_text):
		print "processMessage: " + message_text
		if self.questionIndex == -1:
			print "processMessage - setup"
			self.processClassroomSetup(slack_client, channelName, message_text)
		elif re.match(r'goodbye', message_text, re.IGNORECASE):
			print "processMessage - tearDown"
			slack_client.api_call(
				"chat.postMessage",
				channel=channelName,
				text="Bye",
				as_user=True)
			self.questions = None;
			self.answers = [];
			self.questionIndex = -1
			self.tries=0
		elif self.answers[self.questionIndex].lower() == message_text.lower(): 
			print "processMessage - answer correct"
			slack_client.api_call(
				"chat.postMessage",
				channel=channelName,
				text="CORRECT!",
				as_user=True)
			self.refreshQuestion()
			self.postNewQuestion(slack_client, channelName)
		elif self.tries +1< MAX_TRIES:
			print "processMessage - answer incorrect"
			self.tries = self.tries + 1
			slack_client.api_call(
				"chat.postMessage",
				channel=channelName,
				text="Not quite :( you have " + str(MAX_TRIES - self.tries) + " tries left",
				as_user=True)
			self.postNewQuestion(slack_client, channelName)
		else:
			print "processMessage - answer incorrect take 2"
			slack_client.api_call(
				"chat.postMessage",
				channel=channelName,
				text="Sorry, the correct answer is " + self.answers[self.questionIndex],
				as_user=True)
			self.refreshQuestion()
			self.postNewQuestion(slack_client, channelName)

	def postNewQuestion(self, slack_client, channelName): 
		question = "".join(["What is the sound that ", self.questions[self.questionIndex], " makes?"])
		slack_client.api_call(
			"chat.postMessage",
			channel=channelName,
			text=question,
			as_user=True)
	
	def refreshQuestion(self): 
		self.questionIndex = random.randint(0, len(self.questions)-1)
		self.tries = 0;


API_KEY_FILE = "slack_api_key.txt"

MY_NAME = "gallowaysensei"
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

katakana=[u'\u30A2', u'\u30A4', u'\u30A6', u'\u30A8', u'\u30aa', 
u'\u30AB', u'\u30AD', u'\u30AF', u'\u30B1', u'\u30B3', 
u'\u30B5', u'\u30B7', u'\u30B9', u'\u30BB', u'\u30BD', 
u'\u30BF', u'\u30C1', u'\u30C4', u'\u30C6', u'\u30C8', 
u'\u30CA', u'\u30CB', u'\u30CC', u'\u30CD', u'\u30CE', 
u'\u30CF', u'\u30D2', u'\u30D5', u'\u30D8', u'\u30DB', 
u'\u30DE', u'\u30DF', u'\u30E0', u'\u30E1', u'\u30E2', 
u'\u30E4',            u'\u30E6',            u'\u30E8', 
u'\u30E9', u'\u30EA', u'\u30EB', u'\u30EC', u'\u30ED', 
u'\u30EF',            u'\u30F2',            u'\u30f3', 
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

def isMesageToMe(message):
	if 'user' in message and message['user'] == slack_user_id:
		return False
	if 'type' in message and message['type'] == 'message':
		if 'text' in message and message['text'].startswith("<@%s>" % slack_user_id):
			return True
		if 'channel' in message and message['channel'].startswith('D'):
			return True
	return False

def extractMessage(message): 
	message_text = message['text']
	if message['text'].startswith("<@%s>" % slack_user_id):
		message_text = message['text'].\
			split("<@%s>" % slack_user_id)[1].\
			strip()
	return message_text

lines = [line.rstrip('\n') for line in open(API_KEY_FILE)]
slack_client = SlackClient(lines[0])

# Fetch your Bot's User ID
user_list = slack_client.api_call("users.list")
for user in user_list.get('members'):
	if user.get('name') == MY_NAME:
		slack_user_id = user.get('id')
		break

# Start connection
if slack_client.rtm_connect():
	print("Connected!")
	while True:
		for message in slack_client.rtm_read():
			if isMesageToMe(message):
				print "Message received: %s" % json.dumps(message, indent=2)
				if message['channel'] in classrooms.keys():
					print ("passing message to classroom")
					room = classrooms[message['channel']]
				else:
					print ("creating new classroom")
					room = Classroom()
					classrooms[message['channel']] = room

				message_text = extractMessage(message)
				room.processMessage(slack_client, message['channel'], message_text)

		time.sleep(1)
