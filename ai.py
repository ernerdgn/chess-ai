import engine
import random

def find_random_move(game_state):
    valid_moves = game_state.get_legal_moves()

    if not valid_moves:
        return None
    
    random_index = random.randint(0, len(valid_moves) - 1)
    return valid_moves[random_index]