#!/usr/bin/env python
# coding: utf-8

# In[ ]:


class Board:

    def __init__(self,size = 9):
        self.size = size
        self.fence_spots = self.size - 1
        self.total_board_size = size + self.fence_spots
        self.player1 = "placeholder"
        self.player2 = "placeholder2"

        self.columns = [chr(i) for i in range(ord('A'),ord('Z')+1)][0:self.size]
        self.locations = []
        for each in self.columns:
            for i in range(1,self.size + 1):
                self.locations.append(f'{each}{i}')
        self.display = self.create_display(size) # write to var for use in other functions
        
    def create_display(self,size):
        display = []
        display.append(list(' '*11+'     '.join(self.columns)))
        for i in range(1,self.size+1):
            display.append(list(f'''        '''+'—————'.join("|"*(self.size+1))))
            display.append(list(f'''     {i}  '''+'     '.join("|"*(self.size+1))+f''' {i}'''))
        display.append(list(f'''        '''+'—————'.join("|"*(self.size+1))))
        display.append(list(' '*11+'     '.join(self.columns)))          
        return display

    def show_display(self):
        for i in range(0,self.size*2 + 2):
            print("".join(self.display[i]))
     
    def update_display(self):
        # Clear out player's old location on the display
        p1srow = self.player1.starting_location[1]
        p1scol = ord(self.player1.starting_location[0])-64
        p2srow = self.player2.starting_location[1]
        p2scol =  ord(self.player2.starting_location[0])-64
        self.display[int(p1srow)*2][5+6*(p1scol)]= " "
        self.display[int(p2srow)*2][5+6*(p2scol)]= " "
        
        # Set player's current location on display to their marker
        p1row = self.player1.location[1]
        p1col = ord(self.player1.location[0])-64
        p2row = self.player2.location[1]
        p2col =  ord(self.player2.location[0])-64
        self.display[int(p1row)*2][5+6*(p1col)]= self.player1.marker
        self.display[int(p2row)*2][5+6*(p2col)]= self.player2.marker

        # label player's current location as starting location (for future moves)
        self.player1.starting_location = self.player1.location
        self.player2.starting_location = self.player2.location

class Player:

    def __init__(self, name, marker = "A", location = "A2", fences = 10, turn = False):
        self.name = name
        self.marker = '\u25A1'
        self.fences = fences
        self.fences_remaining = fences
        self.location = location
        self.starting_location = location
        self.turn = turn
        self.board = ""

    def __str__(self):
        return f'''{self.name}, location {self.location}, {self.fences_remaining} fences remaining{", their turn" if self.turn else ""}.'''

    def move_piece(self):
        # display board
        self.board.show_display()
        
        self.move_options = {"left":"", "right":"", "up":"", "down":""}
        
        # Store starting location (to remove marker from display after they move)
        self.starting_location = self.location
        
        # Can you move left?
        if not self.location[0] == "A":
            ##### Jordan must check if fence blocked before the next line
            self.move_options.update({"left":chr(ord(self.location[0]) - 1)+self.location[1]})
        else:
            self.move_options.update({"left":None})
        # Can you move right?
        if not self.location[0] == self.board.columns[-1]:
            ##### Jordan must check if fence blocked before the next line            
            self.move_options.update({"right":chr(ord(self.location[0]) + 1)+self.location[1]})
        else:
            self.move_options.update({"right":None})
        # Can you move up?
        if not self.location[1] == "1":
            ##### Jordan must check if fence blocked before the next line
            self.move_options.update({"up":self.location[0]+chr(ord(self.location[1]) - 1)})
        else:
            self.move_options.update({"up":None})
        # Can you move down?
        if not self.location[1] == str(len(self.board.columns)):
            ##### Jordan must check if fence blocked before the next line
            self.move_options.update({"down":self.location[0]+chr(ord(self.location[1]) + 1)})
        else:
            self.move_options.update({"down":None})

        # keep asking until it's not the player's turn
        moved = False
        while True:
            move_choice = input(f'''\nWhere would you like to move? \n 
            {'> Left to ' + f'{self.move_options["left"]} (enter "left", "l", or "4")' if self.move_options["left"] is not None else "(can't move left)"}
            {'> Right to ' + f'{self.move_options["right"]} (enter "right", "r", or "6")' if self.move_options["right"] is not None else "(can't move right)"}
            {'> Up to ' + f'{self.move_options["up"]} (enter "up", "u", or "8")' if self.move_options["up"] is not None else "(can't move up)"}
            {'> Down to ' + f'{self.move_options["down"]} (enter "down", "d", or "2")' if self.move_options["down"] is not None else "(can't move down)"}
            {'> Go back (enter "back" or "b")'}      ''')
    
            # Make the move
                # ToDo: Check if lands on other player's location before return. implement the logic for them to jump over
            if move_choice.lower() in ["back", "b"]:
                return False
            elif move_choice.lower() in ["left", "l", "4"] and self.move_options["left"] is not None:
                print("moving left")
                self.location = f'{self.move_options["left"]}'
                return True
            elif move_choice.lower() in ["right", "r", "6"] and self.move_options["right"] is not None:
                print("moving right")
                self.location = f'{self.move_options["right"]}'
                return True
            elif move_choice.lower() in ["down", "d", "2"] and self.move_options["down"] is not None:
                print("moving down")
                self.location = f'{self.move_options["down"]}'
                return True
            elif move_choice.lower() in ["up", "u", "8"] and self.move_options["up"] is not None:
                print("moving up")
                self.location = f'{self.move_options["up"]}'
                return True
            else:
                print("That is not a valid option. Please select again, .")
            
    def place_fence(self):
        if self.fences_remaining > 0:
            fence_location_1 = input(f'''\nAround which square will the fence go?\n(Enter column letter and row number, such as D5, a3, etc., \nafter this you'll give the specifics like the fence's direction)    ''')            
            while True:
                if fence_location_1.lower in ["back", "b"]:
                    return False
                if fence_location_1.upper() in self.board.locations:
                    # Now to inquire about vertical vs. horizontal, facing up/down/left/right. Will think about simplest way to 
                    # Will append to a list of placed fences, with this list checked in update_display() to replace the lines with "Xs"
                    self.fences_remaining -= 1
                    return fence_location_1.upper()
                else:
                    # Keep asking until user enters valid square, or goes back
                    fence_location_1 = input(f'''\nPlease select a space on the board (column letter + row number, such as D5, a3, etc.), \nafter this you'll give the specifics like the fence's direction)    ''')                     
        else:
            print("You have no more fences to place.")
            return False


# In[ ]:


class Quoridor():
    
    def __init__(self, player1 = "Player1", player2 = "Player2", custom_size = 9,done_turn = False):
        self.player1 = player1
        self.player2 = player2        
        self.board = None
        self.custom_size = custom_size
        self.done_turn = done_turn
        
    def game_setup(self, player1 = "Player1", player2 = "Player2"):
        print(f"""It's Quoridor time!""")
        player1_name = input(f'''\nWhat is the name of player 1?   ''')
        player2_name = input(f'''What is the name of player 2?   ''')
        player1 = Player(name = player1_name)
        player2 = Player(name = player2_name)

        settings = input(f'''\nEnter "custom" or "c" to enter custom settings, \nenter anything else and the game will begin.   ''')
        if settings in ["custom","c"]:
            custom_size = input(f'''\nHow large would you like the board to be? (enter a number from 3 to 9).   ''')
            self.custom_size = custom_size
            # Todo later: accept custom number of fences to start

        # instantiate players and board 
        self.player1 = player1
        self.player2 = player2
        #print(self.custom_size)
        self.board = Board(size = int(self.custom_size))
        # associate players with board, and board with players
        self.player1.board = self.board
        self.player2.board = self.board
        self.board.player1 = player1
        self.board.player2 = player2
        # set starting positions and update display
        self.player1.location = self.board.columns[int(len(self.board.columns)/2)]+f'{len(self.board.columns)}'
        self.player2.location = self.board.columns[int(len(self.board.columns)/2)]+"1"
        self.player2.marker = '\u25A0'
        #self.player1.name = self.player1.name + " (" + self.player1.marker
        #self.player2.name = self.player2.name + " (" + self.player2.marker
        self.board.update_display()
        print("\nGame initialized!")
        self.set_first_turn()

    # determine first turn (currently, alphabetical)
    def set_first_turn(self):
        if self.player1.name <= self.player2.name:
            self.player1.turn = True
            print("We'll start with {} ({}).".format(self.player1.name, self.player1.marker))
            self.take_turn()
        else: 
            self.player2.turn = True
            print("We'll start with {} ({}).".format(self.player2.name, self.player2.marker))
            self.take_turn()
            
    def take_turn(self):           
        self.board.show_display()
        self.done_turn = False
        while not self.done_turn:
            if self.player1.turn:
                player = self.player1              
            if self.player2.turn: 
                player = self.player2
            #print("you are at location {}".format(player.location))
            action = input(f'''{player.name} ({player.marker}), would you like to: \n    1. Make a move, or\n    2. Place a fence? ({player.fences_remaining} fences remaining)   ''')
            
            if action.lower() in {'q', 'quit', 'e', 'exit'}:
                print("Goodbye!")
                raise SystemExit("Player quit");
                #ToDo: a prettier way to exit. Also a way to make this an optain from all input prompts
                
            if action == "1":
                print("makin moves")
                if player.move_piece() == True:
                    self.done_turn = True
                    clear_output() # clearing output at the end of turns makes sense because you'll show the display at the start of the next turn
                    self.board.update_display()
                    print(f'''{player.name} ({player.marker}) moved to {player.location}.''')
                    self.change_turns()
                else:
                    print(f'''Please try again.\n''')
                    
            elif action == "2":
                print("fence time")
                self.fence_placement = player.place_fence()
                if self.fence_placement in self.board.locations:                    
                    self.done_turn = True
                    #clear_output() # clearing output at the end of turns makes sense because you'll show the display at the start of the next turn
                    self.board.update_display()    
                    print(f'''{player.name} ({player.marker}) placed a fence next to {self.fence_placement}.''')
                    self.change_turns()
                else:
                    print(f'''Please try again.\n''')
            else:
                print("\nYou must enter 1 or 2 to continue. If you want to quit, enter 'q' or 'quit'.\n")
        
    def change_turns(self):
        self.check_win()
        self.player1.turn = not self.player1.turn
        self.player2.turn = not self.player2.turn
        self.take_turn()

    def check_win(self):
        if self.player1.location[1] == '1':
            self.board.show_display()
            print(f'''CONGRATULATIONS {self.player1.name}, you have won Quoridor!''')
            raise SystemExit(f'''{self.player1.name} won!''');
        elif self.player2.location[1] == f'{len(self.board.columns)}':
            self.board.show_display()
            print(f'''CONGRATULATIONS {self.player2.name}, you have won Quoridor!''')
            raise SystemExit(f'''{self.player2.name} won!''');
        else:
            pass


# In[ ]:


# This is how to kick off a game from this file
from IPython.display import clear_output # might not need depending on view in console
game = Quoridor()
game.game_setup()

