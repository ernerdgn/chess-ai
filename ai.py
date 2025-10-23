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

SEARCH_DEPTH = 3 # can be set to 4 after pruning
best_move_found = None

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

# def find_best_move(game_state):
#     valid_moves = game_state.get_legal_moves()

#     if not valid_moves:
#         return None

#     random.shuffle(valid_moves)
#     best_move = None

#     best_score = float('inf')

#     for move in valid_moves:
#         game_state.make_move(move)

#         score = minimax(game_state, SEARCH_DEPTH - 1, True)

#         game_state.undo_move()

#         if score < best_score:
#             best_score = score
#             best_move = move

#     return best_move

def find_best_move(game_state):
    global best_move_found
    best_move_found = None
    random.seed()

    minimax_pruning(game_state, SEARCH_DEPTH, -float('inf'), float('inf'), game_state.white_to_move)

    return best_move_found

def minimax_pruning(game_state, depth, alpha, beta, is_maximizing_player):
    global best_move_found

    if depth == 0:
        return score_material(game_state)
    
    valid_moves = game_state.get_legal_moves()
    random.shuffle(valid_moves)

    if not valid_moves:
        if game_state.in_check(): # checkmate is best move
            return float('-inf') if is_maximizing_player else float('inf')
        else: # stalemate
            return 0
    
    # recursive
    if is_maximizing_player: # white
        best_score = -float('inf')
        for move in valid_moves:
            game_state.make_move(move)
            score = minimax_pruning(game_state, depth - 1, alpha, beta, False)
            game_state.undo_move()

            if score > best_score:
                best_score = score
                if depth == SEARCH_DEPTH:
                    best_move_found = move
            # pruning
            alpha = max(alpha, best_score)
            if beta <= alpha:
                break
        return best_score
    
    else: # black
        best_score = float('inf')
        for move in valid_moves:
            game_state.make_move(move)
            score = minimax_pruning(game_state, depth - 1, alpha, beta, True)
            game_state.undo_move()
            
            if score < best_score:
                best_score = score
                if depth == SEARCH_DEPTH:
                    best_move_found = move
            # pruning
            beta = min(beta, best_score)
            if beta <= alpha:
                break
        return best_score





# def minimax(game_state, depth, is_maximizing_player):
#     if depth == 0:
#         return score_material(game_state)
    
#     valid_moves = game_state.get_legal_moves()

#     if not valid_moves:
#         if game_state.in_check(): # checkmate is best move
#             return float('-inf') if is_maximizing_player else float('inf')
#         else: # stalemate
#             return 0
        
#     # recursive
#     if is_maximizing_player: # white
#         best_score = -float('inf')
#         for move in valid_moves:
#             game_state.make_move(move)
#             score = minimax(game_state, depth - 1, False)
#             game_state.undo_move()
#             best_score = max(best_score, score)
#         return best_score
#     else: # black
#         best_score = float('inf')
#         for move in valid_moves:
#             game_state.make_move(move)
#             score = minimax(game_state, depth - 1, True)
#             game_state.undo_move()
#             best_score = min(best_score, score)
#         return best_score

# def find_random_move(game_state):
#     valid_moves = game_state.get_legal_moves()

#     if not valid_moves:
#         return None
    
#     random_index = random.randint(0, len(valid_moves) - 1)
#     return valid_moves[random_index]