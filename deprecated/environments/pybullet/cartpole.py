"""
PyBullet Pendulum enviornment
"""

from pybullet_envs.gym_pendulum_envs import InvertedPendulumBulletEnv
from tigercontrol.environments.deprecated.pybullet.pybullet_environment import PyBulletEnvironment


class CartPole(PyBulletEnvironment):
    """
    Description: Simulates a pendulum balanced on a cartpole.
    """

    compatibles = set(['CartPole', 'PyBullet'])
    
    def __init__(self):
        self.initialized = False

    def initialize(self, render=False):
        self.initialized = True
        self._env = InvertedPendulumBulletEnv()
        if render:
            self._env.render(mode="human")
        self.observation_space = self._env.observation_space.shape
        self.action_space = self._env.action_space.shape
        initial_obs = self._env.reset()
        return initial_obs

    def step(self, action):
        return self._env.step(action)

    def render(self, mode='human', close=False):
        self._env.render(mode=mode, close=close)
