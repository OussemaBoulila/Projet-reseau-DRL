import pygame
import sys
from checkers.constants import WIDTH, HEIGHT, SQUARE_SIZE, RED, WHITE
from checkers.game import Game

FPS = 60
MUTE_BTN_RECT = pygame.Rect(10, 10, 40, 40)

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

def show_game_result(win, winner):
    """Display win/loss announcement popup"""
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    win.blit(overlay, (0, 0))
    
    popup_rect = pygame.Rect(WIDTH//4, HEIGHT//3, WIDTH//2, HEIGHT//3)
    pygame.draw.rect(win, (50, 50, 50), popup_rect, border_radius=10)
    pygame.draw.rect(win, (100, 100, 100), popup_rect, 2, border_radius=10)
    
    font = pygame.font.SysFont("Arial", 24)
    title = font.render("Game Over!", True, (255, 255, 255))
    
    if winner == RED:
        message = font.render("Red Player Wins!", True, (255, 0, 0))
    else:
        message = font.render("White Player Wins!", True, (255, 255, 255))
    
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
        "no_legal_moves": "Draw - no legal moves!"
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

def run_local_multiplayer():
    pygame.init()
    pygame.mixer.init()
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Checkers - Local Multiplayer')

    is_muted = False

    try:
        pygame.mixer.music.load("assets/BGSG.mp3")
        pygame.mixer.music.set_volume(0.1)
        pygame.mixer.music.play(-1)
    except Exception as e:
        print(f"Could not load music: {e}")

    run = True
    clock = pygame.time.Clock()
    game = Game(WIN)

    while run:
        clock.tick(FPS)

        winner = game.winner()
        draw_type = game.check_draw()
        
        if winner is not None:
            result = show_game_result(WIN, winner)
            if result == "rematch":
                game = Game(WIN)
            elif result == "menu":
                run = False
        elif draw_type:
            result = show_draw_popup(WIN, draw_type)
            if result == "rematch":
                game = Game(WIN)
            elif result == "menu":
                run = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if MUTE_BTN_RECT.collidepoint(pos):
                    is_muted = not is_muted
                    pygame.mixer.music.set_volume(0 if is_muted else 0.1)
                else:
                    row, col = get_row_col_from_mouse(pos)
                    game.select(row, col)

        game.update()
        draw_mute_button(WIN, is_muted)
        pygame.display.update()

    pygame.quit()
    # Only return to menu if "Menu" button was clicked
    if not run:  # This means "Menu" was clicked
        import subprocess
        subprocess.Popen([sys.executable, "game_launcher.py"])

if __name__ == "__main__":
    run_local_multiplayer()
