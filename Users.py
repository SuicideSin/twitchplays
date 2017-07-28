import pickle
import datetime

from colorama import Fore

LEVELS = {"viewer": 0, "whitelist": 1, "superviewer": 2, "mod": 3, "admin": 4}
LEVELS_INV = {0: "viewer", 1: "whitelist", 2: "superviewer", 3: "mod", 4: "admin"}

COLORS = {
	"red": Fore.RED,
	"green": Fore.GREEN,
	"blue": Fore.BLUE,
	"yellow": Fore.YELLOW,
	"cyan": Fore.CYAN,
	"white": Fore.WHITE
}


def add_user(name):

	USERS[name] = User(name)
	pickle.dump(USERS, open("USERS.p","wb"))

class User:

	def __init__(self, name, level=0, messages=0, points=100, team=0, inventory = [], subscriber=False):

		self.name = name
		self.level = level
		self.messages = messages
		self.points = points
		self.team = team
		self.color = Fore.CYAN
		self.inventory = inventory
		self.subscriber = subscriber
		self.bet_timer = 0
		self.join_date = datetime.datetime.now()

# Load the user list from the file
try: USERS = pickle.load(open("USERS.p","rb"))
except:
	USERS = {
		"twitchplays_everything": User("twitchplays_everything", 4, 100, 100, 0, [""], True),
		"mrmacrobot": User("mrmacrobot", 4, 100, 100, 0, [""], True)
	}
	pickle.dump(USERS, open("USERS.p","wb"))
