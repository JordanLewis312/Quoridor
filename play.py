#!/usr/bin/env python3
from Quoridor_objects import QuoridorGame, RCify

P0_MARKER = '□'  # □
P1_MARKER = '○'  # ○
FENCE     = '●'  # ●

def marker_for(idx):
    return P0_MARKER if idx == 0 else P1_MARKER

def render_board(state):
    size    = state["board_size"]
    players = state["players"]
    h_set   = set(tuple(f) for f in state["fences"]["horizontal"])
    v_set   = set(tuple(f) for f in state["fences"]["vertical"])
    p0      = tuple(players[0]["location"])
    p1      = tuple(players[1]["location"])
    cols    = [chr(ord('A') + i) for i in range(size)]
    lines   = []

    # Header
    lines.append('           ' + '     '.join(cols))

    for r in range(1, size + 1):
        # --- Divider line above row r ---
        div = list('        ' + ('|' + '—————') * size + '|')

        # Horizontal fences: fence at (r, c) marks middle of seg c, the | between segs, middle of seg c+1
        for (fr, fc) in h_set:
            if fr == r:
                div[5 + 6 * fc]       = FENCE
                div[8 + 6 * fc]       = FENCE
                div[5 + 6 * (fc + 1)] = FENCE

        # Vertical fences that span into this divider: vp[(r-1, c)] sits between rows r-1 and r
        for (vr, vc) in v_set:
            if vr == r - 1:
                div[2 + 6 * vc] = FENCE

        lines.append(''.join(div))

        # --- Cell row r ---
        cell = list(f'     {r}  ' + ('|' + '     ') * size + '|' + f' {r}')

        # Player markers (p1 drawn last so it shows on top if sharing a square)
        for p, m in [(p0, P0_MARKER), (p1, P1_MARKER)]:
            if p[0] == r:
                cell[5 + 6 * p[1]] = m

        # Vertical fence separators: vp[(r,c)] and vp[(r-1,c)] both touch row r
        for (vr, vc) in v_set:
            if vr == r or vr == r - 1:
                cell[2 + 6 * vc] = FENCE

        lines.append(''.join(cell))

    # Bottom border and footer
    lines.append('        ' + ('|' + '—————') * size + '|')
    lines.append('           ' + '     '.join(cols))
    return '\n'.join(lines)


def do_move(game, player_index):
    dirs = {"up": "up", "u": "up", "down": "down", "d": "down",
            "left": "left", "l": "left", "right": "right", "r": "right"}
    while True:
        raw = input("    Direction (up/down/left/right)  or 'back': ").strip().lower()
        if raw in ('back', 'b'):
            if game.must_move_again:
                print("    You must move — you can't go back right now.")
                continue
            return False
        if raw not in dirs:
            print("    Enter a direction: up, down, left, right (or u/d/l/r).")
            continue
        result = game.move_piece(player_index, dirs[raw])
        if result["ok"]:
            return True
        print(f"    {result['error']}")


def do_fence(game, player_index):
    print("    Enter location + orientation, e.g. D5H or D5V  (or 'back'):")
    while True:
        raw = input("    > ").strip().upper()
        if raw in ('BACK', 'B'):
            return False
        if len(raw) < 3 or raw[-1] not in ('H', 'V'):
            print("    Format: column letter + row number + H or V  (e.g. D5H, C3V).")
            continue
        loc = RCify(raw[:-1], game.board.size)
        if loc is None:
            print("    That location isn't on the board.")
            continue
        row, col = loc
        result = game.place_fence(player_index, row, col, raw[-1])
        if result["ok"]:
            return True
        print(f"    {result['error']}")


def main():
    print("\nWelcome to Quoridor!\n")
    p1_name = input("Player 1 name: ").strip() or "Player 1"
    p2_name = input("Player 2 name: ").strip() or "Player 2"

    size_raw = input("Board size (3–9, default 9): ").strip()
    size = int(size_raw) if size_raw.isdigit() and 3 <= int(size_raw) <= 9 else 9

    fences_raw = input("Fences per player (1–15, default 10): ").strip()
    fences = int(fences_raw) if fences_raw.isdigit() and 1 <= int(fences_raw) <= 15 else 10

    game = QuoridorGame(p1_name, p2_name, size=size, fences=fences)

    print(f"\nGet to the other side to win!")
    print(f"{p1_name} ({P0_MARKER}) starts at the bottom and moves toward row 1.")
    print(f"{p2_name} ({P1_MARKER}) starts at the top and moves toward row {size}.")
    print(f"\nFences are placed by entering a square + direction, e.g. 'D5H' places a")
    print(f"horizontal fence above D5–E5, and 'D5V' places a vertical fence left of D5–D6.")
    print(f"\nType 'q' at any prompt to quit.\n")
    print(render_board(game.serialize()))

    while game.status == "playing":
        idx    = game.current_player
        player = game.players[idx]
        state  = game.serialize()

        if state["must_move_again"]:
            opponent = game.players[1 - idx]
            print(f"\n  You are on top of {opponent['name']}! Move again — where to next?")
            do_move(game, idx)
        else:
            print(f"\n{player['name']} ({marker_for(idx)})'s turn — "
                  f"{player['fences_remaining']} fence(s) remaining.")
            print("  1. Move   2. Place fence   q. Quit")

            action_done = False
            while not action_done:
                choice = input("  > ").strip().lower()
                if choice in ('q', 'quit', 'exit'):
                    raise SystemExit("Player quit.")
                if choice == '1':
                    action_done = do_move(game, idx)
                elif choice == '2':
                    action_done = do_fence(game, idx)
                else:
                    print("  Enter 1 to move or 2 to place a fence.")

        print()
        print(render_board(game.serialize()))

    print(f"\nCONGRATULATIONS {game.winner}, you have won Quoridor!\n")


if __name__ == "__main__":
    main()
