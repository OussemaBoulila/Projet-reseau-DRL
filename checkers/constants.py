import pygame

WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH//COLS

# rgb
RED = (39,24,16)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 255,0 )
GREY = (128,128,128)
BWHITE=(238, 235, 227)

CROWN = pygame.transform.scale(pygame.image.load('assets/crown.png'), (44, 25))
