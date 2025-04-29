import pygame
from .constants import RED, WHITE, BLUE, SQUARE_SIZE, WIDTH
from checkers.board import Board

class Game:
    def __init__(self, win):
        self._init()
        self.win = win
        self.position_count = {}  # Tracks how many times each position occurs
        self.no_capture_count = 0
        self.move_history = []
    
    def update(self):
        self.board.draw(self.win)
        if self.selected:
            self.draw_valid_moves(self.board.get_valid_moves(self.selected))
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
        self._record_position()

    def _record_position(self):
        """Record the current board position in position_count"""
        position_hash = self.get_board_hash()
        if position_hash in self.position_count:
            self.position_count[position_hash] += 1
        else:
            self.position_count[position_hash] = 1
        self.move_history.append(position_hash)

    def winner(self):
        return self.board.winner()

    def check_draw(self):
        """Returns draw type if detected, None otherwise"""
        # 1. Threefold repetition
        if self.check_repetition(3):
            return "threefold_repetition"
            
        # 2. 40-move rule (40 moves per player = 80 half-moves)
        if self.no_capture_count >= 80:
            return "40_moves_no_capture"
            
        # 3. No legal moves (stalemate)
        if not any(self.board.get_valid_moves(piece) 
                 for piece in self.board.get_all_pieces(self.turn)):
            return "no_legal_moves"
            
        # 4. Insufficient material
        if self.is_insufficient_material():
            return "insufficient_material"
            
        return None

    def is_insufficient_material(self):
        """Check if neither player can win with remaining pieces"""
        white_pieces = 0
        red_pieces = 0
        white_kings = 0
        red_kings = 0
        
        for piece in self.board.get_all_pieces():
            if piece.color == WHITE:
                white_pieces += 1
                if piece.king:
                    white_kings += 1
            else:
                red_pieces += 1
                if piece.king:
                    red_kings += 1
        
        # Lone king vs lone king
        if white_pieces == 1 and red_pieces == 1:
            return True
            
        # King vs king + 1 piece (if the single piece is a king)
        if (white_pieces == 1 and red_pieces == 2 and red_kings == 2) or \
           (red_pieces == 1 and white_pieces == 2 and white_kings == 2):
            return True
            
        return False

    def check_repetition(self, count):
        """Check if current position has occurred 'count' times"""
        current_hash = self.get_board_hash()
        return self.position_count.get(current_hash, 0) >= count

    def get_board_hash(self):
        """Creates unique hash of current board state including turn"""
        pieces_tuple = tuple(
            (piece.row, piece.col, piece.king, piece.color) 
            for piece in self.board.get_all_pieces()
        )
        return hash((pieces_tuple, self.turn))

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
                self.no_capture_count = 0  # Reset on capture
            else:
                self.no_capture_count += 1
                
            self._record_position()
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
        self.draw_offer = False