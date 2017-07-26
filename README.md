# twitchplays

Commands.py:

  Contains the command and macro database. New commands are created with Command() and added to COMMANDS, and are linked to functions defined in Commands.py
  
Controller.py:

  Controller() object takes in a sequence of inputs in a multi-nested array. The innermost layer is one input. The next is a sequence of   simultaneous inputs. The next is a sequence of a sequence of simultaneous inputs.
  
Parser.py:

  Parses strings of ASCII into the input sequence syntax. Example: "left50%3s+b _a start30ms #100ms -a !macro_name b b"
  
TwitchBot.py:

  Use TwitchBot() to create a new TwitchBot. A new Settings.py containing the private information will need to be created.
  
Users.py:

  Use User() to create a new user and append it to the USERS dictionary.
