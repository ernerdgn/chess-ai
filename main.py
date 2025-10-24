import pygame as p
import engine
import ai

#consts
SIDE_PANEL_WIDTH = 256
WIDTH = 512 + SIDE_PANEL_WIDTH
HEIGHT = 512
DIMENSION = 8
MAX_FPS = 15
SQ_SIZE = HEIGHT // DIMENSION
IMAGES = {}
CAPTURED_IMAGES = {}
CAPTURED_SQ_SIZE = 24

def load_images():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
        CAPTURED_IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (CAPTURED_SQ_SIZE, CAPTURED_SQ_SIZE))

def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))

    FONT = p.font.SysFont("Arial", 32, True, False)
    SMALL_FONT = p.font.SysFont("Arial", 20, False, False)

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
    #player_two_is_human = True # by default, can be changed from menu
    opponent_type = "human"
    menu_buttons = ()
    game_over_button = ()
    game_over_text = ""
    scroll_offset_y = 0

    min_insput_strt = "5" # default time 5+3
    inc_input_str = "3"
    active_input = None
    input_boxes = {}
    turn_start_time = p.time.get_ticks()
    last_update_time = turn_start_time # for smoother display
    white_display_time = gs.white_time_left
    black_display_time = gs.black_time_left

    while running:
        turn = 'w' if gs.white_to_move else 'b'

        # event handling
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            if app_state == "menu":
                if e.type == p.MOUSEBUTTONDOWN and e.button == 1:
                    location = p.mouse.get_pos()
                    if menu_buttons[0].collidepoint(location):
                        opponent_type = "human"
                        app_state = "playing"
                        turn_start_time = p.time.get_ticks() # reset clock
                        last_update_time = turn_start_time
                        white_display_time = gs.white_time_left
                        black_display_time = gs.black_time_left
                    elif menu_buttons[1].collidepoint(location):
                        #print("ai classic selected")
                        opponent_type = "ai_classic"
                        app_state = "playing"
                        turn_start_time = p.time.get_ticks() # reset clock
                        last_update_time = turn_start_time
                        white_display_time = gs.white_time_left
                        black_display_time = gs.black_time_left
                    elif menu_buttons[2].collidepoint(location):
                        #print("ai ml selected")
                        opponent_type = "ai_ml"
                        app_state = "playing"
                        turn_start_time = p.time.get_ticks() # reset clock
                        last_update_time = turn_start_time
                        white_display_time = gs.white_time_left
                        black_display_time = gs.black_time_left
            
            elif app_state == "game_over":
                if e.type == p.MOUSEBUTTONDOWN and e.button == 1:
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
                if e.type == p.MOUSEWHEEL:
                    scroll_offset_y -= e.y * 30 # e.y-> +1 for down, -1 for up

                elif e.type == p.MOUSEBUTTONDOWN and e.button and promotion_pending:
                    location = p.mouse.get_pos()
                    for i, rect in enumerate(promotion_clicks):
                        if rect.collidepoint(location):
                            choice = ['Q', 'R', 'B', 'N'][i]

                            start_sq = (pending_move.start_row, pending_move.start_col)
                            end_sq = (pending_move.end_row, pending_move.end_col)
                            specific_move = engine.Move(
                                start_sq,
                                end_sq,
                                gs.board,
                                promotion_choice=choice)
                            
                            for vm in valid_moves:
                                if vm == specific_move:
                                    gs.make_move(vm)
                                    print(f"promoted to {choice}")
                                    break

                            promotion_pending = False
                            pending_move = None
                            move_made = True
                            sq_selected = ()
                            promotion_clicks = []
                            break

                elif e.type == p.MOUSEBUTTONDOWN and e.button == 1:
                    if not game_over:
                        location = p.mouse.get_pos()  #(x,y)
                        col = location[0] // SQ_SIZE
                        row = location[1] // SQ_SIZE
                        # check if the click inside the board
                        if 0 <= row < DIMENSION and 0 <= col < DIMENSION:
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
                                start_sq = player_clicks[0]
                                end_sq = player_clicks[1]
                                move = engine.Move(start_sq, end_sq, gs.board)
                                
                                
                                start_piece = gs.board[start_sq[0]][start_sq[1]]

                                is_promotion_click = False
                                if start_piece is not None and start_piece.type == 'p':
                                    if (start_piece.color == 'w' and end_sq[0] == 0) or \
                                        (start_piece.color == 'b' and end_sq[0] == 7):
                                        is_promotion_click = True
                                
                                if is_promotion_click:
                                    for vm in valid_moves:
                                        if vm.start_row == start_sq[0] and vm.start_col == start_sq[1] and \
                                            vm.end_row == end_sq[0] and vm.end_col == end_sq[1] and \
                                            vm.promotion_choice is not None:
                                            promotion_pending = True
                                            pending_move = move
                                            break
                                    sq_selected = ()
                                    player_clicks = []

                                else:
                                    for i in range(len(valid_moves)):
                                        if move == valid_moves[i]: # only non-promo moves
                                            gs.make_move(valid_moves[i])

                                            final_elapsed_sec = (p.time.get_ticks() - turn_start_time) / 1000.0

                                            if not gs.white_to_move:
                                                pre_increment_time = gs.white_time_log[-2]
                                                gs.white_time_left = pre_increment_time - final_elapsed_sec + gs.increment
                                                gs.white_time_log[-1] = gs.white_time_left
                                            else:
                                                pre_increment_time = gs.black_time_log[-2]
                                                gs.black_time_left = pre_increment_time - final_elapsed_sec + gs.increment
                                                gs.black_time_log[-1] = gs.black_time_left

                                            gs.white_time_left = max(0, gs.white_time_left)
                                            gs.black_time_left = max(0, gs.black_time_left)

                                            # sync display times
                                            white_display_time = gs.white_time_left
                                            black_display_time = gs.black_time_left

                                            # reset timer for the next turn
                                            turn_start_time = p.time.get_ticks()
                                            last_update_time = turn_start_time

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
                        else: # click outside the board
                            sq_selected = ()
                            player_clicks = []
                #
                elif e.type == p.KEYDOWN:
                    if e.key == p.K_u:
                        gs.undo_move()

                        turn_start_time = p.time.get_ticks()
                        last_update_time = turn_start_time
                        white_display_time = gs.white_time_left
                        black_display_time = gs.black_time_left

                        move_made = True
                        game_over = False
                        promotion_pending = False
                        pending_move = None
                        game_over_text = ""
                        app_state = "playing"

        # end of event loop

        if app_state == "playing":
            if not game_over:
                current_time_ms = p.time.get_ticks()
                elapsed_turn_time_sec = (current_time_ms - turn_start_time) / 1000.0 # elapsed time in seconds in this turn

                # update display time (every 100ms)
                if current_time_ms - last_update_time >= 100:
                    if gs.white_to_move:
                        white_display_time = gs.white_time_left - elapsed_turn_time_sec
                    else:
                        black_display_time = gs.black_time_left - elapsed_turn_time_sec
                    last_update_time = current_time_ms

                # check timeout
                if (gs.white_to_move and white_display_time <= 0) or \
                (not gs.white_to_move and black_display_time <= 0):

                    game_over = True
                    game_over_text = "black wins on time" if gs.white_to_move else "white wins on time"
                    print(game_over_text)
                    app_state = "game_over"
                    game_over_button = () # reset

                    # prevent display from showing negative time
                    white_display_time = max(0, white_display_time)
                    black_display_time = max(0, black_display_time)

            if not game_over and not promotion_pending and opponent_type != "human" and not gs.white_to_move:
                ai_move = ai.find_best_move(gs, opponent_type)
                if ai_move:
                    gs.make_move(ai_move)

                    final_elapsed_sec = (p.time.get_ticks() - turn_start_time) / 1000.0

                    pre_increment_time = gs.black_time_log[-2]
                    gs.black_time_left = pre_increment_time - final_elapsed_sec + gs.increment
                    gs.black_time_log[-1] = gs.black_time_left

                    gs.white_time_left = max(0, gs.white_time_left)
                    gs.black_time_left = max(0, gs.black_time_left)

                    white_display_time = gs.white_time_left
                    black_display_time = gs.black_time_left

                    turn_start_time = p.time.get_ticks()
                    last_update_time = turn_start_time

                    print("ai move: " + ai_move.get_chess_notation())
                    move_made = True

            if move_made:
                valid_moves = gs.get_legal_moves()
                move_made = False
            if not game_over:
                if len(valid_moves) == 0 and not promotion_pending:
                    game_over = True
                    game_over_text = "stalemate" if not gs.in_check() else "checkmate"
                
                # print(gs.position_history.get(gs.get_game_state_hash(), 0))
                if gs.position_history.get(gs.get_game_state_hash(), 0) >= 3:
                    game_over = True
                    game_over_text = "draw, threefold repetition"
                    #print("draw by threefold repetition")
                
                if gs.fifty_move_counter >= 100: # a play for each side counts as one move
                    game_over = True
                    game_over_text = "drawn, fifty-move rule"
                    #print("drawn by fifty-move rule")

                if gs.check_insufficient_material():
                    game_over = True
                    game_over_text = "draw, insufficient material"
                    #print("draw by insufficient material")
                
                if game_over:
                    print(game_over_text) # console log
                    app_state = "game_over"
        mouse_pos = p.mouse.get_pos()

        if app_state == "menu":
            menu_buttons = draw_menu(screen, mouse_pos, FONT, SMALL_FONT)
        elif app_state == "game_over":
            #print("game over text: ", game_over_text)
            game_over_button = draw_game_over(screen, game_over_text, FONT)
        elif app_state == "playing":
            draw_game_state(screen, gs,valid_moves, sq_selected)
            scroll_offset_y = draw_side_panel(screen, gs, FONT, SMALL_FONT, scroll_offset_y,
                                              white_display_time, black_display_time, gs.white_to_move)
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

def draw_side_panel(screen, gs, font, small_font, scroll_y,
                    w_time, b_time, white_turn):
    panel_rect = p.Rect(512, 0, 256, HEIGHT)
    p.draw.rect(screen, p.Color("black"), panel_rect)

    padding = 10
    text_color = p.Color("white")
    active_clock_color = p.Color("yellow") # highlight active clock

    # areas
    log_area_width = 250
    log_area_height = 172
    log_area_x = panel_rect.x + (panel_rect.width - log_area_width) // 2
    log_area_y = panel_rect.y + (panel_rect.height - log_area_height) // 2
    log_area_rect = p.Rect(log_area_x, log_area_y, log_area_width, log_area_height)

    # leaving space for clocks
    clock_height_estimate = font.get_height() + 10 # height needed for clock text + padding
    available_space_each = (panel_rect.height - log_area_height - 2 * padding - 2 * clock_height_estimate) // 2
    capture_area_height = max(CAPTURED_SQ_SIZE + padding, available_space_each)

    # black captures pos
    black_captures_y = padding
    black_captures_rect = p.Rect(panel_rect.x + padding, black_captures_y,
                                panel_rect.width - 2 * padding, capture_area_height)

    # clock pos
    black_clock_y = black_captures_rect.bottom + 5
    white_clock_y = log_area_rect.bottom + 5

    # white captures
    white_captures_y = white_clock_y + clock_height_estimate
    white_captures_rect = p.Rect(panel_rect.x + padding, white_captures_y,
                                panel_rect.width - 2 * padding, capture_area_height)

    # draw captures
    material_diff = 0
    piece_order = ['p', 'N', 'B', 'R', 'Q']

    # black captures
    black_capture_counts = {'p': 0, 'N': 0, 'B': 0, 'R': 0, 'Q': 0}
    for piece in gs.black_captured:
        black_capture_counts[piece.type] += 1
        material_diff -= ai.pst.piece_scores.get(piece.type, 0)

    current_x = black_captures_rect.x
    current_y = black_captures_rect.y
    for piece_type in piece_order:
        count = black_capture_counts[piece_type]
        if count > 0:
            if current_y + CAPTURED_SQ_SIZE <= black_captures_rect.bottom:
                img = CAPTURED_IMAGES['w' + piece_type]
                screen.blit(img, (current_x, current_y))
                if count > 1:
                    count_text = small_font.render(f"x{count}", True, text_color)
                    screen.blit(count_text, (current_x + CAPTURED_SQ_SIZE - 10, current_y + CAPTURED_SQ_SIZE - 15))
                current_x += CAPTURED_SQ_SIZE + 5

    # white captures
    white_capture_counts = {'p': 0, 'N': 0, 'B': 0, 'R': 0, 'Q': 0}
    for piece in gs.white_captured:
        white_capture_counts[piece.type] += 1
        material_diff += ai.pst.piece_scores.get(piece.type, 0)

    current_x = white_captures_rect.x
    current_y = white_captures_rect.y
    for piece_type in piece_order:
        count = white_capture_counts[piece_type]
        if count > 0:
             if current_y + CAPTURED_SQ_SIZE <= white_captures_rect.bottom:
                img = CAPTURED_IMAGES['b' + piece_type]
                screen.blit(img, (current_x, current_y))
                if count > 1:
                    count_text = small_font.render(f"x{count}", True, text_color)
                    screen.blit(count_text, (current_x + CAPTURED_SQ_SIZE - 10, current_y + CAPTURED_SQ_SIZE - 15))
                current_x += CAPTURED_SQ_SIZE + 5

    # material difference
    if material_diff != 0:
        diff_sign = "+" if material_diff > 0 else ""
        diff_text = small_font.render(f"({diff_sign}{material_diff})", True, text_color)
        screen.blit(diff_text, (black_captures_rect.right - diff_text.get_width() - 5, black_captures_rect.y + 5))

    # draw clocks
    black_time_str = format_time(b_time)
    white_time_str = format_time(w_time)

    black_text = font.render(black_time_str, True, active_clock_color if not white_turn else text_color)
    white_text = font.render(white_time_str, True, active_clock_color if white_turn else text_color)

    black_text_rect = black_text.get_rect(centerx=panel_rect.centerx, y=black_clock_y)
    white_text_rect = white_text.get_rect(centerx=panel_rect.centerx, y=white_clock_y)

    screen.blit(black_text, black_text_rect)
    screen.blit(white_text, white_text_rect)

    # draw move log
    line_spacing = 3
    total_text_height = 0
    move_log = gs.move_log
    lines_to_render = []
    line_text = ""
    for i, move in enumerate(move_log):
         move_number = (i // 2) + 1
         if i % 2 == 0:
             line_text = f"{move_number}. {move.get_chess_notation()}"
             if i == len(move_log) - 1:
                  lines_to_render.append(line_text)
                  text_object = small_font.render(line_text, True, text_color)
                  total_text_height += text_object.get_height() + line_spacing
         else:
             line_text += f" {move.get_chess_notation()}"
             lines_to_render.append(line_text)
             text_object = small_font.render(line_text, True, text_color)
             total_text_height += text_object.get_height() + line_spacing
             line_text = ""

    if total_text_height > 0:
         total_text_height -= line_spacing

    text_surface_height = max(total_text_height, log_area_height)
    text_surface = p.Surface((log_area_width, text_surface_height))
    text_surface.fill(p.Color(34,34,34))

    current_y_on_surface = 0
    for line in lines_to_render:
        text_object = small_font.render(line, True, text_color)
        text_rect = text_object.get_rect(centerx=log_area_width // 2, top=current_y_on_surface)
        text_surface.blit(text_object, text_rect)
        current_y_on_surface += text_object.get_height() + line_spacing

    max_scroll = max(0, total_text_height - log_area_height)
    scroll_y = max(0, min(scroll_y, max_scroll))

    source_rect = p.Rect(0, scroll_y, log_area_width, log_area_height)
    destination_rect = log_area_rect
    screen.blit(text_surface, destination_rect, source_rect)

    return scroll_y

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

def draw_menu(screen, mouse_pos, font, small_font):
    screen.fill(p.Color("black"))
    font = p.font.SysFont("Arial", 32, bold=True, italic=False)

    # tit(s)le
    text = font.render("chASS", 1, p.Color("white"))
    text_react = text.get_rect(center=(WIDTH // 2, HEIGHT // 12))
    screen.blit(text, text_react)

    buttons = {
        "pvp": {
            "rect": p.Rect((WIDTH // 4), (HEIGHT // 2) - 60, (WIDTH // 2), 50),
            "text": "PvP",
            "desc": "Play a two-player (or solo) game locally."
        },
        "ai_classic": {
            "rect": p.Rect((WIDTH // 4), (HEIGHT // 2) + 10, (WIDTH // 2), 50),
            "text": "PvAI",
            "desc": "Play against the fast, logic-based AI."
        },
        "ai_ml": {
            "rect": p.Rect((WIDTH // 4), (HEIGHT // 2) + 80, (WIDTH // 2), 50),
            "text": "PvAI (ML)",
            "desc": "Play against the experimental machine learning AI."
        }
    }

    color_default = p.Color("gray")
    color_hover = p.Color("lightyellow")
    explanation_text = ""
    button_rects_to_return = []

    for key, button in buttons.items():
        color = color_default
        if button["rect"].collidepoint(mouse_pos):
            color = color_hover
            explanation_text = button["desc"]
        
        p.draw.rect(screen, color, button["rect"])
        text_obj = font.render(button["text"], 1, p.Color("black"))

        screen.blit(text_obj, text_obj.get_rect(center=button["rect"].center))
        button_rects_to_return.append(button["rect"])
    
    if explanation_text:
        exp_text_obj = small_font.render(explanation_text, 1, p.Color("white"))
        exp_text_rect = exp_text_obj.get_rect(center=(WIDTH // 2, (HEIGHT // 2) - 130))
        screen.blit(exp_text_obj, exp_text_rect)
    
    return tuple(button_rects_to_return)

def draw_game_over(screen, text, font):
    menu_rect = p.Rect(0, 0, 400, 200)
    menu_rect.center = (WIDTH // 2, HEIGHT // 2)
    p.draw.rect(screen, p.Color("black"), menu_rect)
    p.draw.rect(screen, p.Color("white"), menu_rect.inflate(4, 4), 2)

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

def format_time(seconds):
    if seconds < 0: seconds = 0
    minutes = int(seconds // 60)
    secs = seconds % 60
    tenths = int(max(0, (seconds - int(seconds))) * 10)
    return f"{minutes:02}:{int(secs):02}.{tenths}"

if __name__ == "__main__":
    main()