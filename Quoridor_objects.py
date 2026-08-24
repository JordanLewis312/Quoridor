#!/usr/bin/env python
# coding: utf-8

# Load required packages
import math
from collections import deque

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

# define Board attributes and methods
class Board:

    def __init__(self, size=9):
        self.size = size
        self.locations = [(row, col) for row in range(1, self.size+1) for col in range(1, self.size+1)]
        
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
               self.horizontal_pairs[each] = [(each, right), None]

            # Check down neighbor for vertical pair
            down = (row + 1, col)
            if self.is_fence_location(down):
                self.vertical_pairs[each] = [(each, down), None]
     
    def is_blocked(self, r, c, dr, dc):
        hp = self.horizontal_pairs
        vp = self.vertical_pairs
        if dr == -1:  # moving up
            return (hp.get((r, c),     [None, None])[1] is not None or
                    hp.get((r, c-1),   [None, None])[1] is not None)
        if dr == 1:   # moving down
            return (hp.get((r+1, c),   [None, None])[1] is not None or
                    hp.get((r+1, c-1), [None, None])[1] is not None)
        if dc == -1:  # moving left
            return (vp.get((r, c),     [None, None])[1] is not None or
                    vp.get((r-1, c),   [None, None])[1] is not None)
        if dc == 1:   # moving right
            return (vp.get((r, c+1),   [None, None])[1] is not None or
                    vp.get((r-1, c+1), [None, None])[1] is not None)

    def serialize(self):
        h = [[r, c, owner] for (r, c), (_, owner) in self.horizontal_pairs.items() if owner is not None]
        v = [[r, c, owner] for (r, c), (_, owner) in self.vertical_pairs.items() if owner is not None]
        return {"horizontal": h, "vertical": v}

    def has_path(self, start, goal_row):
        queue = deque([start])
        visited = set([start])
        while queue:
            r, c = queue.popleft()
            if r == goal_row:
                return True
            for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                nr, nc = r + dr, c + dc
                neighbor = (nr, nc)
                if not (1 <= nr <= self.size and 1 <= nc <= self.size):
                    continue
                if neighbor in visited:
                    continue
                if self.is_blocked(r, c, dr, dc):
                    continue
                visited.add(neighbor)
                queue.append(neighbor)
        return False


# define QuoridorGame class to manage game state and flow
class QuoridorGame:

    def __init__(self, player1_name, player2_name, size=9, fences=10):
        self.board = Board(size=size)
        self.board.create_fence_locations()
        mid = math.ceil(size / 2)
        self.players = [
            {"name": player1_name, "location": [size, mid], "fences_remaining": fences, "goal_row": 1},
            {"name": player2_name, "location": [1,    mid], "fences_remaining": fences, "goal_row": size},
        ]
        self.current_player = 0
        self.status = "playing"
        self.winner = None
        self.must_move_again = False

    def move_piece(self, player_index, direction):
        DIRECTIONS = {"up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1)}

        if self.status != "playing":
            return {"ok": False, "error": "Game is over."}
        if player_index != self.current_player:
            return {"ok": False, "error": "It is not your turn."}
        if direction not in DIRECTIONS:
            return {"ok": False, "error": f"Invalid direction '{direction}'."}

        player   = self.players[player_index]
        opponent = self.players[1 - player_index]
        r, c     = player["location"]
        dr, dc   = DIRECTIONS[direction]
        nr, nc   = r + dr, c + dc

        if not (1 <= nr <= self.board.size and 1 <= nc <= self.board.size):
            return {"ok": False, "error": f"Can't move {direction} — edge of board."}
        if self.board.is_blocked(r, c, dr, dc):
            return {"ok": False, "error": f"Can't move {direction} — fence is blocking."}

        player["location"] = [nr, nc]

        if [nr, nc] == opponent["location"]:
            self.must_move_again = True
            return {
                "ok": True,
                "must_move_again": True,
                "message": f"You are on top of {opponent['name']}! Move again — where to next?",
                "state": self.serialize(),
            }

        self.must_move_again = False
        self._advance_turn()
        return {"ok": True, "must_move_again": False, "state": self.serialize()}

    def _advance_turn(self):
        for player in self.players:
            if player["location"][0] == player["goal_row"]:
                self.status = "game_over"
                self.winner = player["name"]
                return
        self.current_player = 1 - self.current_player

    def place_fence(self, player_index, row, col, orientation):
        if self.status != "playing":
            return {"ok": False, "error": "Game is over."}
        if player_index != self.current_player:
            return {"ok": False, "error": "It is not your turn."}

        if self.must_move_again:
            return {"ok": False, "error": "You must move again before placing a fence."}

        player = self.players[player_index]
        if player["fences_remaining"] <= 0:
            return {"ok": False, "error": "You have no fences remaining."}

        orientation = orientation.upper()
        if orientation not in ("H", "V"):
            return {"ok": False, "error": "Orientation must be 'H' or 'V'."}

        size = self.board.size

        if orientation == "H":
            if col == size:
                return {"ok": False, "error": "a horizontal fence can't start on the last column - it'd go off the board!"}
            if row == 1:
                return {"ok": False, "error": "A horizontal fence above row 1 doesn't block anything."}
            pd = self.board.horizontal_pairs
            if (row, col) not in pd:
                return {"ok": False, "error": "Invalid fence location."}
            if pd[(row, col)][1] is not None:
                return {"ok": False, "error": "A fence already exists here."}
            for nb in [(row, col + 1), (row, col - 1)]:
                if pd.get(nb, [None, None])[1] is not None:
                    return {"ok": False, "error": "An adjacent horizontal fence conflicts with this placement."}
            if self.board.vertical_pairs.get((row - 1, col + 1), [None, None])[1] is not None:
                return {"ok": False, "error": "A perpendicular vertical fence crosses this placement."}
        else:
            if row == size:
                return {"ok": False, "error": "a vertical fence can't start on the last row - it'd go off the board!"}
            if col == 1:
                return {"ok": False, "error": "A vertical fence left of column 1 doesn't block anything."}
            pd = self.board.vertical_pairs
            if (row, col) not in pd:
                return {"ok": False, "error": "Invalid fence location."}
            if pd[(row, col)][1] is not None:
                return {"ok": False, "error": "A fence already exists here."}
            for nb in [(row - 1, col), (row + 1, col)]:
                if pd.get(nb, [None, None])[1] is not None:
                    return {"ok": False, "error": "An adjacent vertical fence conflicts with this placement."}
            if self.board.horizontal_pairs.get((row + 1, col - 1), [None, None])[1] is not None:
                return {"ok": False, "error": "A perpendicular horizontal fence crosses this placement."}

        pd[(row, col)][1] = player_index
        p0_ok = self.board.has_path(tuple(self.players[0]["location"]), self.players[0]["goal_row"])
        p1_ok = self.board.has_path(tuple(self.players[1]["location"]), self.players[1]["goal_row"])
        if not p0_ok or not p1_ok:
            pd[(row, col)][1] = None
            trapped = self.players[0]["name"] if not p0_ok else self.players[1]["name"]
            return {"ok": False, "error": f"Can't place fence — {trapped} would have no path to their goal."}

        player["fences_remaining"] -= 1
        self._advance_turn()
        return {"ok": True, "state": self.serialize()}

    def serialize(self):
        return {
            "board_size":      self.board.size,
            "current_player":  self.current_player,
            "status":          self.status,
            "winner":          self.winner,
            "must_move_again": self.must_move_again,
            "players": [
                {"name": p["name"], "location": p["location"], "fences_remaining": p["fences_remaining"]}
                for p in self.players
            ],
            "fences": self.board.serialize(),
        }
