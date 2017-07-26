import Commands
import re
from re import match

FLAGS = {
	"default": 0,
	"macro": 1,
	"meme": 2,
	"hidden_meme": 3
}
VALID_INPUTS = [
	"left", "right", "up", "down",
	"a", "b", "l", "r", "z", "x", "y",
	"start",
	"cleft", "cright", "cup", "cdown",
	"dleft", "dright", "dup", "ddown",
	"#", "."
]

DURATION_DEFAULT = 200
DURATION_MAX = 30000

class Input:

	def __init__(self):

		self.name = ""
		self.hold = False
		self.release = False
		self.percent = 100
		self.duration = DURATION_DEFAULT
		self.duration_type = "ms"
		self.length = 0
		self.error = ""

# Returns False if recursion error, string otherwise
def populate_macros(message):

	if message == False:
		return False

	# Find the longest length macro that matches
	longest_length = 0

	for command in Commands.COMMANDS:

		if Commands.COMMANDS[command].flag != FLAGS["macro"]: continue

		regex = r'' + Commands.COMMANDS[command].name + r''

		if message == False:
			return False

		m = re.search(regex, message)

		if m != None:
			if len(Commands.COMMANDS[command].name) > longest_length:
				longest_command = Commands.COMMANDS[command].name
				longest_length = len(Commands.COMMANDS[command].name)
				longest_match = m

	if longest_length > 0:

		# Insert the macro contents into the message
		message = message[0:longest_match.start()] + Commands.COMMANDS[longest_command].contents + message[longest_match.end():]
		# Try to use recursion. If we max it out, the message is unusable
		try:
			message = populate_macros(message)
		except:
			return False

	return message

# Returns Input object
def get_input(message):

	# Create a default input instance
	current_input = Input()

	# Check for input modifiers
	regex = r'[_-]'
	m = match(regex, message)

	# If theres a match, trim the message
	if m != None:
		c = message[m.start():m.end()]
		message = message[m.end():]

		if c == "_":
			current_input.hold = True
			current_input.length += 1
		elif c == "-":
			current_input.release = True
			current_input.length += 1

	# Try to match one input, prioritizing the longest match
	max = 0
	valid_input = ""

	for button in VALID_INPUTS:
		if button == ".":
			regex = r'' + "\." + r''
		else:
			regex = r'' + button + r''

		m = match(regex, message)

		if m != None:
			length = m.end() - m.start()

			if length > max:
				max = length
				current_input.name = message[m.start():m.end()]

	# If not a valid input, break parsing
	if current_input.name == "":
		current_input.error = "ERR_INVALID_INPUT"

		return current_input
	else:
		current_input.length += max

	# Trim the input from the message
	message = message[max:]

	# Try to match a percent
	regex = r'\d+%'
	m = match(regex, message)

	if m != None:
		current_input.percent = int(message[m.start():m.end()-1])
		message = message[m.end():]
		current_input.length += len(str(current_input.percent)) + 1

		if current_input.percent > 100:
			current_input.error = "ERR_INVALID_PERCENTAGE"
			return current_input

	# Try to match a duration
	regex = r'\d+'
	m = match(regex, message)

	if m != None:
		current_input.duration = int(message[m.start():m.end()])
		message = message[m.end():]
		current_input.length += len(str(current_input.duration))

		# Determine the type of duration
		regex = r'(s|ms)'
		m = match(regex, message)

		if m != None:
			current_input.duration_type = message[m.start():m.end()]
			message = message[m.end():]

			if current_input.duration_type == "s":
				current_input.duration *= 1000
				current_input.length += 1
			else:
				current_input.length += 2
		else:
			current_input.error = "ERR_DURATION_TYPE_UNSPECIFIED"
			return current_input

	return current_input

# Returns list containing: [Valid, input_sequence]
# Or: [Invalid, input that it failed on]
def parse(message):

	message = populate_macros(message)
	if message == False:
		return_input = Input()
		return_input.error = "ERR_POPULATING_MACROS"
		return [False, return_input]
	message = message.replace(" ", "")
	input_subsequence = []
	input_sequence = []
	duration_counter = 0

	while len(message) > 0:

		input_subsequence = []
		subduration_max = 0
		current_input = get_input(message)

		if current_input.error != "":
			return [False, current_input]

		message = message[current_input.length:]
		input_subsequence.append(current_input)

		if current_input.duration > subduration_max:
			subduration_max = current_input.duration

		if len(message) > 0:

			while message[0] == "+":

				if len(message) > 0:
					message = message[1:]
				else:
					break

				current_input = get_input(message)

				if current_input.error != "":
					return [False, current_input]

				message = message[current_input.length:]
				input_subsequence.append(current_input)

				if current_input.duration > subduration_max:
					subduration_max = current_input.duration

				if len(message) == 0:
					break

		duration_counter += subduration_max

		if duration_counter > DURATION_MAX:
			return [False, current_input]

		input_sequence.append(input_subsequence)

	return [True, input_sequence]
