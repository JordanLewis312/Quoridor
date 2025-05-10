# Load required packages
import string
import math
from IPython.display import clear_output

# 2 global functions: since A1 notation (a la chess) is likely most intuitive for players, but (r,c) format is more flexible for backend data processing, RCify() and A1ify() quickly convert a location to the necessary format. 

def RCify(label, size):    
    if label == "":
        return    
    elif not label[0].isalpha() or not label[1:].isdigit():
        print("Label must be in format like 'A1', 'C2', etc.")
        return
    col_letter = label[0].upper()
    row = int(label[1:])

    if not ('A' <= col_letter <= chr(ord('A') + size - 1)) or not (1 <= row <= size):
        print((f"Label must be within A1 to {chr(ord('A') + size - 1)+str(size)}"))
        return
    col = ord(col_letter) - ord('A') + 1
    return (row, col)

def A1ify(location):
    row, col = location
    col_letter = chr(ord('A') + col - 1)
    return f"{col_letter}{row}"

class Board:

    def __init__(self,size = 9):
        self.size = size
        self.fence_spots = self.size - 1
        self.total_board_size = size + self.fence_spots
        self.player1 = "placeholder"
        self.player2 = "placeholder2"

        self.columns = list(string.ascii_uppercase[:self.size]) 
        self.locations = [(row, col) for row in range(1, self.size+1) for col in range(1, self.size+1)]
        self.display = self.create_display(size = self.size) # write to var for use in other functions
        self.starting_display = self.create_display(self.size)
        
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

    def is_fence_location(self,location):
        r, c = location
        return 1 <= r <= self.size and 1 <= c <= self.size
        
    def create_fence_locations(self):
        self.horizontal_pairs = {}
        self.vertical_pairs = {}
        for each in self.locations:
            row, col = each
            # Check right neighbor for horizontal pair
            right = (row, col + 1)
            if self.is_fence_location(right):
               self.horizontal_pairs[each] = [(each, right), "empty"]

            # Check down neighbor for vertical pair
            down = (row + 1, col)
            if self.is_fence_location(down):
                self.vertical_pairs[each] = [(each, down), "empty"]
     
    def update_display(self):
        self.display = self.create_display(size = self.size)
        for each in [self.player1, self.player2]:
            # Set player's current location on display to their marker
            prow = each.location[0]
            pcol = each.location[1]
            self.display[prow*2][5+6*(pcol)]= each.marker
            # label player's current location as starting location (for future moves)
            each.starting_location = each.location 

        for each in self.horizontal_pairs:
            if self.horizontal_pairs[each][1] != "empty":
                for i in range(0, 2):
                    fenceRow = self.horizontal_pairs[each][0][i][0]
                    fenceCol = self.horizontal_pairs[each][0][i][1]
                    self.display[-1+fenceRow*2][5+6*(fenceCol)]= self.horizontal_pairs[each][1].fencemarker
                self.display[fenceRow*2-1][5+6*(fenceCol)-3]= self.horizontal_pairs[each][1].fencemarker # add marker in-between 2 fences to show fence extends through 
        for each in self.vertical_pairs:
            if self.vertical_pairs[each][1] != "empty":
                for i in range(0, 2):
                    fenceRow = self.vertical_pairs[each][0][i][0]
                    fenceCol = self.vertical_pairs[each][0][i][1]
                    self.display[fenceRow*2][2+6*(fenceCol)]= self.vertical_pairs[each][1].fencemarker
                self.display[fenceRow*2-1][2+6*(fenceCol)]= self.vertical_pairs[each][1].fencemarker # add marker in-between 2 fences to show fence extends through 

class Player:

    def __init__(self, name, marker = "A", location = (2,1), fences = 10, turn = False):
        self.name = name
        self.marker = '\u25A1'
        self.fences = fences
        self.fencemarker = '\u25A0'
        self.fences_remaining = fences
        self.location = location
        self.previous_location = location
        self.turn = turn
        self.board = None
        self.opponent = None

    def __str__(self):
        return f'''{self.name}, location {self.location}, {self.fences_remaining} fences remaining{", their turn" if self.turn else ""}.'''

    def move_piece(self):
        must_move_again = False  # Set True if player is standing on opponent after a move
        dir_inputs = {
            "up": ["up", "u", "1"],
            "down": ["down", "d", "2"],
            "left": ["left", "l", "3"],
            "right": ["right", "r", "4"],
        }
        while True:  # Prompt repeats until player moves to unoccupied space or goes back
            while True:  # Inner loop (happens a second time if player moves onto opponent's location, so that they move again)
                ### Determine move_options based on current location
                self.move_options = {}
                # Store reason to display when moves are blocked by fences
                self.move_block_reasons = {}  
                directions = {
                    "up":    (-1, 0, lambda r, c: r > 1),
                    "down":  (1, 0,  lambda r, c: r < self.board.size),
                    "left":  (0, -1, lambda r, c: c > 1),
                    "right": (0, 1,  lambda r, c: c < self.board.size),
                }

                ### Check each direction for a fence that would block the move (since fences are 2 spaces long, there are 2 potential fence spots to check)
                r, c = self.location
                for dir, (dr, dc, condition) in directions.items():
                    new_pos = (r + dr, c + dc)
                    if condition(r, c):
                        blocked = False
                        reason = ""

                        if dir == "left":
                            fences_to_check = [(r, c), (r-1, c)]
                            for fence_rc in fences_to_check:
                                fence_data = self.board.vertical_pairs.get(fence_rc, [None, "empty"])
                                if fence_data[1] != "empty":
                                    blocked = True
                                    ends = fence_data[0]
                                    reason = f"(the vertical fence at {A1ify(ends[0])}-{A1ify(ends[1])} blocks moving left to {A1ify(new_pos)})"
                                    break
                        elif dir == "right":
                            fences_to_check = [(r, c+1), (r-1, c+1)]
                            for fence_rc in fences_to_check:
                                fence_data = self.board.vertical_pairs.get(fence_rc, [None, "empty"])
                                if fence_data[1] != "empty":
                                    blocked = True
                                    ends = fence_data[0]
                                    reason = f"(the vertical fence at {A1ify(ends[0])}-{A1ify(ends[1])} blocks moving right to {A1ify(new_pos)})"
                                    break
                        elif dir == "up":
                            fences_to_check = [(r, c), (r, c-1)]
                            for fence_rc in fences_to_check:
                                fence_data = self.board.horizontal_pairs.get(fence_rc, [None, "empty"])
                                if fence_data[1] != "empty":
                                    blocked = True
                                    ends = fence_data[0]
                                    reason = f"(the horizontal fence at {A1ify(ends[0])}-{A1ify(ends[1])} blocks moving up to {A1ify(new_pos)})"
                                    break
                        elif dir == "down":
                            fences_to_check = [(r+1, c), (r+1, c-1)]
                            for fence_rc in fences_to_check:
                                fence_data = self.board.horizontal_pairs.get(fence_rc, [None, "empty"])
                                if fence_data[1] != "empty":
                                    blocked = True
                                    ends = fence_data[0]
                                    reason = f"(the horizontal fence at {A1ify(ends[0])}-{A1ify(ends[1])} blocks moving down to {A1ify(new_pos)})"
                                    break
                        if not blocked:
                            self.move_options[dir] = new_pos
                        else:
                            self.move_options[dir] = None
                            self.move_block_reasons[dir] = reason
                    else:
                        self.move_options[dir] = None
                        self.move_block_reasons[dir] = f"(can't move {dir})"
                        
                # Build move prompt
                move_prompt = f"\nWhere would you like to move, {self.name} ({self.marker})?\n"
                if must_move_again:
                    move_prompt += f"You are now on top of {self.opponent.name}! Move again, {self.name} - where to next?)\n"
                    must_move_again = False

                for idx, dir in enumerate(["up", "down", "left", "right"], 1):
                    inputs = dir_inputs[dir]
                    move = self.move_options[dir]
                    if isinstance(move, tuple):
                        move_prompt += f"> {idx}: {dir.capitalize()} to {A1ify(move)} (enter {', '.join(f'\"{i}\"' for i in inputs)})\n"
                    else:
                        reason = self.move_block_reasons.get(dir, f"(can't move {dir})")
                        move_prompt += f"> {idx}: {reason}\n"
                move_prompt += "> 9: Go back (enter \"back\", \"b\" or \"9\")\n"

                move_choice = input(move_prompt).lower()
                if move_choice in ["back", "b", "9"]:
                    return False
                
                valid_move = False
                for dir, inputs in dir_inputs.items():
                    if move_choice in inputs and isinstance(self.move_options[dir], tuple):
                        print(f"moving {dir}")
                        self.previous_location = self.location
                        self.location = self.move_options[dir]
                        valid_move = True
                        self.board.update_display()
                        if self.location == self.opponent.location:
                            must_move_again = True
                            clear_output()
                            self.board.show_display()
                            break  # re-enter inner loop to move again
                        else:
                            return True
                if not valid_move:
                    print("That is not a valid move option. Please select again.")
            
    def place_fence(self):
        if self.fences_remaining <= 0:
            print("You have no more fences to place.")
            return False

        while True:
            fence_location_A1 = input(f'''\nAround which square will the fence go?\n(Enter column letter and row number, 
            such as D5, a3, etc., \nThe fence starts in that cell's top left corner, \nyou'll then specify whether the fence goes right or down)''')

            if fence_location_A1.lower() in ["back", "b", "stop", "q", "9"]:
                return False

            fence_RC = RCify(fence_location_A1.upper(), self.board.size)
            if fence_RC not in self.board.locations:
                print(f'''\nPlease select a valid space on the board ("A2", "C3", etc.) to start building a fence.''')
                continue

            horiz_text, vert_text = "", ""
            check_horiz, check_vert = True, True

            # Board-edge constraints
            if fence_RC[1] == self.board.size:
                check_horiz = False
                horiz_text += "(Can't select a horizontal fence starting on the last column - it'd go off the board!)"
            if fence_RC[0] == 1:
                check_horiz = False
                horiz_text += ("\n" + " " * 17 if horiz_text else "") + \
                    "(A horizontal fence above the first row doesn't block anywhere! Choose from the second row and below)"
            if fence_RC[0] == self.board.size:
                check_vert = False
                vert_text += "(Can't select a vertical fence starting on the last row - it'd go off the board!)"
            if fence_RC[1] == 1:
                check_vert = False
                vert_text += ("\n" + " " * 17 if vert_text else "") + \
                    "(A fence to the left of the first column doesn't block anywhere! Choose from the second column and over)"

            def fence_block_msg(pair_dict, rc, orientation):
                owner = pair_dict.get(rc, [None, "empty"])[1]
                if owner != "empty":
                    ends = pair_dict[rc][0]
                    owner_name = "you already have" if owner == self else owner.name + " already has"
                    return f"(can't place {orientation}, {owner_name} a fence at {A1ify(ends[0])}-{A1ify(ends[1])} which blocks this)"
                return ""

            # Horizontal fence overlap + crossing checks
            if check_horiz:
                fence_H = self.board.horizontal_pairs[fence_RC]
                conflicts = []

                if fence_H[1] != "empty":
                    owner_name = "you already have" if fence_H[1] == self else fence_H[1].name + " already has"
                    conflicts.append(f"(can't place horizontal fence - {owner_name} a fence at {A1ify(fence_H[0][0])}-{A1ify(fence_H[0][1]):})")
                for neighbor in [
                    (fence_RC[0], fence_RC[1] + 1),
                    (fence_RC[0], fence_RC[1] - 1)
                ]:
                    msg = fence_block_msg(self.board.horizontal_pairs, neighbor, "horizontally")
                    if msg:
                        conflicts.append(msg)

                # Check for perpendicular crossing: vertical at (r-1, c+1)
                crossing_rc = (fence_RC[0] - 1, fence_RC[1] + 1)
                crossing_entry = self.board.vertical_pairs.get(crossing_rc, [None, "empty"])
                crossing_owner = crossing_entry[1]
                if crossing_owner != "empty":
                    ends = self.board.vertical_pairs[crossing_rc][0]
                    owner_name = "you already have" if crossing_owner ==self else crossing_owner.name + " already has"
                    conflicts.append(f"(can't place horizontal fence — {owner_name} a vertical fence at {A1ify(ends[0])}-{A1ify(ends[1])} which overlaps with this)")
                if conflicts:
                    check_horiz = False
                    horiz_text += ("\n" + " " * 17).join(conflicts) if len(conflicts) > 1 else conflicts[0]

            # Vertical fence overlap + crossing checks
            if check_vert:
                fence_V = self.board.vertical_pairs[fence_RC]
                conflicts = []

                if fence_V[1] != "empty":
                    owner_name = "you already have" if fence_V[1] == self else fence_V[1].name + " already has"
                    conflicts.append(f"(can't place vertical fence - {owner_name} a fence at {A1ify(fence_V[0][0])}-{A1ify(fence_V[0][1]):})")
                for neighbor in [
                    (fence_RC[0] - 1, fence_RC[1]),
                    (fence_RC[0] + 1, fence_RC[1])
                ]:
                    msg = fence_block_msg(self.board.vertical_pairs, neighbor, "vertically")
                    if msg:
                        conflicts.append(msg)

                # Check for perpendicular crossing: horizontal at (r+1, c-1)
                crossing_rc = (fence_RC[0] + 1, fence_RC[1] - 1)
                crossing_entry = self.board.horizontal_pairs.get(crossing_rc, [None, "empty"])
                crossing_owner = crossing_entry[1]
                if crossing_owner != "empty":
                    ends = self.board.horizontal_pairs[crossing_rc][0]
                    owner_name = "you already have" if crossing_owner ==self else crossing_owner.name + " already has"
                    conflicts.append(f"(can't place vertical fence — {owner_name} a horizontal fence at {A1ify(ends[0])}-{A1ify(ends[1])} which overlaps with this)")
                if conflicts:
                    check_vert = False
                    vert_text += ("\n" + " " * 17).join(conflicts) if len(conflicts) > 1 else conflicts[0]

            # Prompt user to select direction now that checks are done
            fence_direction = input(f'''\nShould the fence at {fence_location_A1} be \n
                > 1. {f'Horizontal above {A1ify(fence_H[0][0])} to {A1ify(fence_H[0][1])} (enter "1", "H", or "h")' if check_horiz else horiz_text}
                > 2. {f'Vertical from {A1ify(fence_V[0][0])} to {A1ify(fence_V[0][1])} (enter "2", "V", or "v")' if check_vert else vert_text}    
                > 9. Go back (enter "back", "b" or "9")\n''')

            if fence_direction.lower() in ["back", "b", "stop", "q", "9"]:
                return False

            def confirm_and_finalize(fence, orientation_text):
                fence[1] = self
                self.board.update_display()
                clear_output()
                self.board.show_display()
                confirm = input(f'''Fence placed {orientation_text}! If this doesn't look right to you, enter ("no", "n","back" or "b") to try again, otherwise press any key to continue''')
                if confirm.lower() not in ["no", "n", "back", "b"]:
                    clear_output()
                    print(f'''{self.name} ({self.marker}) has placed a fence {orientation_text}''')
                    self.fences_remaining -= 1
                    return True
                else:
                    fence[1] = "empty"
                    self.board.update_display()
                    clear_output()
                    self.board.show_display()
                    return None  # loop continues

            if fence_direction.lower() in ["1", "h"] and check_horiz:
                result = confirm_and_finalize(fence_H, f"above {A1ify(fence_H[0][0])}-{A1ify(fence_H[0][1])}")
                if result is not None:
                    return result
            elif fence_direction.lower() in ["2", "v"] and check_vert:
                result = confirm_and_finalize(fence_V, f"to the left of {A1ify(fence_V[0][0])}-{A1ify(fence_V[0][1])}")
                if result is not None:
                    return result
            else:
                print("That is not a valid option. Please select again.")

class Quoridor():
    
    def __init__(self, player1 = "Player1", player2 = "Player2", board = None, custom_size = 9,done_turn = False):
        self.player1 = player1
        self.player2 = player2        
        self.board = None
        self.custom_size = custom_size
        self.done_turn = done_turn
        
    def game_setup(self, player1 = "Player1", player2 = "Player2"):
        print(f"""It's Quoridor time!
          A     B     C     D     E     F     G     H
       |—————|—————|—————|—————|—————|—————|—————|—————|
     1 |     |     |     |     |     |     |     |     | 1
       |—————|—————|—————|—————|—————|—————|——●——●——●——|
     2 |     |     |     |     |     |     ●     |     | 2
       |—————|—————|—————|——●——●——●——|—————●—————|—————|
     3 |     |     |     ●     |     |     ●     |     | 3
       |—————|—————|—————●—————|——●——●——●——|—————|—————|
     4 |     |     |     ●  □  ●     |     |     |     | 4
       |—————|——■——■——■——|—————●—————|—————|—————|—————|
     5 |     |     |     |     ●     |     |     |     | 5
       |—————|—————|—————|—————|—————|—————|—————|—————|
     6 |     |     |     |     |     |     |     |     | 6
       |—————|—————|——■——■——■——|——■——■——■——|—————|—————|
     7 |     |     |     |  ○  |     |     ■     |     | 7
       |—————|—————|—————|—————|—————|—————■—————|—————|
     8 |     |     |     |     |     |     ■     |     | 8
       |—————|—————|—————|—————|—————|—————|—————|—————|
          A     B     C     D     E     F     G     H     
Get yourself to the other side to win. Place fences to slow down 
your opponent's path and secure your own!""")
        # Get player names
        player1 = Player(name=input("\nWhat is the name of player 1?   "))
        player2 = Player(name=input("What is the name of player 2?   "))

        # Optional custom settings
        settings = input('\nEnter "custom" or "c" to enter custom settings,\nenter anything else and the game will begin.   ')
        self.custom_size = input("\nHow large would you like the board to be? (enter a number from 3 to 9).   ") if settings in ["custom", "c"] else 9
        # ToDo: accept custom number of fences to start

        # instantiate players, board, and fence locations
        self.player1, self.player2 = player1, player2
        self.player1.opponent = player2
        self.player2.opponent = player1
        self.board = Board(size = int(self.custom_size))
        self.board.create_fence_locations()
        # Associate players with board, and board with players
        self.player1.board = self.board
        self.player2.board = self.board
        self.board.player1 = player1
        self.board.player2 = player2
        
        # Set starting positions and update display
        mid_col = math.ceil(self.board.size / 2)
        self.player1.location = (self.board.size, mid_col)
        self.player2.location = (1, mid_col)
        self.player2.marker = '\U000025CB'
        self.player2.fencemarker = '\U000025CF'
        self.board.update_display()

        self.first_turn_input = input("""\nNote: Since this is a text-based version of Quoridor,
squares on the board are referred to by their column letter and row number,
like "A3" refers to the first column, 3rd row from the top.
                                      
When placing fences between squares, by default they'll start on
the edges closer to A1, i.e. TOP LEFT corner of the square.
So the horizontal "fence C2" will go above C2 and D2, visualized below:
                A     B     C     D     E     F     G
                |—————|—————|—————|—————|—————|—————|—————|
            1   |     |     |     |     |     |     |     | 
                |—————|—————|——●——●——●——|—————|—————|—————|
            2   |     |     ■  ^the C2 horizontal fence   | 
                |—————|—————■—————|—————|—————|—————|—————|
            3   |     |     ■  <-the C2 vertical fence    |
                                      
Press any key to start the game with Player 1 going first (or enter "2" or "two" to start with Player 2)""")
        self.set_first_turn()

    # determine first turn
    def set_first_turn(self):
        self.first_turn = self.player2 if self.first_turn_input.lower() in ["no", "n", "2", "two"] else self.player1
        self.first_turn.turn = True
        clear_output()
        print("We'll start with {} ({}).".format((self.first_turn).name, (self.first_turn).marker))
        self.take_turn()
            
    def take_turn(self):           
        self.done_turn = False
        while not self.done_turn:
            if self.player1.turn:
                player = self.player1              
            if self.player2.turn: 
                player = self.player2
            self.board.show_display()
            action = input(f'''{player.name} ({player.marker}), would you like to: \n    1. Move one space, or\n    2. Place a fence? ({player.fences_remaining} fences remaining)   ''')
            
            if action.lower() in {'q', 'quit', 'e', 'exit'}:
                print("Goodbye!")
                raise SystemExit("Player quit");
                #ToDo: a prettier way to exit. Also a way to make this an option from all input prompts
                
            if action == "1":
                print("Makin' moves")
                if player.move_piece() == True:
                    self.done_turn = True
                    clear_output()
                    print(f'''{player.name} ({player.marker}) has moved to {A1ify(player.location)}.''')
                    self.change_turns()
                else:
                    print(f'''Please try again.\n''')
                    
            elif action == "2":
                print("Fencing time")
                if player.place_fence() == True:            
                    self.done_turn = True
                    self.change_turns()
                else:
                    print(f'''Please try again.\n''')
            else:
                print("\nYou must enter 1 or 2 to continue. If you want to quit, enter 'q' or 'quit'.\n")

        # End turn
        
    def change_turns(self):
        self.check_win()
        self.player1.turn = not self.player1.turn
        self.player2.turn = not self.player2.turn
        self.take_turn()

    def check_win(self):
        if self.player1.location[0] == 1:
            self.board.show_display()
            print(f'''CONGRATULATIONS {self.player1.name}, you have won Quoridor!''')
            raise SystemExit(f'''{self.player1.name} won!''');
        elif self.player2.location[0] == self.board.size:
            self.board.show_display()
            print(f'''CONGRATULATIONS {self.player2.name}, you have won Quoridor!''')
            raise SystemExit(f'''{self.player2.name} won!''');
        else:
            pass

raise Exception("when the objects file is called by Quoridor.ipynb, it will stop reading here");

# %%
# This is how to kick off a game from this file
from IPython.display import clear_output # might not need depending on view in console
game = Quoridor()
game.game_setup()
