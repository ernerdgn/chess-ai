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

    app_state = "menu"
    player_two_is_human = True # by default, can be changed from menu
    menu_buttons = ()
    game_over_button = ()
    game_over_text = ""


    while running:
        turn = 'w' if gs.white_to_move else 'b'

        # event handling
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            if app_state == "menu":
                if e.type == p.MOUSEBUTTONDOWN:
                    location = p.mouse.get_pos()
                    if menu_buttons[0].collidepoint(location):
                        player_two_is_human = True
                        app_state = "playing"
                    elif menu_buttons[1].collidepoint(location):
                        player_two_is_human = False
                        app_state = "playing"
            
            elif app_state == "game_over":
                if e.type == p.MOUSEBUTTONDOWN:
                    location = p.mouse.get_pos()
                    if game_over_button.collidepoint(location):
                        gs = engine.GameState()
                        valid_moves = gs.get_legal_moves()
                        sq_selected = ()
                        player_clicks = []
                        game_over = False
                        promotion_pending = False
                        pending_move = None
                        app_state = "menu"
            
            elif app_state == "playing":
                if e.type == p.MOUSEBUTTONDOWN and promotion_pending:
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
                #
                elif e.type == p.KEYDOWN:
                    if e.key == p.K_u:
                        gs.undo_move()
                        move_made = True
                        game_over = False
                        promotion_pending = False
                        pending_move = None
                        game_over_text = ""
                        app_state = "playing"

        
        if app_state == "playing":
            if move_made:
                valid_moves = gs.get_legal_moves()
                move_made = False
            if not game_over:
                if len(valid_moves) == 0 and not promotion_pending:
                    game_over = True
                    game_over_text = "stalemate" if not gs.in_check() else "checkmate"

                elif gs.position_history.get(gs.get_game_state_hash, 0) >= 3:
                    game_over = True
                    print("draw by threefold repetition")
                
                elif gs.fifty_move_counter >= 100: # a play for each side counts as one move
                    game_over = True
                    print("drawn by fifty-move rule")

                elif gs.check_insufficient_material():
                    game_over = True
                    print("draw by insufficient material")
                
                if game_over:
                    print(game_over_text) # console log
                    app_state = "game_over"
            
        if app_state == "menu":
            menu_buttons = draw_menu(screen)
        elif app_state == "game_over":
            game_over_button = draw_game_over(screen, game_over_text)
        elif app_state == "playing":
            draw_game_state(screen, gs,valid_moves, sq_selected)
            if promotion_pending:
                promotion_clicks = draw_promotion_menu(screen, turn)
            
        clock.tick(MAX_FPS)
        p.display.flip()

def draw_game_state(screen, gs, valid_moves, sq_selected):
    draw_board(screen)
    draw_check_highlight(screen, gs)
    highlight_squares(screen, gs, valid_moves, sq_selected)
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

def highlight_squares(screen, gs, valid_moves, sq_selected):
    if sq_selected != ():
        r, c = sq_selected

        piece = gs.board[r][c]
        if piece is not None and piece.color == ('w' if gs.white_to_move else 'b'):
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('blue'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))

            s.fill(p.Color('yellow'))
            for move in valid_moves:
                if move.start_row == r and move.start_col == c:
                    screen.blit(s, (move.end_col * SQ_SIZE, move.end_row * SQ_SIZE))

def draw_check_highlight(screen, gs):
    if gs.in_check():
        color = 'w' if gs.white_to_move else 'b'
        king_pos = gs.find_king(color)

        if king_pos:
            r, c = king_pos
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(150)
            s.fill(p.Color('red'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))

def draw_menu(screen):
    screen.fill(p.Color("black"))
    font = p.font.SysFont("Arial", 32, bold=True, italic=False)

    # tit(s)le
    text = font.render("chASS", 1, p.Color("white"))
    text_react = text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
    screen.blit(text, text_react)

    # play w/human
    pvp_rect = p.Rect((WIDTH // 4), (HEIGHT // 2), (WIDTH // 2), 50)
    p.draw.rect(screen, p.Color("grey"), pvp_rect)
    text = font.render("PvP", 1, p.Color("black"))
    text_rect = text.get_rect(center=pvp_rect.center)
    screen.blit(text, text_rect)

    # play /w ai
    pvai_rect = p.Rect((WIDTH // 4), (HEIGHT // 2) + 70, (WIDTH // 2), 50)
    p.draw.rect(screen, p.Color("gray"), pvai_rect)
    text = font.render("PvAI", 1, p.Color("black"))
    text_rect = text.get_rect(center=pvai_rect.center)
    screen.blit(text, text_rect)

    return pvp_rect, pvai_rect

def draw_game_over(screen, text):
    menu_rect = p.Rect(0, 0, 400, 200)
    menu_rect.center = (WIDTH // 2, HEIGHT // 2)
    p.draw.rect(screen, p.Color("black"), menu_rect)
    p.draw.rect(screen, p.Color("white"), menu_rect.inflate(4, 4), 2)

    font = p.font.SysFont("Arial", 32, True, False)

    # gameOver
    text_obj = font.render(text, 1, p.Color("white"))
    text_rect = text_obj.get_rect(center=(menu_rect.centerx, menu_rect.centery - 50))
    screen.blit(text_obj, text_rect)

    # hit me baby one more time
    play_again_rect = p.Rect(0, 0, 200, 50)
    play_again_rect.center = (menu_rect.centerx, menu_rect.centery + 40)
    p.draw.rect(screen, p.Color("gray"), play_again_rect)
    text_obj = font.render("again?", 1, p.Color("black"))
    text_rect = text_obj.get_rect(center=play_again_rect.center)
    screen.blit(text_obj, text_rect)

    return play_again_rect

if __name__ == "__main__":
    main()