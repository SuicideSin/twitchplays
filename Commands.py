import pickle
import time
import datetime
import random
import re

from Cleverbot import chat, CW
from Controller import savestate, loadstate
from Users import User, USERS, LEVELS, LEVELS_INV, COLORS
from Parser import parse
from colorama import *
from profanity import profanity
from threading import Thread
from TwitchBot import sendmessage, sendwhisper

FLAGS = {
	"default": 0,
	"macro": 1,
	"meme": 2,
	"hidden_meme": 3
}

TUTORIAL_URL = "https://pastebin.com/26NeMcpN"
LEVEL_INFO = "User levels: 0 (viewer), 1 (whitelisted), 2 (superviewer), 3 (moderator), 4 (admin). For some games, certain inputs are whitelisted or superviewers will have access to !savestate and !loadstate."
BOT_INFO = "MrDestructoid I am a Twitch Plays program written in Python. Type buttons in chat to play and type !tutorial or !commands for more information."
BET_TIMER_THRESHOLD = 30

ROULETTE_TIMER_THRESHOLD = 60
ROULETTE_CHAMBERS = 6
ROULETTE_TIMER = 0

SAVESTATES = ["","","","","",""]

def null_function(user, message, message_with_case=""): pass

def return_name_and_contents(user, message, message_with_case=""): pass

def return_user_points(user, message, message_with_case=""):

	message_split = message.split(" ")
	if len(message_split) > 1:
		return "@" + user.name + " " + message_split[1] + " has " + str(USERS[message_split[1]].points) + " points!"
	elif len(message_split) == 1:
		return "@" + user.name + " You have " + str(user.points) + " points!"

def bet_points(user, message, message_with_case=""):

	if time.clock() - user.bet_timer > BET_TIMER_THRESHOLD:
		message_split = message.split(" ")
		try:
			wager = int(message_split[1])
		except:
			return "Wager must be numerical."
		if wager <= 0:
			return "Wager must be greater than zero."
		elif wager > user.points:
			return "You do not have enough points to wager."
		else:
			user.bet_timer = time.clock()
			if random.random() >= 0.5:
				user.points += wager
				pickle.dump(USERS, open("USERS.p", "wb"))
				return user.name + " gained " + str(wager) + " points!"
			else:
				user.points -= wager
				pickle.dump(USERS, open("USERS.p", "wb"))
				return user.name + " lost " + str(wager) + " points..."
	else:
		return "Try again later."
	
def return_user_info(user, message, message_with_case=""):
	
	return_message = user.name + ": "
	
	if user.subscriber: return_message += "subscriber, "
	return_message += LEVELS_INV[user.level] + ", "
	return_message += str(user.messages) + " valid input messages"
	
	return return_message
	
def roulette(user, message, message_with_case=""):

	global ROULETTE_CHAMBERS
	global ROULETTE_TIMER

	if time.clock() - ROULETTE_TIMER > ROULETTE_TIMER_THRESHOLD:
		if random.randrange(0,ROULETTE_CHAMBERS) == 0:
			sendmessage("☠ BANG! ☠")
			sendmessage("/timeout " + user.name + " 10")
			ROULETTE_CHAMBERS = 6
			ROULETTE_TIMER = time.clock()
		else:
			ROULETTE_CHAMBERS -= 1
			sendmessage("..." + str(ROULETTE_CHAMBERS) + " shots remain...")
	else:
		return "Not active right now. Try again later."

def return_user_level(user, message, message_with_case=""):

	message_split = message.split(" ")
	if len(message_split) > 1:
		return "@" + user.name + " " + message_split[1] + " is level: " + str(USERS[message_split[1]].level) + "(" + LEVELS_INV[USERS[message_split[1]].level] + ")"
	elif len(message_split) == 1:
		return "@" + user.name + " You are level: " + str(user.level) + "(" + LEVELS_INV[user.level] + ")"

def send_list(send_list):

	i = 0
	send_str = ""
	send_messages = [""]

	for thing in send_list:
		send_str += thing + ", "
		i +=1

		if i % 30 == 0:
			send_messages.append(send_str[0:-2])
			send_str = ""
		elif i < 30:
			send_messages[0] = send_str

	if len(send_messages) == 1:
		sendmessage(send_messages[0][0:-2])
	else:
		for i in range(0,len(send_messages)):
			if i != 0:
				sendmessage(send_messages[i])
		try:
			sendmessage(send_str[:-2])
		except:
			pass

def return_macro_list(user, message, message_with_case=""):

	macros = []
	for command in sorted(COMMANDS):
		if COMMANDS[command].flag == FLAGS["macro"]:
			macros.append(COMMANDS[command].name)
	if len(macros) > 0:
		send_list(macros)
	else:
		return "There are none!"

def return_meme_list(user, message, message_with_case=""):

	memes = []
	for command in sorted(COMMANDS):
		if COMMANDS[command].flag == FLAGS["meme"]:
			memes.append(COMMANDS[command].name)
	if len(memes) > 0:
		send_list(memes)
	else:
		return "There are none!"

def return_command_list(user, message, message_with_case=""):

	commands = []
	for command in sorted(COMMANDS):
		if COMMANDS[command].flag == FLAGS["default"] and COMMANDS[command].level_required < 4:
			commands.append(COMMANDS[command].name)
	if len(commands) > 0:
		send_list(commands)
	else:
		return "There are none!"

def return_cleverbot_chat(user, message, message_with_case=""):

	if user.subscriber:
		cleverbot_thread = Thread(target=chat, args=[user, message[5:]])
		cleverbot_thread.start()

def change_user_color(user, message, message_with_case=""):

	if user.subscriber:
		message = message.split(" ")
		user.color = COLORS[message[1]]

def save_state(user, message, message_with_case=""):

	global SAVESTATES

	message_split = message.split(" ")
	try:
		num = int(message_split[0][10:])
	except:
		try:
			num = int(message_split[1])
		except:
			return "Invalid number."

	result = savestate(num, user)

	if result.startswith("Saving"):
		SAVESTATES[num-1] = profanity.censor(message_with_case[10:].lstrip())
	return result

def load_state(user, message, message_with_case=""):

	return loadstate(int(message[10:].replace(" ","")), user)

def view_state(user, message, message_with_case=""):

	global SAVESTATES

	return "State " + SAVESTATES[int(message[10:].replace(" ",""))-1]

def log_message(user, message, message_with_case=""):
	
	global LOG
	
	message = message.split(" ")
	try:
		index = len(message[0]) + 1
		LOG.append([datetime.datetime.now(), user.name, profanity.censor(message_with_case[index:])])
		pickle.dump(LOG, open("LOG.p","wb"))
	except:
		return "Invalid message."
	
def view_log(user, message, message_with_case=""):

	global LOG
	
	log_date = LOG[-1][0]
	log_user = LOG[-1][1]
	log_message = LOG[-1][2]
			    
	return str(log_date) + " --> " + log_user + " : " + log_message

def set_level(user, message, message_with_case=""):

	message = message.split(" ")
	if USERS[message[1]].level < user.level and message[2] < user.level:
		USERS[message[1]].level = int(message[2])
	else:
		return "Not allowed"

def set_message(user, message, message_with_case=""):

	message_with_case = message_with_case[12:].upper()
	f = open("message.txt", "w")
	f.write(profanity.censor(message_with_case))
	f.close()

def add_command(user, message, message_with_case=""):

	message_split = message.split(" ")
	index = len(message_split[0]) + len(message_split[1]) + 1
	if message_split[1].startswith("!"):
		result = parse(message_split[2])
		if result[0] == False:
			return "Macro contents must parse successfully."
		else:
			COMMANDS[message_split[1]] = Command(message_split[1], message[index:], FLAGS["macro"])
			pickle.dump(COMMANDS, open("COMMANDS.p", "wb"))
	else:
		COMMANDS[message_split[1]] = Command(message_split[1], message_with_case[index:], FLAGS["meme"])
		pickle.dump(COMMANDS, open("COMMANDS.p", "wb"))

def add_secret_meme(user, message, message_with_case=""):

	message = message.split(" ")
	message_with_case = message_with_case.split(" ")
	COMMANDS[message[1]] = Command(message[1], "".join(message_with_case[2:]), FLAGS["hidden_meme"])
	pickle.dump(COMMANDS, open("COMMANDS.p", "wb"))

def return_secret_memes(user, message, message_with_case=""):

	secrets = []
	for secret in sorted(COMMANDS):
		if COMMANDS[secret].flag == FLAGS["hidden_meme"]:
			secrets.append(COMMANDS[secret].name)
	if len(secrets) > 0:
		send_list(secrets)
	else:
		return "There are none!"

def remove_command(user, message, message_with_case=""):

	message = message.split(" ")
	if COMMANDS[message[1]].flag != FLAGS["default"]:
		del COMMANDS[message[1]]
		pickle.dump(COMMANDS, open("COMMANDS.p", "wb"))
	else:
		return "Default commands cannot be removed."

def execute_python(user, message, message_with_case):

	exec(message_with_case[6:])

def delete_macros(user, message, message_with_case=""):
	
	macros = []
	for macro in sorted(COMMANDS):
		if COMMANDS[macro].flag == FLAGS["macro"]:
			del COMMANDS[macro]
	pickle.dump(COMMANDS, open("COMMANDS.p","wb"))
	
def delete_memes(user, message, message_with_case=""):
	
	memes = []
	for meme in sorted(COMMANDS):
		if COMMANDS[meme].flag == FLAGS["meme"]:
			del COMMANDS[meme]
	pickle.dump(COMMANDS, open("COMMANDS.p","wb"))
	
def delete_secret_memes(user, message, message_with_case=""):
	
	memes = []
	for meme in sorted(COMMANDS):
		if COMMANDS[meme].flag == FLAGS["hidden_meme"]:
			del COMMANDS[meme]
	pickle.dump(COMMANDS, open("COMMANDS.p","wb"))
	
def set_team(user, message, message_with_case=""):
	
	message = message.split(" ")
	if message[2] == "0" or message[2] == "1":
		USERS[message[1]].team = int(message[2])
		pickle.dump(USERS, open("USERS.p","wb"))
	else:
		return "Invalid number."

def set_all_team(user, message, message_with_case=""):
	
	message = message.split(" ")
	team = int(message[1])
	for viewer in USERS:
		viewer.team = team
	pickle.dump(USERS, open("USERS.p","wb"))
	
class Command:

	def __init__(self, name, contents, flag, function=None, level_required=0):

		self.name = name
		self.contents = contents
		self.level_required = level_required
		self.flag = flag
		self.function = function

	def evaluate(self, user, message, message_with_case=""):

		if user.level >= self.level_required:
			if self.function == None:
				return self.contents
			elif self.function == return_name_and_contents:
				if COMMANDS[message.split(" ")[1]].flag != FLAGS["default"]:
					return COMMANDS[message.split(" ")[1]].name + " = " + COMMANDS[message.split(" ")[1]].contents
			else:
				result = self.function(user, message, message_with_case)
				return result
		else:
			return "Permission denied."

# Load the log from the file
try: LOG = pickle.load(open("LOG.p","rb"))
except:
	LOG = [[datetime.datetime.now(), "Log Created"]]
	pickle.dump(LOG, open("LOG.p","wb"))

# Load the command list from the file
try: COMMANDS = pickle.load(open("COMMANDS.p","rb"))
except:
	COMMANDS = {
		"!points": Command("!points", "Usage: !points", FLAGS["default"], return_user_points),
		"!bet": Command("!bet", "Usage: !bet <wager>", FLAGS["default"], bet_points),
		"!roulette": Command("!roulette", "Usage: !roulette", FLAGS["default"], roulette),
		"!me": Command("!me", "Usage: !me", FLAGS["default"], return_user_info),
		"!permissions": Command("!permissions", LEVEL_INFO, FLAGS["default"]),
		"!tutorial": Command("!tutorial", TUTORIAL_URL, FLAGS["default"]),
		"!botinfo": Command("!botinfo", BOT_INFO, FLAGS["default"]),
		"!level": Command("!level", "Usage: !level <username>", FLAGS["default"], return_user_level),
		"!show": Command("!show", "Usage: !show <command/macro/meme name>", FLAGS["default"], return_name_and_contents),
		"!macros": Command("!macros", "Usage: !macros", FLAGS["default"], return_macro_list),
		"!memes": Command("!memes", "Usage: !memes", FLAGS["default"], return_meme_list),
		"!commands": Command("!commands", "Usage: !commands", FLAGS["default"], return_command_list),
		"!chat": Command("!chat", "Subscriber Command Usage: !chat <your message here>", FLAGS["default"], return_cleverbot_chat),
		"!color": Command("!color", "Subscriber Command Usage: !color <red/blue/green/yellow/cyan/white>", FLAGS["default"], change_user_color),
		"!savestate": Command("!savestate", "Superviewer Usage: !savestate <1-6> <optional message>", FLAGS["default"], save_state, 2),
		"!loadstate": Command("!loadstate", "Superviewer Usage: !loadstate <1-6>", FLAGS["default"], load_state, 2),
		"!viewstate": Command("!viewstate", "Superviewer Usage: !viewstate <1-6>", FLAGS["default"], view_state, 2),
		"!log": Command("!log", "Superviewer Usage: !log <log message>, FLAGS["default"], log_message, 2),
		"!viewlog": Command("!viewlog", "Usage: !viewlog", FLAGS["default"], view_log),
		"!setlevel": Command("!setlevel", "Mod Command Usage: !setlevel <username> <0/1/2>", FLAGS["default"], set_level, 3),
		"!setmessage": Command("!setmessage", "Mod Command Usage: !setmessage <message>", FLAGS["default"], set_message, 3),
		"!add": Command("!add", "Mod Command Usage: !add <macro/meme name> <macro/meme contents>", FLAGS["default"], add_command, 3),
		"!addsecret": Command("!addsecret", "Mod Command Usage: !addsecret <secrete meme name> <secret meme contents>", FLAGS["default"], add_secret_meme, 3),
		"!secrets": Command("!secrets", "Mod Command Usage: !secrets", FLAGS["default"], return_secret_memes, 3),
		"!remove": Command("!remove", "Mod Command Usage: !remove <macro/meme name>", FLAGS["default"], remove_command, 3),
		"!exec": Command("!exec", "Admin Command Usage: !exec <Valid Python code>", FLAGS["default"], execute_python, 4),
		"!deletememes": Command("!deletememes", "Admin Command Usage: !deletememes", FLAGS["default"], delete_memes, 4),
		"!deletesecrets": Command("!deletesecrets", "Admin Command Usage: !deletesecrets", FLAGS["default"], delete_secret_memes, 4),
		"!deletemacros": Command("!deletemacros", "Admin Command Usage: !deletemacros", FLAGS["default"], delete_macros, 4),
		"!setteam": Command("!setteam", "Admin Command Usage: !setteam <0/1>", FLAGS["default"], set_team, 4),
		"!setallteam": Command("!setallteam", "Admin Command Usage: !setallteam <0/1>", FLAGS["default"], set_all_team, 4),
	}
	pickle.dump(COMMANDS, open("COMMANDS.p","wb"))
