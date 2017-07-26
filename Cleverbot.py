from cleverwrap import CleverWrap
from Settings import CLEVERBOT_API_KEY
from TwitchBot import sendmessage, sendwhisper

CW = CleverWrap(CLEVERBOT_API_KEY)

def chat(user, message):

	global CW

	try:
		sendmessage("@" + user.name + " " + CW.say(message))
	except:
		sendmessage("Error gathering response. Trying again...")
		try:
			CW = CleverWrap(CLEVERBOT_API_KEY)
			sendmessage("@" + user.name + " " + CW.say(message))
		except:
			sendmessage("Unable to get a response.")
