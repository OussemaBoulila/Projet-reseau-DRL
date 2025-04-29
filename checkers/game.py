import pygame
from .constants import RED, WHITE, BLUE, SQUARE_SIZE, WIDTH
from checkers.board import Board

class Game:
    def __init__(self, win):
        self._init()
        self.win = win
        self.position_count = {}  # Tracks how many times each position occurs
        self.no_capture_count = 0
        self.draw_offer = False
    
    def update(self):
        self.board.draw(self.win)
        self.draw_valid_moves(self.valid_moves)
        if self.draw_offer:
            self.draw_draw_indication()

    def _init(self):
        self.selected = None
        self.board = Board()
        self.turn = RED
        self.valid_moves = {}
        self.move_history = []
        self.position_count = {}
        self.no_capture_count = 0
        self.draw_offer = False
        # Record initial position
        self._record_position()

    def _record_position(self):
        """Record the current board position in position_count"""
        position_hash = self.get_board_hash()
        if position_hash in self.position_count:
            self.position_count[position_hash] += 1
        else:
            self.position_count[position_hash] = 1

    def winner(self):
        return self.board.winner()

    def check_draw(self):
        """Returns draw type if detected, None otherwise"""
        # 1. Threefold repetition
        if self.check_repetition(3):
            return "threefold_repetition"
            
        # 2. 40-move rule
        if self.no_capture_count >= 40:
            return "40_moves_no_capture"
            
        # 3. No legal moves
        if not any(self.board.get_valid_moves(piece) 
                for piece in self.board.get_all_pieces(self.turn)):
            return "no_legal_moves"
            
        return None

    def check_repetition(self, count):
        """Check if current position has occurred 'count' times"""
        # Need at least 4 moves per player to potentially have repetition
        if len(self.move_history) < 8:
            return False
        current_hash = self.get_board_hash()
        return self.position_count.get(current_hash, 0) >= count

    def get_board_hash(self):
        """Creates unique hash of current board state including turn"""
        pieces_tuple = tuple(
            (piece.row, piece.col, piece.king, piece.color) 
            for piece in self.board.get_all_pieces()
        )
        return hash((pieces_tuple, self.turn))  # Include current turn in hash

    def draw_draw_indication(self):
        font = pygame.font.SysFont("Arial", 24)
        text = font.render("Draw Offer Active!", True, (255, 215, 0))
        self.win.blit(text, (WIDTH//2 - text.get_width()//2, 10))

    def reset(self):
        self._init()

    def select(self, row, col):
        if self.selected:
            result = self._move(row, col)
            if not result:
                self.selected = None
                self.select(row, col)
        
        piece = self.board.get_piece(row, col)
        if piece != 0 and piece.color == self.turn:
            self.selected = piece
            self.valid_moves = self.board.get_valid_moves(piece)
            return True
            
        return False

    def _move(self, row, col):
        if self.selected and (row, col) in self.valid_moves:
            skipped = self.valid_moves[(row, col)]
            self.board.move(self.selected, row, col)
            
            if skipped:
                self.board.remove(skipped)
                self.no_capture_count = 0
                
                # Immediately check for follow-up captures
                additional_moves = self.board.get_valid_moves(self.selected)
                if any(skipped for skipped in additional_moves.values()):
                    # Take the first available follow-up capture
                    next_move, next_skipped = next((m, s) for m, s in additional_moves.items() if s)
                    self.board.move(self.selected, next_move[0], next_move[1])
                    self.board.remove(next_skipped)
            
            self.change_turn()
            return True
        return False

    def draw_valid_moves(self, moves):
        for move in moves:
            row, col = move
            pygame.draw.circle(self.win, BLUE, 
                             (col * SQUARE_SIZE + SQUARE_SIZE//2, 
                              row * SQUARE_SIZE + SQUARE_SIZE//2), 15)

    def change_turn(self):
        self.valid_moves = {}
        self.selected = None
        self.turn = WHITE if self.turn == RED else RED