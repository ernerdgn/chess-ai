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

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.KEYDOWN:
                if e.key == p.K_u:
                    gs.undo_move()
                    move_made = True
                    # game_over = False # reset
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

                    if len(player_clicks) == 2:
                        move = engine.Move(player_clicks[0], player_clicks[1], gs.board)
                        #print("two clicks")
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:

                                print("=====before making move")
                                for c_idx in range(8):
                                    pawn = gs.board[6][c_idx]
                                    if pawn is not None and pawn.type == 'p':
                                        print(f"Pawn at (6,{c_idx}) has_moved: {pawn.has_moved} (ID: {id(pawn)})")
                                
                                gs.make_move(valid_moves[i])  # make move

                                print("=====after making move")
                                for c_idx in range(8):
                                    pawn = gs.board[6][c_idx]
                                    if pawn is not None and pawn.type == 'p':
                                        print(f"Pawn at (6,{c_idx}) has_moved: {pawn.has_moved} (ID: {id(pawn)})")

                                print(move.get_chess_notation())
                                move_made = True
                                sq_selected = () # reset clicks
                                player_clicks = []
                                break
                        if not move_made:
                            player_clicks = [sq_selected]
        if move_made:
            valid_moves = gs.get_legal_moves()
            move_made = False

        draw_game_state(screen, gs)

        if len(valid_moves) == 0:
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


if __name__ == "__main__":
    main()