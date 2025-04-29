
import pygame
import sys

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FONT = None

def main_menu(screen):
    global FONT
    FONT = pygame.font.Font(None, 74)
    buttons = [
        ("Single Player", "SINGLE"),
        ("Local Multiplayer", "LOCAL"),
        ("Host Online Game", "HOST"),
        ("Join Online Game", "JOIN"),
        ("Exit", "EXIT")
    ]
    button_rects = []

    while True:
        screen.fill(BLACK)
        mx, my = pygame.mouse.get_pos()

        for idx, (text, _) in enumerate(buttons):
            button = FONT.render(text, True, WHITE)
            rect = button.get_rect(center=(screen.get_width() // 2, 150 + idx * 100))
            screen.blit(button, rect)
            button_rects.append((rect, buttons[idx][1]))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for rect, action in button_rects:
                    if rect.collidepoint((mx, my)):
                        return action

        pygame.display.update()
    