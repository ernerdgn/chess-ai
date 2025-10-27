import random
import torch
import torch.nn as nn
import piece_square_tables as pst # pst pst pst meow

# model arch
class ChessCNN(nn.Module):
    def __init__(self):
        super(ChessCNN, self).__init__()
        self.conv1 = nn.Conv2d(12, 32, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(32)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(64)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm2d(128)
        self.flatten = nn.Flatten()
        self.fc1 = nn.Linear(128 * 8 * 8, 512)
        self.dropout = nn.Dropout(0.5)
        self.fc2 = nn.Linear(512, 1)
        self.relu = nn.ReLU()
        self.tanh = nn.Tanh()

    def forward(self, x):
        x = self.relu(self.bn1(self.conv1(x)))
        x = self.relu(self.bn2(self.conv2(x)))
        x = self.relu(self.bn3(self.conv3(x)))
        x = self.flatten(x)
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        x = self.tanh(x)
        return x

MODEL_PATH = "sf_chess_model.pth"

# set device cpu if cuda is not available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"loading model onto device: {device}")

model = ChessCNN().to(device)
try:
    model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
    print("model loaded!")
except Exception as e:
    print(f"ERROR loading model: {e}")
    print("model does not loaded")
    model = None

if model:
    model.eval()

def vectorize_board(game_state):
    board_tensor = torch.zeros(1, 12, 8, 8, dtype=torch.float32)

    for r in range(8):
        for c in range(8):
            piece = game_state.board[r][c]
            if piece is not None:
                # channel index
                channel = pst.piece_map[piece.type]
                if piece.color == 'b':
                    channel += 6

                board_tensor[0, channel, r, c] = 1.0
    return board_tensor

def evaluate_board_ML(game_state):
    board_tensor = vectorize_board(game_state).to(device)
    
    with torch.no_grad():
        score_tensor = model(board_tensor)

    return score_tensor.item() * 10.0

def evaluate_board_classic(game_state):
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
                    score -= table[7-r][c] / 100.
    #score = 0
    return score

SEARCH_DEPTH = 3  # can be set to 4 after pruning
best_move_found = None

def find_best_move(game_state, opponent_type):
    global best_move_found
    best_move_found = None
    random.seed()

    # decide eval funct to use
    use_ml_eval = (opponent_type == "ai_ml") and (model is not None)

    if opponent_type == "ai_ml" and model is None:
        print("load model failed, falling back to classic eval...")
    
    #USE_ML_EVAL = (model is not None) 
    
    print(f"AI is thinking using {'ML model' if use_ml_eval else 'classic eval'}...")
    
    minimax_pruning(game_state, SEARCH_DEPTH, -float('inf'), float('inf'), game_state.white_to_move, use_ml_eval)
    
    return best_move_found

def minimax_pruning(game_state, depth, alpha, beta, is_maximizing_player, use_ml_eval):
    global best_move_found
    
    if depth == 0:
        if use_ml_eval:
            return evaluate_board_ML(game_state)
        else:
            return evaluate_board_classic(game_state)
            
    valid_moves = game_state.get_legal_moves()
    random.shuffle(valid_moves)
    
    if not valid_moves:
        if game_state.in_check():
            return float('-inf') if is_maximizing_player else float('inf')
        else:
            return 0
    
    if is_maximizing_player:
        best_score = -float('inf')
        for move in valid_moves:
            game_state.make_move(move)
            score = minimax_pruning(game_state, depth - 1, alpha, beta, False, use_ml_eval)
            game_state.undo_move()
            if score >= best_score:
                best_score = score
                if depth == SEARCH_DEPTH:
                    best_move_found = move
            alpha = max(alpha, best_score)
            if beta <= alpha:
                break
        return best_score
    else:
        best_score = float('inf')
        for move in valid_moves:
            game_state.make_move(move)
            score = minimax_pruning(game_state, depth - 1, alpha, beta, True, use_ml_eval)
            game_state.undo_move()
            if score <= best_score:
                best_score = score
                if depth == SEARCH_DEPTH:
                    best_move_found = move
            beta = min(beta, best_score)
            if beta <= alpha:
                break
        return best_score