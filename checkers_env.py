import gymnasium as gym
import numpy as np
import pygame
from gymnasium import spaces
from checkers.gameAI import Game
from checkers.constants import ROWS, COLS, WHITE, RED

class CheckersEnv(gym.Env):
    metadata = {'render_modes': ['human', 'rgb_array'], 'render_fps': 30}

    def __init__(self, render_mode=None):
        # Define observation and action spaces FIRST
        self.observation_space = spaces.Dict({
            'board': spaces.Box(low=-2, high=2, shape=(64,), dtype=np.int8),
            'action_mask': spaces.Box(low=0, high=1, shape=(4096,), dtype=np.int8)
        })
        self.action_space = spaces.Discrete(4096)
        
        super().__init__()
        
        # Attributes
        self.render_mode = render_mode
        self.game = Game(None)
        self.current_player = WHITE
        self.steps = 0
        self.max_steps = 150
        self.action_history = []
        self.window_size = 800
        self.window = None
        self.clock = None

    def get_observation(self):
        board_obs = np.zeros((64,), dtype=np.int8)
        action_mask = np.zeros((4096,), dtype=np.int8)

        for row in range(8):
            for col in range(8):
                piece = self.game.board.get_piece(row, col)
                if piece:
                    idx = row * 8 + col
                    value = 1 if piece.color == WHITE else -1
                    if piece.king:
                        value *= 2
                    board_obs[idx] = value

                    if piece.color == self.current_player:
                        valid_moves = self.game.board.get_valid_moves(piece)
                        for (to_row, to_col) in valid_moves:
                            to_idx = to_row * 8 + to_col
                            action_idx = idx * 64 + to_idx
                            action_mask[action_idx] = 1

        return {
            'board': board_obs,
            'action_mask': action_mask
        }

    def step(self, action):
        self.steps += 1
        self.action_history.append(action)

        reward = -0.02  # Small base penalty
        terminated = truncated = False
        info = {'valid_move': False, 'captures': 0}

        if self.steps >= self.max_steps:
            truncated = True
            info['termination_reason'] = 'max_steps'
            return self.get_observation(), reward, terminated, truncated, info

        from_row, from_col = divmod(action // 64, 8)
        to_row, to_col = divmod(action % 64, 8)
        piece = self.game.board.get_piece(from_row, from_col)
        valid_moves = self.game.board.get_valid_moves(piece) if piece else {}

        if piece and piece.color == self.current_player and (to_row, to_col) in valid_moves:
            info['valid_move'] = True
            self.game.select(from_row, from_col)
            self.game.select(to_row, to_col)

            reward += 0.03
            captures = len(valid_moves.get((to_row, to_col), []))
            if captures:
                reward += 0.25 * captures
                info['captures'] = captures

            winner = self.game.winner()
            draw_type = self.game.check_draw()

            if winner is not None:
                terminated = True
                reward += 10.0 if winner == WHITE else -10.0
                info['winner'] = winner
                info['termination_reason'] = 'win'
            elif draw_type is not None:
                terminated = True
                reward += 0.2  # Small bonus for surviving till draw
                info['draw'] = draw_type
                info['termination_reason'] = 'draw'

            else:
                # Normal move, continue
                self.current_player = RED if self.current_player == WHITE else WHITE
        else:
            # Illegal move
            terminated = True
            reward = -1.0
            info['termination_reason'] = 'invalid_move'

        if reward > 8.0:
            print(f"\n⚠️ High reward: {reward:.2f} at step {self.steps}")
            print(f"Last actions: {self.action_history[-5:]}")
            print(f"Captures: {info.get('captures', 0)}")

        return self.get_observation(), reward, terminated, truncated, info

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.game.reset()
        self.current_player = WHITE
        self.steps = 0
        self.action_history = []
        return self.get_observation(), {}

    def render(self):
        if self.render_mode == 'human':
            if self.window is None:
                pygame.init()
                self.window = pygame.display.set_mode((self.window_size, self.window_size))
                self.clock = pygame.time.Clock()
            self.game.win = self.window
            self.game.update()
            pygame.time.delay(300)

    def close(self):
        if self.window:
            pygame.quit()
