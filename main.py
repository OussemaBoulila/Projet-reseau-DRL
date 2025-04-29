import pygame
import threading
import sys
from ui.menu import main_menu
from game.game_state import GameState, RED, WHITE
from network.host import start_server
from network.join import join_game

pygame.init()
screen = pygame.display.set_mode((800, 800))
pygame.display.set_caption("Checkers")

def main():
    clock = pygame.time.Clock()
    run = True

    if len(sys.argv) > 1:
        mode = sys.argv[1].upper()
    else:
        mode = main_menu(screen)

    network = None
    player_color = None

    if mode == "HOST":
        threading.Thread(target=start_server, daemon=True).start()
        pygame.time.delay(1000)
        network = join_game("localhost")
        player_color = RED
    elif mode == "JOIN":
        host_ip = "127.0.0.1"
        network = join_game(host_ip)
        player_color = WHITE

    game = GameState(mode, screen, network, player_color)

    while run:
        game.handle_network()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                game.select(pos)

        game.update()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
