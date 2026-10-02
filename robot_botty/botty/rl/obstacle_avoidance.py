"""
Reinforcement Learning — esquiva autonoma de obstaculos.
Usa Stable Baselines3 PPO con un entorno Gymnasium personalizado.

Arquitectura:
  Observation: [sonar_front, sonar_left, sonar_right, speed, turn]
  Action: [speed (-1..1), turn (-1..1)]
  Reward: +1 por avanzar, -1 por colision, +0.5 por esquiva

Entrenamiento (en PC potente):
  python -m botty.rl.obstacle_avoidance --train

Inferencia (en la Pi):
  cargar modelo guardado y llamar .predict(obs)
"""

import os
import pickle
import numpy as np
from pathlib import Path
from botty.config import Config


class ObstacleAvoidanceRL:
    def __init__(self):
        self.model = None
        self._ready = False
        self.model_path = Path(Config.RL_MODEL_PATH)

    @property
    def ready(self) -> bool:
        return self._ready

    def load(self):
        """Carga modelo pre-entrenado."""
        try:
            from stable_baselines3 import PPO
            if self.model_path.exists():
                self.model = PPO.load(str(self.model_path))
                self._ready = True
                print(f"  [RL] Modelo cargado: {self.model_path}")
                return True
            else:
                print(f"  [RL] No se encuentra modelo en {self.model_path}")
                print("  [RL] Entrena uno con: python -m botty.rl.obstacle_avoidance --train")
                return False
        except ImportError:
            print("  [RL] stable-baselines3 no instalado")
            return False
        except Exception as e:
            print(f"  [RL] Error cargando modelo: {e}")
            return False

    def predict(self, sonar_front: float, sonar_left: float,
                sonar_right: float, speed: float = 0.0,
                turn: float = 0.0) -> tuple[float, float]:
        """Predice (speed, turn) basado en sensores.
        speed, turn: -1..1"""
        if not self._ready:
            return 0.0, 0.0

        try:
            obs = np.array([[sonar_front, sonar_left, sonar_right, speed, turn]],
                          dtype=np.float32)
            obs = np.clip(obs / 100.0, 0, 1)  # Normalize distances
            action, _ = self.model.predict(obs, deterministic=True)
            return float(action[0][0]), float(action[0][1])
        except Exception as e:
            print(f"  [RL] Error en predict: {e}")
            return 0.0, 0.0


class BottyEnv:
    """
    Entorno Gymnasium para entrenar Botty en simulacion.
    Observation: [sonar_front, sonar_left, sonar_right, speed, turn] (normalizado)
    Action: [speed, turn] continuo -1..1
    """
    def __init__(self):
        try:
            import gymnasium as gym
            from gymnasium import spaces
        except ImportError:
            raise ImportError("gymnasium no instalado: pip install gymnasium")

        self.observation_space = spaces.Box(
            low=0, high=1, shape=(5,), dtype=np.float32
        )
        self.action_space = spaces.Box(
            low=-1, high=1, shape=(2,), dtype=np.float32
        )
        self.state = np.zeros(5, dtype=np.float32)
        self.step_count = 0

    def reset(self):
        self.state = np.random.uniform(0.3, 1.0, size=(5,)).astype(np.float32)
        self.step_count = 0
        return self.state, {}

    def step(self, action):
        self.step_count += 1
        speed, turn = float(action[0]), float(action[1])

        # Simulate sensor readings based on action
        front = self.state[0] - speed * 0.1 + np.random.normal(0, 0.02)
        front = np.clip(front, 0.05, 1.0)

        left = self.state[1] - turn * 0.05 + np.random.normal(0, 0.02)
        left = np.clip(left, 0.05, 1.0)

        right = self.state[2] + turn * 0.05 + np.random.normal(0, 0.02)
        right = np.clip(right, 0.05, 1.0)

        self.state = np.array([front, left, right, speed * 0.5 + 0.5, turn * 0.5 + 0.5],
                             dtype=np.float32)

        # Reward
        collision = front < 0.1
        escaped = front > 0.8 and abs(turn) > 0.3
        moving = abs(speed) > 0.2

        reward = 0.0
        if moving:
            reward += speed * 0.5
        if collision:
            reward -= 1.0
        if escaped:
            reward += 0.5

        done = collision or self.step_count > 200
        return self.state, reward, done, False, {}


def train():
    """Entrena un modelo PPO (ejecutar en PC, no en Pi)."""
    try:
        from stable_baselines3 import PPO
        from stable_baselines3.common.callbacks import EvalCallback

        env = BottyEnv()
        model = PPO(
            "MlpPolicy",
            env,
            verbose=1,
            learning_rate=3e-4,
            n_steps=2048,
            batch_size=64,
            n_epochs=10,
            gamma=0.99,
            ent_coef=0.01,
        )

        out_dir = Path(Config.RL_MODEL_PATH).parent
        out_dir.mkdir(parents=True, exist_ok=True)

        model.learn(total_timesteps=200_000)
        model.save(str(Config.RL_MODEL_PATH))
        print(f"  [RL] Modelo guardado en {Config.RL_MODEL_PATH}")
    except Exception as e:
        print(f"  [RL] Error entrenando: {e}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", action="store_true", help="Entrenar modelo PPO")
    args = parser.parse_args()
    if args.train:
        train()
    else:
        print("Usa --train para entrenar")
