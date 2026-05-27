#!/usr/bin/env python
# coding: utf-8

# Load required packages

from Quoridor_objects_2 import Board, Player

from collections import deque

def is_blocked(board, r, c, dr, dc):
  """Check if a fence blocks moving from (r,c) in direction (dr,dc)."""
  hp = board.horizontal_pairs
  vp = board.vertical_pairs

  if dr == -1:  # moving up
      return (hp.get((r, c),   [None, "empty"])[1] != "empty" or
              hp.get((r, c-1), [None, "empty"])[1] != "empty")
  if dr == 1:   # moving down
      return (hp.get((r+1, c),   [None, "empty"])[1] != "empty" or
              hp.get((r+1, c-1), [None, "empty"])[1] != "empty")
  if dc == -1:  # moving left
      return (vp.get((r, c),   [None, "empty"])[1] != "empty" or
              vp.get((r-1, c), [None, "empty"])[1] != "empty")
  if dc == 1:   # moving right
      return (vp.get((r, c+1),   [None, "empty"])[1] != "empty" or
              vp.get((r-1, c+1), [None, "empty"])[1] != "empty")

def has_path(board, start, goal_row):
  """Return True if start can reach goal_row given current fences."""
  queue = deque([start])
  visited = set([start])

  while queue:
      r, c = queue.popleft()
      print(f"  popped ({r},{c}) | queue size: {len(queue)} | visited: {len(visited)}")

      if r == goal_row:
          print(f"  --> found goal row {goal_row} at ({r},{c})!")
          return True

      for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
          nr, nc = r + dr, c + dc
          neighbor = (nr, nc)
          if not (1 <= nr <= board.size and 1 <= nc <= board.size):
              continue
          if neighbor in visited:
              continue
          if is_blocked(board, r, c, dr, dc):
              print(f"    fence blocks ({r},{c}) -> ({nr},{nc})")
              continue
          visited.add(neighbor)
          queue.append(neighbor)

  print(f"  --> queue empty, no path found")
  return False


# Player 1 starts at bottom row, needs to reach row 1
b2 = Board(size=9)
b2.create_fence_locations()
b2.horizontal_pairs[(5, 4)][1] = "test"  # one fence mid-board
print(has_path(b2, (9, 5), goal_row=1)) 

