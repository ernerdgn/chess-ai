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
        # self.board = [
        #     [Piece("b", "R"),None,None, None, Piece("b", "K"), None,None,Piece("b", "R")],
        #     [None, None, None, None, None, None, None, None],            [None, None, None, None, None, None, None, None],
        #     [None, None, None, None, None, None, None, None],
        #     [None, None, None, None, None, None, None, None],
        #     [None, None, None, None, None, None, None, None],
        #     [None, None, None, None, None, None, None, None],
        #     [Piece("w", "R"),None,None, None, Piece("w", "K"), None,None,Piece("w", "R")]
        # ]

        self.white_to_move = True
        self.move_log = []
        # self.white_king_location = (7, 4)
        # self.black_king_location = (0, 4)

        self.castle_rights = CastleRights(True, True, True, True)
        self.castle_rights_log = [self.castle_rights.copy()]

        self.en_passant_target = None # (r,c) of target square
        self.en_passant_log = [self.en_passant_target]

        self.fifty_move_counter = 0
        self.fifty_move_log = [0]

        self.position_history = {}

        self.position_history[self.get_game_state_hash()] = 1

    def get_game_state_hash(self):
        board_string = ""
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece is None:
                    board_string += "--"
                else:
                    board_string += piece.color + piece.type
        return (
            board_string,
            self.white_to_move,
            self.castle_rights.wks, self.castle_rights.wqs,
            self.castle_rights.bks, self.castle_rights.bqs,
            self.en_passant_target
        )

    def make_move(self, move):  # no castle, promo, en pass
        self.board[move.start_row][move.start_col] = None

        if move.promotion_choice is not None:
            promo_piece = Piece(move.piece_moved.color, move.promotion_choice)
            self.board[move.end_row][move.end_col] = promo_piece
        else:
            self.board[move.end_row][move.end_col] = move.piece_moved

        self.move_log.append(move)
        self.white_to_move = not self.white_to_move
        
        move.piece_moved.has_moved = True

        # en passant
        if move.is_en_passant: # capture
            self.board[move.start_row][move.end_col] = None

        if move.piece_moved.type == 'p' and abs(move.start_row - move.end_row) == 2:
            self.en_passant_target = ((move.start_row + move.end_row) // 2, move.start_col)
        else:
            self.en_passant_target = None

        self.en_passant_log.append(self.en_passant_target)

        # fifty-move rule
        # no pawn plays or no captures in 50 move
        if move.piece_moved.type == 'p' or move.piece_captured is not None:
            self.fifty_move_counter = 0
        else:
            self.fifty_move_counter += 1
        self.fifty_move_log.append(self.fifty_move_counter)

        # castling
        if move.is_castle_move:
            if move.end_col - move.start_col == 2:
                rook = self.board[move.start_row][7]
                self.board[move.start_row][7] = None
                self.board[move.start_row][5] = rook
                rook.has_moved = True
            else:
                rook = self.board[move.start_row][0]
                self.board[move.start_row][0] = None
                self.board[move.start_row][3] = rook
                rook.has_moved = True
        self.update_castle_rights(move)
        self.castle_rights_log.append(self.castle_rights.copy())

        new_hash = self.get_game_state_hash()
        self.position_history[new_hash] = self.position_history.get(new_hash, 0) + 1

    def undo_move(self):
        if len(self.move_log) != 0: # is there any moves
            current_hash = self.get_game_state_hash()
            if current_hash in self.position_history:
                self.position_history[current_hash] -= 1
            
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_to_move = not self.white_to_move

            if move.was_first_move:
                move.piece_moved.has_moved = False

            # en passant
            self.en_passant_log.pop()
            self.en_passant_target = self.en_passant_log[-1]

            if move.is_en_passant:
                self.board[move.end_row][move.end_col] = None
                self.board[move.start_row][move.end_col] = move.piece_captured

            # fifty-move rule
            self.fifty_move_log.pop()
            self.fifty_move_counter = self.fifty_move_log[-1]

            # castling
            self.castle_rights_log.pop()
            self.castle_rights = self.castle_rights_log[-1].copy()

            if move.is_castle_move:
                if move.end_col - move.start_col == 2: # kingside
                    rook = self.board[move.start_row][5]
                    self.board[move.start_row][7] = rook
                    self.board[move.start_row][5] = None
                    rook.has_moved = False
                else: # queenside
                    rook = self.board[move.start_row][3]
                    self.board[move.start_row][0] = rook
                    self.board[move.start_row][3] = None
                    rook.has_moved = False

    def get_all_psuedo_legal_moves(self):
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
        moves = self.get_all_psuedo_legal_moves()

        if not self.in_check():
            king_pos = self.find_king('w') if self.white_to_move else self.find_king('b')
            if king_pos:
                self.get_castle_moves(king_pos[0], king_pos[1], moves)

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
        opp_moves = self.get_all_psuedo_legal_moves()
        self.white_to_move = not self.white_to_move
        for move in opp_moves:
            if move.end_row == r and move.end_col == c:
                return True
        return False
    
    def update_castle_rights(self, move):
        if move.piece_moved.type == 'K': # king moves
            if move.piece_moved.color == 'w': # white
                self.castle_rights.wks = False
                self.castle_rights.wqs = False
            else: # black
                self.castle_rights.bks = False
                self.castle_rights.bqs = False
        elif move.piece_moved.type == 'R': # rook moves
            if move.piece_moved.color == 'w': # white
                if move.start_row == 7:
                    if move.start_col == 0: # a1 rook
                        self.castle_rights.wqs = False
                    elif move.start_col == 7: # h1 rook
                        self.castle_rights.wks = False
            else: # black
                if move.start_row == 0:
                    if move.start_col == 0: # a8 rook
                        self.castle_rights.bqs = False
                    elif move.start_col == 7: # h8 rook
                        self.castle_rights.bks = False
        
        # check if the rook is captured
        if move.piece_captured is not None and move.piece_captured.type == 'r':
            if move.end_row == 7: # white
                if move.end_col == 0: # a1 rook captured
                    self.castle_rights.wqs = False
                elif move.end_col == 7: # h1 rook captured
                    self.castle_rights.wks = False
            elif move.end_col == 0: # black
                if move.end_col == 0: # a8 rook captured
                    self.castle_rights.bqs = False
                elif move.end_col == 7: # h8 rook captured
                    self.castle_rights.bks = False

    def get_pawn_moves(self, r, c, moves):
        piece = self.board[r][c]
        
        if self.white_to_move: # white pawns
            if self.board[r-1][c] is None:
                if r-1 == 0: # promotion
                    for p_type in ['Q', 'R', 'B', 'N']:
                        moves.append(Move((r, c), (r-1, c), self.board, promotion_choice=p_type))
                else: # 1-square
                    moves.append(Move((r, c), (r-1, c), self.board))
                if r == 6 and not piece.has_moved and self.board[r-2][c] is None: # 2-square
                    moves.append(Move((r, c), (r-2, c), self.board))
            
            # capture
            if c-1 >= 0: # capture left
                target_sq = (r-1, c-1)
                if self.board[r-1][c-1] is not None and self.board[r-1][c-1].color == 'b':
                    if r-1 == 0: # capture promotion
                        for p_type in ['Q', 'R', 'B', 'N']:
                            moves.append(Move((r, c), target_sq, self.board, promotion_choice=p_type))
                    else: # regular capture
                        moves.append(Move((r, c), target_sq, self.board))
                elif target_sq == self.en_passant_target:
                    moves.append(Move((r, c), target_sq, self.board, is_en_passant=True))
            
            if c+1 <= 7: # capture right
                target_sq = (r-1, c+1)
                if self.board[r-1][c+1] is not None and self.board[r-1][c+1].color == 'b':
                    if r-1 == 0: # capture promotion
                        for p_type in ['Q', 'R', 'B', 'N']:
                            moves.append(Move((r, c), target_sq, self.board, promotion_choice=p_type))
                    else: # regular capture
                        moves.append(Move((r, c), target_sq, self.board))
                elif target_sq == self.en_passant_target:
                    moves.append(Move((r, c), target_sq, self.board, is_en_passant=True))

        else: # black pawns (no to racism)
            if self.board[r+1][c] is None:
                if r+1 == 7: # promotion
                    for p_type in ['Q', 'R', 'B', 'N']:
                        moves.append(Move((r, c), (r+1, c), self.board, promotion_choice=p_type))
                else: # 1-square
                    moves.append(Move((r, c), (r+1, c), self.board))
                if r == 1 and not piece.has_moved and self.board[r+2][c] is None: # 2-square
                    moves.append(Move((r, c), (r+2, c), self.board))
            
            # captures
            if c-1 >= 0: # capture left
                target_sq = (r+1, c-1)
                if self.board[r+1][c-1] is not None and self.board[r+1][c-1].color == 'w':
                    if r+1 == 7: # capture promotion
                        for p_type in ['Q', 'R', 'B', 'N']:
                            moves.append(Move((r, c), target_sq, self.board, promotion_choice=p_type))
                    else: # regular capture
                        moves.append(Move((r, c), target_sq, self.board))
                elif target_sq == self.en_passant_target:
                    moves.append(Move((r, c), target_sq, self.board, is_en_passant=True))
            
            if c+1 <= 7: # capture right
                target_sq = (r+1, c+1)
                if self.board[r+1][c+1] is not None and self.board[r+1][c+1].color == 'w':
                    if r+1 == 7: # capture promotion
                        for p_type in ['Q', 'R', 'B', 'N']:
                            moves.append(Move((r, c), target_sq, self.board, promotion_choice=p_type))
                    else: # regular capture
                        moves.append(Move((r, c), target_sq, self.board))
                elif target_sq == self.en_passant_target:
                    moves.append(Move((r, c), target_sq, self.board, is_en_passant=True))

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
        
        # self.get_castle_moves(r, c, moves)

    def get_castle_moves(self, r, c, moves):
        # if self.in_check():
        #     return # cant castle in check
        
        if (self.white_to_move and self.castle_rights.wks) or (not self.white_to_move and self.castle_rights.bks):
            self.get_kingside_castle_moves(r, c, moves)
        if (self.white_to_move and self.castle_rights.wks) or (not self.white_to_move and self.castle_rights.bks):
            self.get_queenside_castle_moves(r, c, moves)

    def get_kingside_castle_moves(self, r, c, moves):
        if self.board[r][c+1] is None and self.board[r][c+2] is None:
            if not self.square_under_attack(r, c+1) and not self.square_under_attack(r, c+2):
                moves.append(Move((r, c), (r, c+2), self.board, is_castle=True))

    def get_queenside_castle_moves(self, r, c, moves):
        if self.board[r][c-1] is None and self.board[r][c-2] is None and self.board[r][c-3] is None:
            if not self.square_under_attack(r, c-1) and not self.square_under_attack(r, c-2):
                moves.append(Move((r, c), (r, c-2), self.board, is_castle=True))

    def check_insufficient_material(self):
        w_pawns = 0
        b_pawns = 0
        w_majors = 0 # Rs and Qs
        b_majors = 0
        w_knights = 0
        b_knights = 0
        w_bishops = [] # square colors (0: light, 1: dark)
        b_bishops = []

        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece is not None:
                    if piece.type == 'p':
                        if piece.color == 'w': w_pawns += 1
                        else: b_pawns += 1
                    elif piece.type == 'R' or piece.type == 'Q':
                        if piece.color == 'w': w_majors += 1
                        else: b_majors += 1
                    elif piece.type == 'N':
                        if piece.color == 'w': w_knights += 1
                        else: b_knights += 1
                    elif piece.type == 'B':
                        square_color = (r + c) % 2
                        if piece.color == 'w': w_bishops.append(square_color)
                        else: b_bishops.append(square_color)
        
        # pawns, rooks, queens
        if w_pawns > 0 or b_pawns > 0 or w_majors > 0 or b_majors > 0:
            return False
        
        # more than one minor piece on either side
        if w_knights + len(w_bishops) > 1 or b_knights + len(b_bishops) > 1:
            return False
        
        # stalemate conditions
        # only kings
        if w_knights == 0 and len(w_bishops) == 0 and b_knights == 0 and len(b_bishops) == 0:
            return True
        
        # king(s) + (bishop or knight)
        if (w_knights == 1 or len(w_bishops) == 1) and b_knights == 0 and len(b_bishops) == 0:
            return True
        if (b_knights == 1 or len(b_bishops) == 1) and w_knights == 0 and len(w_bishops) == 0:
            return True
        
        # king(s) + same colored bishops
        if len(w_bishops) == 1 and len(b_bishops) == 1:
            if w_bishops[0] == b_bishops[0]: # check bishop colors
                return True
        
        return False

class Piece():
    def __init__(self, color, type):
        self.color = color
        self.type = type
        self.has_moved = False

class CastleRights():
    def __init__(self, wks, wqs, bks, bqs):
        self.wks = wks  # white king side
        self.wqs = wqs  # white queen side
        self.bks = bks  # black king side
        self.bqs = bqs  # black queen side
    
    def copy(self):
        return CastleRights(self.wks, self.wqs, self.bks, self.bqs)

class Move():
    def __init__(self, start_sq, end_sq, board, is_castle=False, is_en_passant=False, promotion_choice=None):
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]

        self.is_en_passant = is_en_passant
        if is_en_passant:
            self.piece_captured = board[self.start_row][self.end_col]
        else:
            self.piece_captured = board[self.end_row][self.end_col]

        self.was_first_move = False # by default
        if self.piece_moved is not None: # NoneType protection
            self.was_first_move = not self.piece_moved.has_moved

        self.is_castle_move = is_castle

        # promotion
        self.promotion_choice = promotion_choice
        # self.is_promotion = False
        # if self.piece_moved is not None and self.piece_moved.type == 'p':
        #     if (self.piece_moved.color == 'w' and self.end_row == 0) or \
        #         (self.piece_moved.color == 'b' and self.end_row == 7):
        #         self.is_promotion = True
        # self.promotion_choice = None

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.start_row == other.start_row and self.start_col == other.start_col and \
                    self.end_row == other.end_row and self.end_col == other.end_col and \
                    self.promotion_choice == other.promotion_choice
        return False
    
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                     "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3,
                     "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def get_chess_notation(self):
        return self.piece_moved.type + self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)

    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]