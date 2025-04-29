import pygame
import numpy as np
from sb3_contrib import MaskablePPO
from sb3_contrib.common.maskable.policies import MaskableActorCriticPolicy
from checkers.constants import WIDTH, HEIGHT, SQUARE_SIZE, RED, WHITE
from checkers.gameAI import Game
import time
import sys

FPS = 60
MUTE_BTN_RECT = pygame.Rect(10, 10, 50, 40)
AI_MOVE_DELAY = 0.5

def get_row_col_from_mouse(pos):
    x, y = pos
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    return row, col

def draw_mute_button(win, is_muted):
    color = (180, 180, 180) if is_muted else (50, 200, 50)
    pygame.draw.rect(win, color, MUTE_BTN_RECT, border_radius=5)
    font = pygame.font.SysFont("Arial", 24, bold=True)
    icon = "  X" if is_muted else "  V"
    label = font.render(icon, True, (0, 0, 0))
    win.blit(label, (MUTE_BTN_RECT.x + 5, MUTE_BTN_RECT.y + 5))

def show_game_result(win, result):
    """Display win/loss announcement popup"""
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    win.blit(overlay, (0, 0))
    
    popup_rect = pygame.Rect(WIDTH//4, HEIGHT//3, WIDTH//2, HEIGHT//3)
    pygame.draw.rect(win, (50, 50, 50), popup_rect, border_radius=10)
    pygame.draw.rect(win, (100, 100, 100), popup_rect, 2, border_radius=10)
    
    font = pygame.font.SysFont("Arial", 24)
    title = font.render("Game Over!", True, (255, 255, 255))
    
    if result == "win":
        message = font.render("You Won!", True, (0, 255, 0))
    else:
        message = font.render("You Lost!", True, (255, 0, 0))
    
    win.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3 + 30))
    win.blit(message, (WIDTH//2 - message.get_width()//2, HEIGHT//3 + 70))
    
    menu_btn = pygame.Rect(WIDTH//2 - 100, HEIGHT//3 + 120, 90, 40)
    rematch_btn = pygame.Rect(WIDTH//2 + 10, HEIGHT//3 + 120, 90, 40)
    
    pygame.draw.rect(win, (70, 70, 70), menu_btn, border_radius=5)
    pygame.draw.rect(win, (70, 70, 70), rematch_btn, border_radius=5)
    
    menu_text = font.render("Menu", True, (255, 255, 255))
    rematch_text = font.render("Rematch", True, (255, 255, 255))
    
    win.blit(menu_text, (menu_btn.x + 25, menu_btn.y + 10))
    win.blit(rematch_text, (rematch_btn.x + 10, rematch_btn.y + 10))
    
    pygame.display.update()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if menu_btn.collidepoint(pos):
                    return "menu"
                elif rematch_btn.collidepoint(pos):
                    return "rematch"

def show_draw_popup(win, draw_type):
    """Display draw announcement popup"""
    messages = {
        "threefold_repetition": "Draw by threefold repetition!",
        "40_moves_no_capture": "Draw by 40-move rule!",
        "no_legal_moves": "Draw - no legal moves!",
        "insufficient_material": "Draw by insufficient material!"
    }
    
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    win.blit(overlay, (0, 0))
    
    popup_rect = pygame.Rect(WIDTH//4, HEIGHT//3, WIDTH//2, HEIGHT//3)
    pygame.draw.rect(win, (50, 50, 50), popup_rect, border_radius=10)
    pygame.draw.rect(win, (100, 100, 100), popup_rect, 2, border_radius=10)
    
    font = pygame.font.SysFont("Arial", 24)
    title = font.render("Game Drawn!", True, (255, 255, 255))
    reason = font.render(messages[draw_type], True, (200, 200, 0))
    
    win.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3 + 30))
    win.blit(reason, (WIDTH//2 - reason.get_width()//2, HEIGHT//3 + 70))
    
    menu_btn = pygame.Rect(WIDTH//2 - 100, HEIGHT//3 + 120, 90, 40)
    rematch_btn = pygame.Rect(WIDTH//2 + 10, HEIGHT//3 + 120, 90, 40)
    
    pygame.draw.rect(win, (70, 70, 70), menu_btn, border_radius=5)
    pygame.draw.rect(win, (70, 70, 70), rematch_btn, border_radius=5)
    
    menu_text = font.render("Menu", True, (255, 255, 255))
    rematch_text = font.render("Rematch", True, (255, 255, 255))
    
    win.blit(menu_text, (menu_btn.x + 25, menu_btn.y + 10))
    win.blit(rematch_text, (rematch_btn.x + 10, rematch_btn.y + 10))
    
    pygame.display.update()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if menu_btn.collidepoint(pos):
                    return "menu"
                elif rematch_btn.collidepoint(pos):
                    return "rematch"

def get_observation_and_mask(game, current_player):
    board_obs = np.zeros((64,), dtype=np.int8)
    action_mask = np.zeros(4096, dtype=np.int8)

    for row in range(8):
        for col in range(8):
            piece = game.board.get_piece(row, col)
            if piece:
                idx = row * 8 + col
                val = 1 if piece.color == WHITE else -1
                if piece.king:
                    val *= 2
                board_obs[idx] = val

                if piece.color == current_player:
                    valid_moves = game.board.get_valid_moves(piece)
                    for (to_row, to_col) in valid_moves:
                        to_idx = to_row * 8 + to_col
                        action_idx = idx * 64 + to_idx
                        action_mask[action_idx] = 1
    return {
        "board": board_obs,
        "action_mask": action_mask
    }

def run_singleplayer():
    pygame.init()
    pygame.mixer.init()
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Checkers - Human (BROWN) vs AI (WHITE)')

    is_muted = False

    try:
        pygame.mixer.music.load("assets/BGSG.mp3")
        pygame.mixer.music.set_volume(0.1)
        pygame.mixer.music.play(-1)
    except Exception as e:
        print(f"Could not load music: {e}")

    try:
        model = MaskablePPO.load(
            "model/checkers_ai_model.zip",
            policy=MaskableActorCriticPolicy
        )
        print("✅ MaskablePPO AI loaded successfully!")
    except Exception as e:
        print(f"❌ Error loading AI: {e}")
        pygame.quit()
        return

    game = Game(WIN)
    clock = pygame.time.Clock()
    run = True
    ai_thinking = False
    ai_move_time = 0

    while run:
        clock.tick(FPS)
        current_time = time.time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and not ai_thinking:
                pos = pygame.mouse.get_pos()

                if MUTE_BTN_RECT.collidepoint(pos):
                    is_muted = not is_muted
                    pygame.mixer.music.set_volume(0 if is_muted else 0.1)

                if game.turn == RED:
                    row, col = get_row_col_from_mouse(pos)
                    game.select(row, col)

        if game.turn == WHITE and not ai_thinking:
            ai_thinking = True
            ai_move_time = current_time + AI_MOVE_DELAY

        if ai_thinking and current_time >= ai_move_time:
            observation = get_observation_and_mask(game, WHITE)
            action, _ = model.predict(observation, action_masks=observation["action_mask"], deterministic=True)

            from_idx = action // 64
            to_idx = action % 64
            from_row, from_col = divmod(from_idx, 8)
            to_row, to_col = divmod(to_idx, 8)

            piece = game.board.get_piece(from_row, from_col)
            if piece and piece.color == WHITE:
                valid_moves = game.board.get_valid_moves(piece)
                if (to_row, to_col) in valid_moves:
                    game.select(from_row, from_col)
                    game.select(to_row, to_col)

            ai_thinking = False

        winner = game.winner()
        draw_type = game.check_draw()
        
        if winner is not None:
            result = "win" if winner == RED else "loss"
            popup_result = show_game_result(WIN, result)
            
            if popup_result == "rematch":
                game = Game(WIN)
                ai_thinking = False
            elif popup_result == "menu":
                run = False
        elif draw_type:
            popup_result = show_draw_popup(WIN, draw_type)
            if popup_result == "rematch":
                game = Game(WIN)
                ai_thinking = False
            elif popup_result == "menu":
                run = False

        game.update()
        draw_mute_button(WIN, is_muted)
        
        if ai_thinking:
            font = pygame.font.SysFont("Arial", 20)
            thinking_text = font.render("AI is thinking...", True, (0, 0, 0))
            WIN.blit(thinking_text, (WIDTH - 150, 10))
        
        pygame.display.update()

    pygame.quit()
    # Only return to menu if "Menu" was clicked
    if not run:  # This means "Menu" was clicked
        import subprocess
        subprocess.run([sys.executable, "game_launcher.py"])

if __name__ == "__main__":
    run_singleplayer()
