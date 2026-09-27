from Quoridor_objects import QuoridorGame

def test_basic_move():
    game = QuoridorGame("Alice", "Bob")
    result = game.move_piece(0, "up")
    assert result["ok"], f"Expected move to succeed: {result}"
    assert game.players[0]["location"] == [8, 5], f"Unexpected location: {game.players[0]['location']}"
    assert game.current_player == 1, "Turn should have advanced to player 2"
    print("PASS: basic move")

def test_wrong_turn():
    game = QuoridorGame("Alice", "Bob")
    result = game.move_piece(1, "down")
    assert not result["ok"], "Expected failure — it's not player 2's turn"
    print("PASS: wrong turn rejected")

def test_fence_blocks_move():
    game = QuoridorGame("Alice", "Bob")
    # Place a horizontal fence above row 9, col 5 — directly in Alice's path upward
    result = game.place_fence(0, 9, 5, "H")
    assert result["ok"], f"Expected fence placement to succeed: {result}"
    # Now try to move Alice up through that fence
    result = game.move_piece(1, "down")  # Bob moves first now
    result = game.move_piece(0, "up")
    assert not result["ok"], "Expected move to be blocked by fence"
    assert "fence" in result["error"].lower(), f"Unexpected error: {result['error']}"
    print("PASS: fence blocks move")

def test_fence_cannot_trap_player():
    game = QuoridorGame("Alice", "Bob")
    # Manually set 4 horizontal fences across row 5, covering cols 1-4 and 7-9
    # Leaves only cols 5-6 as Alice's path to row 1
    game.board.horizontal_pairs[(5, 1)][1] = 0
    game.board.horizontal_pairs[(5, 3)][1] = 0
    game.board.horizontal_pairs[(5, 7)][1] = 0
    game.board.horizontal_pairs[(5, 8)][1] = 0
    # Fence at (5,5) covers cols 5-6, completing the wall
    # Not adjacent to (5,3) or (5,7) — differs by 2 — so adjacency check passes
    # Only BFS can catch this
    result = game.place_fence(0, 5, 5, "H")
    assert not result["ok"], "Expected fence to be rejected — it would trap Alice"
    assert "path" in result["error"].lower(), f"Unexpected error: {result['error']}"
    print("PASS: trapping fence rejected")

def test_win_condition():
    game = QuoridorGame("Alice", "Bob")
    # Move Alice all the way to row 1
    game.players[0]["location"] = [2, 5]  # shortcut her close to the goal
    game.players[1]["location"] = [1, 1]  # move Bob out of Alice's path
    result = game.move_piece(0, "up")
    assert result["ok"], f"Expected move to succeed: {result}"
    assert game.status == "game_over", "Expected game_over status"
    assert game.winner == "Alice", f"Expected Alice to win, got: {game.winner}"
    print("PASS: win condition")

def test_serialize_shape():
    game = QuoridorGame("Alice", "Bob")
    game.place_fence(0, 5, 5, "H")
    state = game.serialize()
    assert "board_size" in state
    assert "players" in state
    assert "fences" in state
    assert len(state["fences"]["horizontal"]) == 1
    assert state["fences"]["horizontal"][0] == [5, 5, 0]
    print("PASS: serialize shape")

def test_from_state_roundtrip():
    game = QuoridorGame("Alice", "Bob")
    game.move_piece(0, "up")
    game.place_fence(1, 5, 5, "H")
    state = game.serialize()

    rebuilt = QuoridorGame.from_state(state)
    assert rebuilt.serialize() == state, "Rebuilt game should serialize back to the exact same state"

    # Confirm the rebuilt object is actually functional, not just data-equal --
    # it needs to support further moves/fences the same as the original.
    result = rebuilt.move_piece(0, "left")
    assert result["ok"], f"Rebuilt game should support further moves: {result}"
    print("PASS: from_state round-trip")

if __name__ == "__main__":
    test_basic_move()
    test_wrong_turn()
    test_fence_blocks_move()
    test_fence_cannot_trap_player()
    test_win_condition()
    test_serialize_shape()
    test_from_state_roundtrip()
    print("\nAll tests passed.")
