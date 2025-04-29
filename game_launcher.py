import pygame
import sys
import subprocess

def main_menu():
    pygame.init()
    pygame.mixer.init()

    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    WIDTH, HEIGHT = screen.get_size()
    pygame.display.set_caption("Checkers Launcher")
    clock = pygame.time.Clock()

    font_title = pygame.font.SysFont("Garamond", 72)
    font_button = pygame.font.SysFont("Garamond", 32)

    WHITE = (255, 255, 255)
    LIGHT_GRAY = (200, 200, 200)
    DARK_GRAY = (50, 50, 50)
    SILVER = (255, 223, 0)
    BLACK = (0, 0, 0)

    bg_images = [
        pygame.transform.scale(pygame.image.load("assets/battle_chess_background.jpg"), (WIDTH, HEIGHT)),
        pygame.transform.scale(pygame.image.load("assets/battle_chess_background2.jpg"), (WIDTH, HEIGHT))
    ]
    current_bg_index = 0
    background = bg_images[current_bg_index]

    bg_switch_time = 7000
    last_switch = pygame.time.get_ticks()

    try:
        pygame.mixer.music.load("assets/background_music.mp3")
        pygame.mixer.music.play(loops=-1, fade_ms=1000)
        pygame.mixer.music.set_volume(0.6)
    except:
        print("Could not load background music")

    class Button:
        def __init__(self, text, x, y, w, h, callback):
            self.text = text
            self.rect = pygame.Rect(x, y, w, h)
            self.callback = callback
            self.hovered = False

        def draw(self):
            color = LIGHT_GRAY if self.hovered else DARK_GRAY
            pygame.draw.rect(screen, color, self.rect, border_radius=8)
            text_surf = font_button.render(self.text, True, WHITE)
            text_rect = text_surf.get_rect(center=self.rect.center)
            screen.blit(text_surf, text_rect)

        def handle_event(self, event):
            if event.type == pygame.MOUSEMOTION:
                self.hovered = self.rect.collidepoint(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(event.pos):
                    self.callback()

    class VolumeSlider:
        def __init__(self, x, y, w, h):
            self.rect = pygame.Rect(x, y, w, h)
            self.handle_rect = pygame.Rect(x + int(w * 0.6), y - 5, 10, h + 10)
            self.dragging = False
            self.value = 0.6  # Initial volume

        def draw(self):
            pygame.draw.rect(screen, (180, 180, 180), self.rect)
            pygame.draw.rect(screen, SILVER, self.handle_rect)
            label = font_button.render(f"Volume: {int(self.value * 100)}%", True, WHITE)
            screen.blit(label, (self.rect.x, self.rect.y - 35))

        def handle_event(self, event):
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.handle_rect.collidepoint(event.pos):
                    self.dragging = True
            elif event.type == pygame.MOUSEBUTTONUP:
                self.dragging = False
            elif event.type == pygame.MOUSEMOTION and self.dragging:
                new_x = max(self.rect.x, min(event.pos[0], self.rect.x + self.rect.width))
                self.handle_rect.x = new_x
                self.value = (new_x - self.rect.x) / self.rect.width
                pygame.mixer.music.set_volume(self.value)

    def launch_singleplayer():
        pygame.mixer.music.stop()
        pygame.quit()
        subprocess.run([sys.executable, "Singleplayer.py"])

    def launch_local_multiplayer():
        pygame.mixer.music.stop()
        pygame.quit()
        subprocess.run([sys.executable, "LocalMultiplayer.py"])

    def launch_host():
        pygame.mixer.music.stop()
        pygame.quit()
        subprocess.run([sys.executable, "main.py", "HOST"])

    def launch_join():
        pygame.mixer.music.stop()
        pygame.quit()
        subprocess.run([sys.executable, "main.py", "JOIN"])

    def quit_game():
        pygame.mixer.music.stop()
        pygame.quit()
        sys.exit()

    button_width, button_height = 300, 60
    button_x = (WIDTH - button_width) // 2
    start_y = HEIGHT // 2 - 140
    gap = 80

    buttons = [
        Button("Single Player", button_x, start_y, button_width, button_height, launch_singleplayer),
        Button("Local Multiplayer", button_x, start_y + gap, button_width, button_height, launch_local_multiplayer),
        Button("Host Online Game", button_x, start_y + gap * 2, button_width, button_height, launch_host),
        Button("Join Online Game", button_x, start_y + gap * 3, button_width, button_height, launch_join),
        Button("Quit", button_x, start_y + gap * 4, button_width, button_height, quit_game),
    ]

    slider_width = 200
    slider = VolumeSlider((WIDTH - slider_width) // 2, start_y + gap * 5 + 10, slider_width, 10)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                quit_game()
            for btn in buttons:
                btn.handle_event(event)
            slider.handle_event(event)

        now = pygame.time.get_ticks()
        if now - last_switch >= bg_switch_time:
            current_bg_index = (current_bg_index + 1) % len(bg_images)
            background = bg_images[current_bg_index]
            last_switch = now

        screen.blit(background, (0, 0))

        title_surf = font_title.render("JUMIA CHESS", True, SILVER)
        title_rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 5))
        screen.blit(title_surf, title_rect)

        for btn in buttons:
            btn.draw()

        slider.draw()

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main_menu()
