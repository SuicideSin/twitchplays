import time
import Vjoy

from Vjoy import joyState, SetButton, SetPOV, UpdateJoyState
from threading import Thread
from copy import copy

from Users import User, LEVELS

INPUTS = {
    "left":         0,
    "right":        1,
    "up":           2,
    "down":         3,
    "a":            4,
    "b":            5,
    "l":            6,
    "r":            7,
    "z":            8,
    "start":        9,
    "cleft":        10,
    "cright":       11,
    "cup":          12,
    "cdown":        13,
    "dleft":        14,
    "dright":       15,
    "dup":          16,
    "ddown":        17,
    "SAVESTATE1":   18,
    "SAVESTATE2":   19,
    "SAVESTATE3":   20,
    "SAVESTATE4":   21,
    "SAVESTATE5":   22,
    "SAVESTATE6":   23,
    "LOADSTATE1":   24,
    "LOADSTATE2":   25,
    "LOADSTATE3":   26,
    "LOADSTATE4":   27,
    "LOADSTATE5":   28,
    "LOADSTATE6":   29,
    "x":            30,
    "y":            31
}

def savestate(num, user):

	global Controllers

	if user.level < 3 and num <= 3 and num > 0:
		return "Access denied"
	elif num > 0 and num <= 6:
		Controllers[0].execute_input("SAVESTATE" + str(num), 200)
		return "Saving state " + str(num)
	else: return "Invalid number."

def loadstate(num, user):

	global Controllers

	if num > 0 and num <= 6:
		Controllers[0].execute_input("LOADSTATE" + str(num), 200)
		return "Loading state " + str(num)
	else: return "Invalid number."


class Controller:

    def __init__(self, id=0):

        self.id = id
        self.buttons ={
        "left":         False,
        "right":        False,
        "up":           False,
        "down":         False,
        "a":            False,
        "b":            False,
        "l":            False,
        "r":            False,
        "z":            False,
        "start":        False,
        "cleft":        False,
        "cright":       False,
        "cup":          False,
        "cdown":        False,
        "dleft":        False,
        "dright":       False,
        "dup":          False,
        "ddown":        False,
        "SAVESTATE1":   False,
        "SAVESTATE2":   False,
        "SAVESTATE3":   False,
        "SAVESTATE4":   False,
        "SAVESTATE5":   False,
        "SAVESTATE6":   False,
        "LOADSTATE1":   False,
        "LOADSTATE2":   False,
        "LOADSTATE3":   False,
        "LOADSTATE4":   False,
        "LOADSTATE5":   False,
        "LOADSTATE6":   False,
        "x":            False,
        "y":            False,
        "#":            False,
        ".":            False
        }
        self.thread_count = 0

    def execute_input_array(self, input_array):

        self.thread_count += 1

        # The list of buttons this particular instance cares about
        instance_buttons = []

        # For each string of simultaneous buttons
        for simultaneous_buttons in input_array:

            # Determine the delay time
            max_delay = 0
            for button in simultaneous_buttons:

                if button.duration > max_delay: max_delay = button.duration

            # Press each button in a separate thread, as they are simultaneous
            for button in simultaneous_buttons:

                b = Thread(target=self.execute_input, args=[button.name, button.duration, button.percent, button.hold, button.release])
                b.start()

                instance_buttons.append(button.name)

            # Wait the maximum time
            time.sleep(0.01 + int(max_delay)/1000)

        # Release any buttons this instance started holding
        for button in instance_buttons:
            if self.buttons[button]:

                if button == "left" or button == "right" or button == "up" or button == "down":
                    self.release_analog(button)
                elif button != "." and button != "#":
                    self.release_digital(button)

        self.thread_count -= 1

    def hold_digital_duration(self, val="", duration=0):

        global Vjoy
        global joyState

        SetButton(joyState[self.id], INPUTS[val], Vjoy.BUTTON_DOWN)
        UpdateJoyState(self.id, joyState[self.id])

        time.sleep(duration/1000)

        SetButton(joyState[self.id], INPUTS[val], Vjoy.BUTTON_UP)
        UpdateJoyState(self.id, joyState[self.id])


    def hold_digital_indefinite(self, val=""):

        global Vjoy
        global joyState

        SetButton(joyState[self.id], INPUTS[val], Vjoy.BUTTON_DOWN)
        UpdateJoyState(self.id, joyState[self.id])

        self.buttons[val] = True

    def release_digital(self, val=""):

        global Vjoy
        global joyState

        SetButton(joyState[self.id], INPUTS[val], Vjoy.BUTTON_UP)
        UpdateJoyState(self.id, joyState[self.id])
        self.buttons[val] = False

    def hold_analog_duration(self, val="", duration=0, percent=100):

        global Vjoy
        global joyState

        if val == "left": joyState[self.id].XAxis = int(Vjoy.AXIS_MIN * percent/100)
        if val == "right": joyState[self.id].XAxis = int(Vjoy.AXIS_MAX * percent/100)
        if val == "up": joyState[self.id].YAxis = int(Vjoy.AXIS_MAX * percent/100)
        if val == "down": joyState[self.id].YAxis = int(Vjoy.AXIS_MIN * percent/100)
        UpdateJoyState(self.id, joyState[self.id])
        self.buttons[val] = True

        time.sleep(duration/1000)

        if val == "left": joyState[self.id].XAxis = Vjoy.AXIS_NIL
        if val == "right": joyState[self.id].XAxis = Vjoy.AXIS_NIL
        if val == "up": joyState[self.id].YAxis = Vjoy.AXIS_NIL
        if val == "down": joyState[self.id].YAxis = Vjoy.AXIS_NIL
        UpdateJoyState(self.id, joyState[self.id])
        self.buttons[val] = False

    def hold_analog_indefinite(self, val="", percent=100):

        global Vjoy
        global joyState

        if val == "left": joyState[self.id].XAxis = int(Vjoy.AXIS_MIN * percent/100)
        if val == "right": joyState[self.id].XAxis = int(Vjoy.AXIS_MAX * percent/100)
        if val == "up": joyState[self.id].YAxis = int(Vjoy.AXIS_MAX * percent/100)
        if val == "down": joyState[self.id].YAxis = int(Vjoy.AXIS_MIN * percent/100)
        UpdateJoyState(self.id, joyState[self.id])
        self.buttons[val] = True

    def release_analog(self, val=""):

        global Vjoy
        global joyState

        if val == "left": joyState[self.id].XAxis = Vjoy.AXIS_NIL
        if val == "right": joyState[self.id].XAxis = Vjoy.AXIS_NIL
        if val == "up": joyState[self.id].YAxis = Vjoy.AXIS_NIL
        if val == "down": joyState[self.id].YAxis = Vjoy.AXIS_NIL
        UpdateJoyState(self.id, joyState[self.id])
        self.buttons[val] = False

    def execute_input(self, val="", duration=0, percent=100, hold=False, release=False):

        if self.buttons["b"] and self.buttons["x"] and self.buttons["start"]:
            self.release_digital("start")


        if val == "left" or val == "right" or val == "up" or val == "down":
            if hold:
                self.hold_analog_indefinite(val, percent)
            elif release:
                self.release_analog(val)
            else:
                self.hold_analog_duration(val, duration, percent)
        elif val != "." and val != "#" and not (val.startswith("SAVE") or val.startswith("LOAD")):
            if hold:
                self.hold_digital_indefinite(val)
            elif release:
                self.release_digital(val)
            else:
                self.hold_digital_duration(val, duration)
        else:
            if val == ".": time.sleep(0.2)
            elif val == "#": time.sleep(duration/1000)
            else:
                self.hold_digital_duration(val, duration)

Controllers = [Controller(0), Controller(1)]
