"""
Enhanced RL trainer — curriculum learning, hyperparameter search, evaluation.
"""

import time
import json
import random
import math
import os
from pathlib import Path
from collections import deque

from botty.config import Config


try:
    import numpy as np
    import gymnasium as gym
    from gymnasium import spaces
    HAVE_RL_DEPS = True
except ImportError:
    HAVE_RL_DEPS = False
    np = None

try:
    from stable_baselines3 import PPO
    from stable_baselines3.common.callbacks import BaseCallback
    from stable_baselines3.common.vec_env import DummyVecEnv
    from stable_baselines3.common.monitor import Monitor
    HAVE_SB3 = True
except ImportError:
    HAVE_SB3 = False


if HAVE_RL_DEPS:

    class ObstacleAvoidanceEnv(gym.Env):
        """Robot obstacle avoidance simulation environment."""

        def __init__(self, max_steps=200, difficulty=1.0):
            super().__init__()
            self.max_steps = max_steps
            self.difficulty = difficulty
            self.observation_space = spaces.Box(
                low=0.0, high=500.0, shape=(3,), dtype=np.float32
            )
            self.action_space = spaces.Box(
                low=-1.0, high=1.0, shape=(2,), dtype=np.float32
            )
            self.step_count = 0
            self.position = [0.0, 0.0]
            self.obstacles = []
            self.goal = [10.0, 0.0]
            self.prev_distance = 0.0
            self.consecutive_crashes = 0

        def reset(self, seed=None, options=None):
            super().reset(seed=seed)
            self.step_count = 0
            self.position = [0.0, 0.0]
            self.prev_distance = math.hypot(
                self.goal[0] - self.position[0], self.goal[1] - self.position[1]
            )
            self._generate_obstacles()
            return self._get_obs(), {}

        def _generate_obstacles(self):
            self.obstacles = []
            n_obs = int(3 + self.difficulty * 5)
            for _ in range(n_obs):
                x = random.uniform(2.0, 12.0)
                y = random.uniform(-3.0, 3.0)
                r = random.uniform(0.3, 0.8)
                self.obstacles.append({"x": x, "y": y, "r": r})

        def _get_obs(self):
            front = min(
                [math.hypot(o["x"] - self.position[0] - 1, o["y"] - self.position[1])
                 for o in self.obstacles], default=500.0
            )
            left = min(
                [math.hypot(o["x"] - self.position[0], o["y"] - self.position[1] + 1)
                 for o in self.obstacles], default=500.0
            )
            right = min(
                [math.hypot(o["x"] - self.position[0], o["y"] - self.position[1] - 1)
                 for o in self.obstacles], default=500.0
            )
            return np.array([front, left, right], dtype=np.float32) / 100.0

        def step(self, action):
            self.step_count += 1
            speed = float(action[0])
            turn = float(action[1])
            new_x = self.position[0] + speed * 0.2
            new_y = self.position[1] + turn * 0.15
            self.position = [new_x, new_y]
            obs = self._get_obs()
            reward = self._compute_reward()
            terminated = self._check_crash() or self._check_goal()
            truncated = self.step_count >= self.max_steps
            return obs, reward, terminated, truncated, {}

        def _compute_reward(self):
            dist = math.hypot(
                self.goal[0] - self.position[0], self.goal[1] - self.position[1]
            )
            reward = (self.prev_distance - dist) * 2.0
            self.prev_distance = dist
            for o in self.obstacles:
                d = math.hypot(o["x"] - self.position[0], o["y"] - self.position[1])
                if d < o["r"] + 0.5:
                    reward -= 5.0
                    self.consecutive_crashes += 1
                elif d < o["r"] + 1.0:
                    reward -= 2.0
            if abs(self.position[1]) > 3.0:
                reward -= 1.0
            reward -= 0.1
            return reward

        def _check_crash(self) -> bool:
            for o in self.obstacles:
                d = math.hypot(o["x"] - self.position[0], o["y"] - self.position[1])
                if d < o["r"] + 0.2:
                    return True
            return False

        def _check_goal(self) -> bool:
            d = math.hypot(self.goal[0] - self.position[0], self.goal[1] - self.position[1])
            return d < 0.5

        def render(self):
            pass


    class ProgressCallback(BaseCallback):
        def __init__(self, verbose=0):
            super().__init__(verbose)
            self.episode_rewards = deque(maxlen=100)
            self.episode_lengths = deque(maxlen=100)
            self.start_time = time.time()

        def _on_step(self) -> bool:
            if "episode" in self.locals.get("infos", [{}])[0]:
                info = self.locals["infos"][0]["episode"]
                self.episode_rewards.append(info["r"])
                self.episode_lengths.append(info["l"])
                if len(self.episode_rewards) % 10 == 0:
                    avg_r = np.mean(self.episode_rewards)
                    avg_l = np.mean(self.episode_lengths)
                    elapsed = time.time() - self.start_time
                    print(
                        f"  [RL] Step {self.num_timesteps}: reward={avg_r:.2f}, "
                        f"len={avg_l:.1f}, time={elapsed:.0f}s"
                    )
            return True


    class RLTrainer:
        def __init__(self, model_dir=None):
            self.model_dir = Path(model_dir or Config.RL_MODEL_PATH).parent
            self.model_dir.mkdir(parents=True, exist_ok=True)
            self.env = None
            self.model = None
            self.best_reward = -float("inf")
            self.training_history = []

        def make_env(self, difficulty=1.0, max_steps=200):
            def _init():
                return Monitor(ObstacleAvoidanceEnv(max_steps=max_steps, difficulty=difficulty))
            return DummyVecEnv([_init])

        def train_curriculum(self, stages=3, steps_per_stage=50000):
            if not HAVE_SB3:
                print("  [RL] stable-baselines3 no instalado")
                return None
            for stage in range(stages):
                difficulty = 0.5 + stage * 0.5
                print(f"\n  [RL] Curriculum stage {stage + 1}/{stages}, "
                      f"dificultad: {difficulty:.1f}")
                self.env = self.make_env(difficulty=difficulty)
                if self.model is None:
                    self.model = PPO(
                        "MlpPolicy", self.env,
                        learning_rate=3e-4, n_steps=2048, batch_size=64,
                        n_epochs=10, gamma=0.99, gae_lambda=0.95,
                        clip_range=0.2, ent_coef=0.01, verbose=0,
                    )
                callback = ProgressCallback()
                self.model.learn(
                    total_timesteps=steps_per_stage,
                    callback=callback,
                    reset_num_timesteps=(stage == 0),
                )
                model_path = self.model_dir / f"ppo_botty_stage{stage}.zip"
                self.model.save(str(model_path))
                print(f"  [RL] Modelo guardado: {model_path}")
            final_path = self.model_dir / "ppo_botty_final.zip"
            self.model.save(str(final_path))
            print(f"  [RL] Entrenamiento completado: {final_path}")
            return self.model

        def hyperparameter_search(self, trials=10, steps=20000):
            if not HAVE_SB3:
                print("  [RL] stable-baselines3 no instalado")
                return None
            best_model = None
            best_reward = -float("inf")
            results = []
            for trial in range(trials):
                lr = 10 ** random.uniform(-5, -3)
                n_steps = random.choice([1024, 2048, 4096])
                batch_size = random.choice([32, 64, 128])
                gamma = random.uniform(0.9, 0.999)
                ent_coef = random.uniform(0.0, 0.05)
                print(f"\n  [RL] Trial {trial + 1}/{trials}")
                print(f"  [RL] lr={lr:.6f}, steps={n_steps}, batch={batch_size}")
                env = self.make_env(difficulty=1.0, max_steps=100)
                model = PPO(
                    "MlpPolicy", env,
                    learning_rate=lr, n_steps=n_steps, batch_size=batch_size,
                    gamma=gamma, ent_coef=ent_coef, verbose=0,
                )
                model.learn(total_timesteps=steps)
                rewards = []
                for _ in range(20):
                    obs = env.reset()
                    ep_reward = 0.0
                    done = False
                    while not done:
                        action, _ = model.predict(obs, deterministic=True)
                        obs, r, done, _ = env.step(action)
                        ep_reward += r[0]
                    rewards.append(ep_reward)
                avg_reward = np.mean(rewards)
                results.append({
                    "trial": trial, "lr": lr, "n_steps": n_steps,
                    "batch_size": batch_size, "gamma": gamma,
                    "ent_coef": ent_coef, "avg_reward": avg_reward,
                })
                print(f"  [RL] Avg reward: {avg_reward:.2f}")
                if avg_reward > best_reward:
                    best_reward = avg_reward
                    best_model = model
                    model.save(str(self.model_dir / "ppo_botty_best_hp.zip"))
            with open(self.model_dir / "hp_search_results.json", "w") as f:
                json.dump(results, f, indent=2)
            return best_model

        def evaluate(self, model_path=None, episodes=50):
            if not HAVE_SB3:
                return {}
            model_path = model_path or Config.RL_MODEL_PATH
            if not Path(model_path).exists():
                print(f"  [RL] Modelo no encontrado: {model_path}")
                return {}
            model = PPO.load(model_path)
            env = self.make_env(difficulty=1.5, max_steps=300)
            all_rewards = []
            all_lengths = []
            crashes = 0
            goals = 0
            for ep in range(episodes):
                obs = env.reset()
                ep_reward = 0.0
                ep_len = 0
                done = False
                while not done:
                    action, _ = model.predict(obs, deterministic=True)
                    obs, r, done, _ = env.step(action)
                    ep_reward += r[0]
                    ep_len += 1
                    if r[0] < -10:
                        crashes += 1
                all_rewards.append(ep_reward)
                all_lengths.append(ep_len)
                if ep_reward > 50:
                    goals += 1
            results = {
                "episodes": episodes,
                "avg_reward": float(np.mean(all_rewards)),
                "std_reward": float(np.std(all_rewards)),
                "avg_length": float(np.mean(all_lengths)),
                "crashes": crashes, "goals": goals,
                "goal_rate": goals / episodes,
            }
            print(f"  [RL] Evaluacion: {results}")
            return results

        def load_and_predict(self, front: float, left: float, right: float) -> tuple:
            if not HAVE_SB3:
                return 0.0, 0.0
            if self.model is None:
                model_path = Config.RL_MODEL_PATH
                if Path(model_path).exists():
                    self.model = PPO.load(model_path)
                else:
                    return 0.0, 0.0
            obs = np.array([[front / 100.0, left / 100.0, right / 100.0]], dtype=np.float32)
            action, _ = self.model.predict(obs, deterministic=True)
            return float(action[0][0]), float(action[0][1])


else:
    class RLTrainer:
        def __init__(self, model_dir=None): pass
        def make_env(self, **kw): return None
        def train_curriculum(self, **kw): print("  [RL] gymnasium no instalado"); return None
        def hyperparameter_search(self, **kw): print("  [RL] gymnasium no instalado"); return None
        def evaluate(self, **kw): print("  [RL] gymnasium no instalado"); return {}
        def load_and_predict(self, *a): return 0.0, 0.0


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Botty RL Trainer")
    parser.add_argument("--train", action="store_true", help="Train with curriculum")
    parser.add_argument("--search", action="store_true", help="Hyperparameter search")
    parser.add_argument("--evaluate", type=str, default=None, help="Evaluate model path")
    parser.add_argument("--stages", type=int, default=3)
    parser.add_argument("--steps", type=int, default=50000)
    parser.add_argument("--trials", type=int, default=10)
    args = parser.parse_args()
    trainer = RLTrainer()
    if args.train:
        trainer.train_curriculum(stages=args.stages, steps_per_stage=args.steps)
    elif args.search:
        trainer.hyperparameter_search(trials=args.trials)
    elif args.evaluate:
        trainer.evaluate(model_path=args.evaluate)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
