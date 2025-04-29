import os
import datetime
import numpy as np
import torch
import torch.nn as nn
import csv
import gymnasium as gym
from sb3_contrib import MaskablePPO
from sb3_contrib.common.maskable.policies import MaskableActorCriticPolicy
from sb3_contrib.common.wrappers import ActionMasker
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.vec_env import DummyVecEnv, VecMonitor
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor
from checkers_env import CheckersEnv

# === CONFIGURATION ===
MODEL_DIR = "models"
LOG_DIR = "logs"
MODEL_VERSION = "v2"
ARCHITECTURE_VERSION = "2.1"
MODEL_PATH = os.path.join(MODEL_DIR, f"checkers_ai_{MODEL_VERSION}_{ARCHITECTURE_VERSION}")
LOG_PATH = os.path.join(LOG_DIR, "training_log.csv")

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# === FEATURE EXTRACTOR ===
class RobustMaskedFeatureExtractor(BaseFeaturesExtractor):
    def __init__(self, observation_space: gym.spaces.Dict, features_dim: int = 256):
        super().__init__(observation_space, features_dim)
        self.board_net = nn.Sequential(
            nn.Linear(64, 128),
            nn.ReLU(),
            nn.LayerNorm(128),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, features_dim),
            nn.ReLU(),
            nn.LayerNorm(features_dim)
        )

    def forward(self, observations: dict) -> torch.Tensor:
        board_features = self.board_net(observations['board'].float())
        return board_features

# === CALLBACK ===
class EnhancedTrainingLogger(BaseCallback):
    def __init__(self, filename=LOG_PATH):
        super().__init__()
        self.filename = filename
        self.episode_rewards = []
        self.current_episode_rewards = []
        self.valid_moves = 0
        self.total_moves = 0
        self.episode_count = 0
        self.last_log_time = datetime.datetime.now()
        
        # Initialize CSV with headers
        with open(self.filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp",
                "episode",
                "total_steps",
                "episode_reward",
                "avg_reward_100",
                "valid_move_pct",
                "episode_length",
                "time_elapsed"
            ])

    def _on_step(self) -> bool:
        # Track moves and episode completion
        infos = self.locals.get('infos', [])
        for info in infos:
            if 'valid_move' in info:
                self.total_moves += 1
                if info['valid_move']:
                    self.valid_moves += 1
            
            if 'episode' in info:
                # Episode completed, log all metrics
                self.episode_count += 1
                episode_reward = info['episode']['r']
                episode_length = info['episode']['l']
                self.episode_rewards.append(episode_reward)
                
                # Calculate metrics
                avg_reward = np.mean(self.episode_rewards[-100:]) if self.episode_rewards else 0
                valid_pct = (self.valid_moves / self.total_moves) if self.total_moves > 0 else 0
                current_time = datetime.datetime.now()
                time_elapsed = (current_time - self.last_log_time).total_seconds()
                
                # Write to CSV
                with open(self.filename, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        current_time.strftime("%Y-%m-%d %H:%M:%S"),
                        self.episode_count,
                        self.num_timesteps,
                        episode_reward,
                        avg_reward,
                        valid_pct,
                        episode_length,
                        time_elapsed
                    ])
                
                # Print summary
                print(
                    f"\nEpisode {self.episode_count} | "
                    f"Steps: {self.num_timesteps} | "
                    f"Reward: {episode_reward:.2f} | "
                    f"Avg100: {avg_reward:.2f} | "
                    f"Valid: {valid_pct:.1%} | "
                    f"Length: {episode_length} | "
                    f"Time: {time_elapsed:.1f}s"
                )
                
                # Reset counters
                self.valid_moves = 0
                self.total_moves = 0
                self.last_log_time = current_time
        
        return True

# === MASK FUNCTION ===
def safe_mask_fn(env) -> np.ndarray:
    obs = env.get_observation()
    return obs['action_mask'].astype(bool)

# === MODEL CREATION ===
def create_model(env):
    policy_kwargs = {
        "features_extractor_class": RobustMaskedFeatureExtractor,
        "features_extractor_kwargs": {"features_dim": 256},
        "net_arch": [dict(pi=[128, 64], vf=[128, 64])],
        "activation_fn": torch.nn.ReLU,
        "optimizer_class": torch.optim.AdamW,
        "optimizer_kwargs": {"eps": 1e-6, "weight_decay": 1e-4}
    }
    return MaskablePPO(
        MaskableActorCriticPolicy,
        env,
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=128,
        n_epochs=10,
        gamma=0.95,
        clip_range=0.2,
        ent_coef=0.02,
        policy_kwargs=policy_kwargs,
        device="auto",
        verbose=1,
        target_kl=0.05,
        max_grad_norm=0.5
    )

# === TRAIN FUNCTION ===
def train():
    env = CheckersEnv()
    env = ActionMasker(env, safe_mask_fn)
    vec_env = DummyVecEnv([lambda: env])
    vec_env = VecMonitor(vec_env)

    model = None
    if os.path.exists(MODEL_PATH + ".zip"):
        try:
            model = MaskablePPO.load(MODEL_PATH, env=vec_env)
            print("✅ Loaded existing model and continuing training")
        except Exception as e:
            print(f"❌ Failed to load model: {e}")

    if model is None:
        print("📦 Creating new model")
        model = create_model(vec_env)

    logger = EnhancedTrainingLogger()

    try:
        model.learn(
            total_timesteps=500_000,
            callback=logger,
            log_interval=1,  # Show progress every step
            progress_bar=True,
            reset_num_timesteps=False
        )
    except Exception as e:
        print(f"🚨 Error: {e}")
        crash_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        crash_path = os.path.join(MODEL_DIR, f"crash_model_{crash_time}")
        model.save(crash_path)
        print(f"💾 Crash recovery model saved to: {crash_path}")
    finally:
        model.save(MODEL_PATH)
        print(f"💾 Final model saved to: {MODEL_PATH}")

if __name__ == "__main__":
    train()