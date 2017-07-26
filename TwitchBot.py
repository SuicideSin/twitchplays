import string
import os
import socket
import time

from Settings import HOST, PORT, PASS, IDENT, CHANNEL
from colorama import init as ColoramaInit
from colorama import Fore, Back, Style

timeSendLast = 0.1
durationLastChecked = 0
messagesSent = 0

def send_message(s, message, color="WHITE"):

	global timeSendLast
	global messagesSent

	messageTemp = "PRIVMSG #" + CHANNEL + " :" + message + "\r\n"

	# The message rate is in messages / duration since last message sent
	messageRate = 1 / (time.clock() - timeSendLast)
	while messageRate > 1: messageRate = 1 / (time.clock() - timeSendLast)

	timeSendLast = time.clock()
	s.send(messageTemp.encode('utf-8'))
	messagesSent += 1

	message = messageTemp[messageTemp.find(":")+1:].strip("\r")
	message = message.strip("\n")

	if not(message.startswith("/w")):
		if color == "GREEN": print(Fore.MAGENTA + IDENT + ": " + Fore.GREEN + message)
		else:
			try: print(Fore.MAGENTA + IDENT + ": " + Fore.WHITE + message)
			except: pass

def join_room(s):
	readbuffer = ""
	Loading = True
	while Loading:
		readbuffer = readbuffer + s.recv(1024).decode()
		temp = readbuffer.split('\n')
		readbuffer = temp.pop()

		for line in temp:
			Loading = loading_complete(line)

		print(readbuffer)

	os.system("cls")
	send_message(s, "Successfully joined chat")

def loading_complete(line):

	if("ROOMSTATE" in line):
		return False
	else:
		return True

def open_socket():

	s = socket.socket()
	s.connect((HOST, PORT))

	message = "PASS " + PASS + "\r\n"
	s.send(message.encode('utf-8'))

	message = "NICK " + IDENT + "\r\n"
	s.send(message.encode('utf-8'))

	message = "CAP REQ :twitch.tv/membership" + "\r\n"
	s.send(message.encode("utf-8"))

	response = ""
	while "ACK" not in response:
		response = s.recv(1024).decode("utf-8")
		#print(response)

	message = "CAP REQ :twitch.tv/commands" + "\r\n"
	s.send(message.encode("utf-8"))

	response = ""
	while "ACK" not in response:
		response = s.recv(1024).decode("utf-8")
		#print(response)

	message = "CAP REQ :twitch.tv/tags" + "\r\n"
	s.send(message.encode("utf-8"))

	response = ""
	while "ACK" not in response:
		response = s.recv(1024).decode("utf-8")
		#print(response)

	message = "JOIN #" + CHANNEL + "\r\n"
	s.send(message.encode('utf-8'))

	return s

def get_user(line):

	index = line.find("display-name=")
	i = 0
	c = line[index + 13 + i]
	user = ""
	while c != ";":
		user += c
		i += 1
		try:
			c = line[index + 13 + i]
		except:
			return ""

	if "(" in user or ")" in user:
		user = user[user.find("(")+1:user.find(")")]
	return user.lower()

def get_message(line):

	index = line.find("PRIVMSG")
	i = 0
	c = line[index + 6 + i]
	message = ""
	while c != ":":
		i += 1
		try:
			c = line[index + 13 + i]
		except:
			return ""
	message = line[index + 13 + i + 1:]

	return message

class TwitchBot:

	def __init__(self):

		self.message = ""
		self.user = ""
		self.EVENT_MESSAGE_RECEIVED = False
		self.COMMAND_PARSE_SUCCESSFUL = False
		self.messageBuffer = []

	def run(self):

		global s, readbuffer

		while True:
			try:
				readbuffer = readbuffer + s.recv(1024).decode("utf-8")
				temp = readbuffer.split('\n')
				readbuffer = temp.pop()
			except:
				readbuffer = ""
				temp = readbuffer.split('/n')
				readbuffer = temp.pop()



			for line in temp:
				if "PING" in line:
					strSend = "PONG :tmi.twitch.tv\r\n".encode('utf-8')
					s.send(strSend)
					break
				bitnum = 0
				if "bits=" in line:
					index = line.find("bits=") + 5
					c = line[index]
					bitStr = ""
					while c != ";":
						bitStr += c
						index += 1
						c = line[index]
					try:
						bitnum = int(bitStr)
					except:
						print("ERROR CONVERTING BITS TO NUM?")

				index = line.find("subscriber=") + 11
				c = line[index]
				subscriber = False
				if c == "1":
					subscriber = True

				index = line.find("mod=") + 4
				c = line[index]
				mod = False
				if c == "1":
					mod = True

				self.user = get_user(line)
				self.message = get_message(line)

				userList = list(self.user)
				index = 0
				for c in userList:
					if not c.isalnum() and c != "_" and c != "-":
						userList[index] = ""
					index += 1
				self.user = "".join(userList)

				# Let the main code know there is a message
				if not self.user == "mrmacrobot" and not self.user.startswith("tmi.twitch.tv") and not self.user.startswith("jtv MODE") and not self.user.startswith("streamelements") and self.user != "":
					self.messageBuffer.append([self.user,self.message,bitnum,subscriber,mod])
				#print(line)

def sendmessage(message="",color="WHITE"):

    global s
    send_message(s,message,color)

def sendwhisper(user, message):

    global s
    try:
        send_message(s, "/w " + user + " " + message)
    except:
        print(Fore.RED + "Error sending whisper")

s = open_socket()
join_room(s)
