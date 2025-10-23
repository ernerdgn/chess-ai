import engine
import random
import piece_square_tables as pst # pst pst pst meow

SEARCH_DEPTH = 3 # can be set to 4 after pruning
best_move_found = None

# def score_material(game_state):
#     score = 0
#     for r in range(8):
#         for c in range(8):
#             piece = game_state.board[r][c]
#             if piece is not None:
#                 if piece.color == 'w':
#                     score += pst.piece_scores[piece.type]
#                 elif piece.color == 'b':
#                     score -= pst.piece_scores[piece.type]
#     return score

def evaluate_board(game_state):
    score = 0
    for r in range(8):
        for c in range(8):
            piece = game_state.board[r][c]
            if piece is not None:
                # piece scores
                if piece.color == 'w':
                    score += pst.piece_scores[piece.type]
                elif piece.color == 'b':
                    score -= pst.piece_scores[piece.type]
                
                # positional scores
                table = pst.piece_position_scores[piece.type]
                if piece.color == 'w':
                    score += table[r][c] / 100.0
                elif piece.color == 'b': # flip the table for black
                    score -= table[7-r][c] / 100.0
    return score


def find_best_move(game_state):
    global best_move_found
    best_move_found = None
    random.seed()

    minimax_pruning(game_state, SEARCH_DEPTH, -float('inf'), float('inf'), game_state.white_to_move)

    return best_move_found

def minimax_pruning(game_state, depth, alpha, beta, is_maximizing_player):
    global best_move_found

    if depth == 0:
        return evaluate_board(game_state)
    
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

            if score >= best_score:
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
            
            if score <= best_score:
                best_score = score
                if depth == SEARCH_DEPTH:
                    best_move_found = move
            # pruning
            beta = min(beta, best_score)
            if beta <= alpha:
                break
        return best_score