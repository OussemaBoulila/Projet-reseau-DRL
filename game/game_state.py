import pygame
from game.board import Board

RED = (39,24,16)
WHITE = (255, 255, 255)

class GameState:
    def __init__(self, mode, screen, network=None, player_color=None):
        self.board = Board()
        self.turn = RED
        self.selected = None
        self.valid_moves = {}
        self.mode = mode
        self.screen = screen
        self.network = network
        self.player_color = player_color

    def handle_network(self):
        if self.network and self.player_color and self.turn != self.player_color:
            data = self.network.receive()
            if data:
                self.board = data
                self.change_turn()

    def select(self, pos):
        row, col = pos[1] // 100, pos[0] // 100
        if self.selected:
            result = self._move(row, col)
            if not result:
                self.selected = None
                self.select(pos)
        piece = self.board.get_piece(row, col)
        # only allow selecting on your turn in online mode
        if piece != 0 and piece.color == self.turn and (not self.network or self.turn == self.player_color):
            self.selected = piece
            self.valid_moves = self.board.get_valid_moves(piece)
            return True
        return False

    def _move(self, row, col):
        piece = self.board.get_piece(row, col)
        if self.selected and (row, col) in self.valid_moves:
            self.board.move(self.selected, row, col)
            skipped = self.valid_moves[(row, col)]
            if skipped:
                self.board.remove(skipped)
            # send updated board to opponent
            if self.network and self.mode in ["HOST", "JOIN"]:
                self.network.send(self.board)
            self.change_turn()
        else:
            return False
        return True

    def draw_valid_moves(self, moves):
        for move in moves:
            row, col = move
            pygame.draw.circle(self.screen, (0,255,0), (col*100 + 50, row*100 + 50), 15)

    def update(self):
        self.board.draw(self.screen)
        self.draw_valid_moves(self.valid_moves)
        pygame.display.update()

    def reset(self):
        self.selected = None
        self.valid_moves = {}

    def change_turn(self):
        self.valid_moves = {}
        self.turn = WHITE if self.turn == RED else RED
