import engine
import random

piece_scores = {
    "K": 0,
    "Q": 9,
    "R": 5,
    "B": 3,
    "N": 3,
    "p": 1
}

def score_material(game_state):
    score = 0
    for r in range(8):
        for c in range(8):
            piece = game_state.board[r][c]
            if piece is not None:
                if piece.color == 'w':
                    score += piece_scores[piece.type]
                elif piece.color == 'b':
                    score -= piece_scores[piece.type]
    return score

def find_best_move(game_state):
    valid_moves = game_state.get_legal_moves()

    if not valid_moves:
        return None
    
    random.shuffle(valid_moves)
    best_move = None

    # minmax depth 1
    if game_state.white_to_move: # white wants to maximize
        best_score = -float('inf')
        for move in valid_moves:
            game_state.make_move(move)
            score = score_material(game_state)
            if score > best_score:
                best_score = score
                best_move = move
            game_state.undo_move()
    else: # black wants to minimize
        best_score = float('inf')
        for move in valid_moves:
            game_state.make_move(move)
            score = score_material(game_state)
            if score < best_score:
                best_score = score
                best_move = move
            game_state.undo_move()
    return best_move

def find_random_move(game_state):
    valid_moves = game_state.get_legal_moves()

    if not valid_moves:
        return None
    
    random_index = random.randint(0, len(valid_moves) - 1)
    return valid_moves[random_index]