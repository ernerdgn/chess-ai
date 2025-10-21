#

# WIDTH = 512
# HEIGHT = 512
# DIMENSION = 8
# MAX_FPS = 15
# SQ_SIZE = HEIGHT // DIMENSION
# IMAGES = {}

class GameState():
    def __init__(self):
        self.board = [
            [Piece("b", "R"), Piece("b", "N"), Piece("b", "B"), Piece("b", "Q"), Piece("b", "K"), Piece("b", "B"), Piece("b", "N"), Piece("b", "R")],
            [Piece("b", "p"), Piece("b", "p"), Piece("b", "p"), Piece("b", "p"), Piece("b", "p"), Piece("b", "p"), Piece("b", "p"), Piece("b", "p")],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [Piece("w", "p"), Piece("w", "p"), Piece("w", "p"), Piece("w", "p"), Piece("w", "p"), Piece("w", "p"), Piece("w", "p"), Piece("w", "p")],
            [Piece("w", "R"), Piece("w", "N"), Piece("w", "B"), Piece("w", "Q"), Piece("w", "K"), Piece("w", "B"), Piece("w", "N"), Piece("w", "R")]
        ]

        self.white_to_move = True
        self.move_log = []
        # self.white_king_location = (7, 4)
        # self.black_king_location = (0, 4)

    def make_move(self, move):  # no castle, promo, en pass
        self.board[move.start_row][move.start_col] = None
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)
        self.white_to_move = not self.white_to_move
        
        move.piece_moved.has_moved = True

    def undo_move(self):
        if len(self.move_log) != 0: # is there any moves
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_to_move = not self.white_to_move
            # if move.piece_moved == "wK":
            #     self.white_king_location = (move.start_row, move.start_col)
            # elif move.piece_moved == "bK":  #burgerking
            #     self.black_king_location = (move.start_row, move.start_col)
            if move.was_first_move:
                move.piece_moved.has_moved = False

    def get_all_possible_moves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                piece = self.board[r][c]
                # turn = self.board[r][c][0] # w/b
                if piece is not None:
                    if (piece.color == 'w' and self.white_to_move) or (piece.color == 'b' and not self.white_to_move):
                        if piece.type == 'p':
                            self.get_pawn_moves(r, c, moves)
                        elif piece.type == 'R':
                            self.get_rook_moves(r, c, moves)
                        elif piece.type == 'B':
                            self.get_bishop_moves(r, c, moves)
                        elif piece.type == 'N':
                            self.get_knight_moves(r, c, moves)
                        elif piece.type == 'Q':
                            self.get_queen_moves(r, c, moves)
                        elif piece.type == 'K':
                            self.get_king_moves(r, c, moves)
        # print("getAllPosMoves ", moves)
        return moves
    
    def get_legal_moves(self):
        moves = self.get_all_possible_moves()
        for i in range(len(moves) -1, -1, -1):
            self.make_move(moves[i])
            self.white_to_move = not self.white_to_move
            if self.in_check():
                moves.remove(moves[i])
            self.white_to_move = not self.white_to_move
            self.undo_move()
        #print("legal moves count: ", len(moves))  # should be 20 at the start
        return moves
    
    def find_king(self, color):
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece is not None and piece.type == 'K' and piece.color == color:
                    return (r, c)
        return None # if there's no king on the board... if happens,

    def in_check(self):
        if self.white_to_move:
            king_pos = self.find_king('w')
        else:
            king_pos = self.find_king('b')
        return self.square_under_attack(king_pos[0], king_pos[1])

    def square_under_attack(self, r, c):
        self.white_to_move = not self.white_to_move
        opp_moves = self.get_all_possible_moves()
        self.white_to_move = not self.white_to_move
        for move in opp_moves:
            if move.end_row == r and move.end_col == c:
                return True
        return False

    def get_pawn_moves(self, r, c, moves):
        piece = self.board[r][c]

        if self.white_to_move: # white
            if self.board[r-1][c] is None: # 1-square
                moves.append(Move((r, c), (r-1, c), self.board))
                if r == 6 and self.board[r-2][c] is None: # 2-square
                    if not piece.has_moved:
                        moves.append(Move((r, c), (r-2, c), self.board))
                    else:
                        print(f"2-sq move for pawn at ({r},{c}) REJECTED. Piece ID: {id(piece)}, has_moved: {piece.has_moved}")
            # capture
            if c-1 >= 0: # left
                if self.board[r-1][c-1] is not None and self.board[r-1][c-1].color == 'b':
                    moves.append(Move((r, c), (r-1, c-1), self.board))
            if c+1 <= 7: # right
                if self.board[r-1][c+1] is not None and self.board[r-1][c+1].color == 'b':
                    moves.append(Move((r, c), (r-1, c+1), self.board))

        else: # black pawn (no to racism)
            if self.board[r+1][c] is None: # 1-square
                moves.append(Move((r, c), (r+1, c), self.board))
                if r == 1 and not piece.has_moved and self.board[r+2][c] is None: # 2-square
                    moves.append(Move((r, c), (r+2, c), self.board))
            # capture
            if c-1 >= 0: # left
                if self.board[r+1][c-1] is not None and self.board[r+1][c-1].color == 'w':
                    moves.append(Move((r, c), (r+1, c-1), self.board))
            if c+1 <= 7: # right
                if self.board[r+1][c+1] is not None and self.board[r+1][c+1].color == 'w':
                    moves.append(Move((r, c), (r+1, c+1), self.board))

    def get_rook_moves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1)) #up,left,down,right
        enemy_color = "b" if self.white_to_move else "w"
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece is None:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif end_piece.color == enemy_color: # capture
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else: # teammate block
                        break
                else: # off board
                    break
    
    def get_bishop_moves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1)) # diagonals
        enemy_color = "b" if self.white_to_move else "w"
        
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece is None:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif end_piece.color == enemy_color: # capture
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else: # teammate block
                        break
                else: # off board
                    break

    def get_knight_moves(self, r, c, moves):
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)) # L shape? i dont think so...
        ally_color = "w" if self.white_to_move else "b"

        for m in knight_moves:
            end_row = r + m[0]
            end_col = c + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece is None or end_piece.color != ally_color: # empty or enemy
                    moves.append(Move((r, c), (end_row, end_col), self.board))


    def get_queen_moves(self, r, c, moves): # i like queen and its move function 
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)

    def get_king_moves(self,r , c, moves):
        king_moves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        ally_color = "w" if self.white_to_move else "b"
        
        for i in range(8):
            end_row = r + king_moves[i][0]
            end_col = c + king_moves[i][1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece is None or end_piece.color != ally_color: # empty or enemy
                    moves.append(Move((r, c), (end_row, end_col), self.board)) 

class Piece():
    def __init__(self, color, type):
        self.color = color
        self.type = type
        self.has_moved = False

class Move():
    def __init__(self, start_sq, end_sq, board):
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]

        self.was_first_move = not self.piece_moved.has_moved

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.start_row == other.start_row and self.start_col == other.start_col and \
                    self.end_row == other.end_row and self.end_col == other.end_col
        return False
    
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                     "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3,
                     "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def get_chess_notation(self):
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)

    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]