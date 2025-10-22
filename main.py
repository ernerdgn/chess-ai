import pygame as p
import engine

#consts
WIDTH = 512
HEIGHT = 512
DIMENSION = 8
MAX_FPS = 15
SQ_SIZE = HEIGHT // DIMENSION
IMAGES = {}

def load_images():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))

    gs = engine.GameState()
    valid_moves = gs.get_legal_moves()
    move_made = False

    load_images()

    running = True
    sq_selected = ()
    player_clicks = []
    game_over = False

    promotion_pending = False
    pending_move = None
    promotion_clicks = []

    while running:
        turn = 'w' if gs.white_to_move else 'b'

        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            
            elif e.type == p.MOUSEBUTTONDOWN and promotion_pending:
                location = p.mouse.get_pos()
                for i, rect in enumerate(promotion_clicks):
                    if rect.collidepoint(location):
                        choice = ['Q', 'R', 'B', 'N'][i]
                        pending_move.promotion_choice = choice
                        gs.make_move(pending_move)
                        print(f"promoted to  {choice}")

                        promotion_pending = False
                        pending_move = None
                        move_made = True
                        sq_selected = ()
                        promotion_clicks = []
                        break

            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over:
                    location = p.mouse.get_pos()  #(x,y)
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sq_selected == (row, col):
                        sq_selected = ()
                        player_clicks = []
                    else:
                        sq_selected = (row, col)
                        player_clicks.append(sq_selected)

                    if len(player_clicks) == 1:
                        if gs.board[row][col] is None:  #if clicked to an empty square
                            sq_selected = ()
                            player_clicks = []

                    if len(player_clicks) == 2:
                        start_piece = gs.board[player_clicks[0][0]][player_clicks[0][1]]

                        if start_piece is not None:
                            move = engine.Move(player_clicks[0], player_clicks[1], gs.board)
                            for i in range(len(valid_moves)):
                                if move == valid_moves[i]:
                                    if move.is_promotion: # check for promotion
                                        promotion_pending = True
                                        pending_move = move
                                    else:
                                        gs.make_move(valid_moves[i])
                                        print(move.get_chess_notation())
                                        move_made = True
                                    
                                    sq_selected = ()
                                    player_clicks = []
                                    break
                            
                            if not move_made and not promotion_pending:
                                end_piece = gs.board[player_clicks[1][0]][player_clicks[1][1]]
                                if end_piece is not None and end_piece.color == start_piece.color:
                                    sq_selected = player_clicks[1]
                                    player_clicks = [sq_selected]
                                else:
                                    sq_selected = ()
                                    player_clicks = []
                        else:
                            sq_selected = ()
                            player_clicks = []

            elif e.type == p.KEYDOWN:
                if e.key == p.K_u:
                    gs.undo_move()
                    move_made = True
                    # game_over = False # reset
                    promotion_pending = False
                    pending_move = None

        if move_made:
            valid_moves = gs.get_legal_moves()
            move_made = False

        draw_game_state(screen, gs)

        if promotion_pending:
            promotion_clicks = draw_promotion_menu(screen, turn)

        if len(valid_moves) == 0 and not promotion_pending:
            game_over = True
            if gs.in_check():
                print("checkmate")
                running = False
            else:
                print("stalemate")
                running = False

        clock.tick(MAX_FPS)
        p.display.flip()

def draw_game_state(screen, gs):
    draw_board(screen)
    draw_pieces(screen, gs.board)

def draw_board(screen):
    colors = [p.Color("white"), p.Color("grey")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def draw_pieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece is not None:
                image_name = piece.color + piece.type
                screen.blit(IMAGES[image_name], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def draw_promotion_menu(screen, turn):
    menu_x = (WIDTH // 2) - (2 * SQ_SIZE)
    menu_y = (HEIGHT // 2) - (SQ_SIZE // 2)
    menu_rect = p.Rect(menu_x, menu_y, 4 * SQ_SIZE, SQ_SIZE)
    p.draw.rect(screen, p.Color("black"), menu_rect)
    p.draw.rect(screen, p.Color("white"), menu_rect.inflate(4,4), 2)

    pieces = ['Q', 'R', 'B', 'N']
    for i, piece in enumerate(pieces):
        image_name = turn + piece
        screen.blit(IMAGES[image_name], menu_rect.move(i * SQ_SIZE, 0))
    
    clicks = []
    for i in range(4):
        clicks.append(p.Rect(menu_x + (i * SQ_SIZE), menu_y, SQ_SIZE, SQ_SIZE))
    return clicks

if __name__ == "__main__":
    main()