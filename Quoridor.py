try:
    %run "Quoridor_objects.py"
except Exception as e:
    print(f"Notebook 2 stopped execution: {e}")
    clear_output()

game = Quoridor()
game.game_setup()
