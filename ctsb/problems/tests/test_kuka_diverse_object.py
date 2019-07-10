"""Runs a random policy for the random object KukaDiverseObjectEnv.
"""

import os, inspect
import numpy as np

# currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
# parentdir = os.path.dirname(os.path.dirname(currentdir))
# os.sys.path.insert(0, parentdir)

import gym
from ctsb.problems.control.pybullet import Kuka_diverse_object
# from pybullet_envs.bullet.kuka_diverse_object_gym_env import KukaDiverseObjectEnv
from gym import spaces


class ContinuousDownwardBiasPolicy(object):
  """Policy which takes continuous actions, and is biased to move down.
  """

  def __init__(self, height_hack_prob=0.9):
    """Initializes the DownwardBiasPolicy.

    Args:
        height_hack_prob: The probability of moving down at every move.
    """
    self._height_hack_prob = height_hack_prob
    self._action_space = spaces.Box(low=-1, high=1, shape=(5,))

  def sample_action(self, obs, explore_prob):
    """Implements height hack and grasping threshold hack.
    """
    dx, dy, dz, da, close = self._action_space.sample()
    if np.random.random() < self._height_hack_prob:
      dz = -1
    return [dx, dy, dz, da, 0.5]


def main():

  problem = Kuka_diverse_object()
  obs = problem.initialize()
  policy = ContinuousDownwardBiasPolicy()

  while True:
    done =  False
    episode_rew = 0
    while not done:
      problem.render(mode='human')
      act = policy.sample_action(obs, .1)
      obs, rew, done, _ = problem.step(act)
      episode_rew += rew
    print("Episode reward", episode_rew)


if __name__ == '__main__':
  main()