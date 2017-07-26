import time
import random
import pickle

from Users import *
from Commands import *
from Parser import *
from Controller import *
from TwitchBot import *
from threading import Thread
from colorama import Fore, Back, Style


# Timer Variables
vjoy_time = 0
vjoy_time_last = 0
time_current = time.clock()
time_info_elapsed = 0
time_points_elapsed = 0
time_info_last = 0
time_points_last = 0

# Defaults
WHITELIST_THRESHHOLD = 20
VJOY_REINIT_TIME = 240
INFO_TIME = 1000
POINTS_TIME = 300
MAX_THREAD_COUNT = 50

CURRENT_ACTIVE_USERS = []

def vjoy_init():

    global vjoy_time, vjoy_time_last

    while True:
        if vjoy_time > VJOY_REINIT_TIME:
            Vjoy.Initialize()
            vjoy_time = 0
            vjoy_time_last = time.clock()
            vjoy_time = time.clock() - vjoy_time_last

# Run a separate thread to make sure vjoy stays running
vjoy_thread = Thread(target=vjoy_init)
vjoy_thread.start()

# Run a separate thread for the chatbot so we can do other things
TwitchBot = TwitchBot()
bot_thread = Thread(target=TwitchBot.run)
bot_thread.start()

def process(user, message, bitnum, subscriber, mod):

    global Controllers

    if mod and user.level < LEVELS["mod"]:
        user.level = LEVELS["mod"]
        pickle.dump(USERS, open("USERS.p","wb"))

    # All processing is case insensitive
    message_with_case = message[:]
    message = message.lower()

    if Controllers[0].thread_count >= MAX_THREAD_COUNT:
        sendmessage("Reached maximum thread count. Please wait for inputs to finish executing.")
        print(Fore.RED + "Reached maximum thread count. Please wait for inputs to finish executing.")
        time.sleep(1)
        while Controllers[0].thread_count >= MAX_THREAD_COUNT: pass

    # Attempt to parse the message as an input sequence
    parse_result = parse(message)
    valid = parse_result[0]
    content = parse_result[1]

    # Check if the message is a valid input sequence
    if not valid:

        # Ignore invalid input error (since regular messages will always get that error)
        if content.error != "ERR_INVALID_INPUT":

            # Whisper and print the error message
            error_string = content.error + " occurred at " + "'" + content.name + "'"
            try:
                sendwhisper(user.name, error_string)
            except:
                print(Fore.RED + "Error printing user")
            try:
                print(user.color + user.name + ": ", end="")
            except:
                print(Fore.CYAN + "generic: ", end="")
            print(Fore.WHITE + message)
            print(Fore.RED + error_string)
        else:
            # Print the message
            try:
                print(user.color + user.name + ": ", end="")
            except:
                print(Fore.CYAN + "generic: ", end="")
            print(Fore.WHITE + message)
    else:
        # Execute the input sequence
        e = Thread(target=Controllers[user.team].execute_input_array, args=[content])
        e.start()

        try:
            print(user.color + user.name + ": ", end="")
        except:
            print(user.color + "generic: ", end="")
        print(Fore.GREEN + message)
        valid = True

    # Process the message for commands, but not macros since they're processed in parse()
    longest = 0
    command_choice = ""
    for command in COMMANDS:
        if message.startswith(command) and COMMANDS[command].flag != FLAGS["macro"]:
            if len(command) > longest:
                command_choice = command
                longest = len(command)

    if command_choice != "":
        try:
            result = COMMANDS[command_choice].evaluate(user, message, message_with_case)
            if result != None:
                sendmessage(result)
        except Exception as e:
            sendmessage(COMMANDS[command_choice].contents)
            print(Fore.RED + "Error evaluating command: ",end="")
            print(e)

    return valid

PROGRAM_RUNNING = True
while PROGRAM_RUNNING:

    global CURRENT_ACTIVE_USERS

    # TIMED MESSAGES
    time_current = time.clock()
    time_info_elapsed = time_current - time_info_last
    time_points_elapsed = time_current - time_points_last

    if time_info_elapsed > INFO_TIME:
        sendmessage(COMMANDS["!botinfo"].evaluate(USERS["mrmacrobot"], "", ""))
        time_info_elapsed = 0
        time_info_last = time_current

    if time_points_elapsed > POINTS_TIME:
        for user in CURRENT_ACTIVE_USERS:
            user.points += 50
        CURRENT_ACTIVE_USERS = []
        time_points_elapsed = 0
        time_points_last = time_current


    # While there are messages to be processed
    while len(TwitchBot.messageBuffer) > 0:

        # Grab the message attributes
        username = TwitchBot.messageBuffer[0][0].strip("\r")
        username = username.strip("\n")
        message = TwitchBot.messageBuffer[0][1].strip("\r")
        message = message.strip("\n")
        bitnum = TwitchBot.messageBuffer[0][2]
        subscriber = TwitchBot.messageBuffer[0][3]
        mod = TwitchBot.messageBuffer[0][4]

        # Attempt to grab the user object
        try:
            user = USERS[username]
        except:
            USERS[username] = User(username)
            pickle.dump(USERS, open("USERS.p","wb"))
            user = USERS[username]
            try:
                print(Fore.MAGENTA + user + " was added to the user list!")
            except:
                print(Fore.MAGENTA + "Error printing username")

        if user not in CURRENT_ACTIVE_USERS: CURRENT_ACTIVE_USERS.append(user)

        # Process the message
        valid = process(user, message, bitnum, subscriber, mod)

        # Increment their message counter if it was a valid message
        if valid: user.messages += 1

        # Promote if the required number of valid messages is met
        if user.messages == WHITELIST_THRESHHOLD:
            if user.level == 0:
                user.level = LEVELS['superviewer']
                pickle.dump(USERS, open("USERS.p","wb"))
                sendmessage("@" + user.name + " was promoted to superviewer! You can now !savestate 4-6 and !loadstate 1-6.")

        # Delete the message we've processed
        del TwitchBot.messageBuffer[0]
