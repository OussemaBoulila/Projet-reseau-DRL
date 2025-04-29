
import pygame

class Piece:
    PADDING = 18
    OUTLINE = 2

    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.king = False
        self.x = 0
        self.y = 0
        self.calc_pos()

    def calc_pos(self):
        self.x = self.col * 100 + 50
        self.y = self.row * 100 + 50

    def make_king(self):
        self.king = True

    def draw(self, screen):
        radius = 32
        pygame.draw.circle(screen, (128,128,128), (self.x, self.y), radius + self.OUTLINE)
        pygame.draw.circle(screen, self.color, (self.x, self.y), radius)

    def move(self, row, col):
        self.row = row
        self.col = col
        self.calc_pos()
