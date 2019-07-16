"""
PyBullet Double Pendulum enviornment
"""
import gym
import pybullet_envs
from ctsb.problems.control.pybullet.pybullet_problem import PyBulletProblem
from ctsb.problems.control.pybullet.simulator_wrapper import SimulatorWrapper


class CartPoleDouble(PyBulletProblem):
    """
    Simulates a pendulum balanced on a cartpole.
    """
    def __init__(self):
        self.initialized = False

    def initialize(self, render=False):
        self.initialized = True
        self.env = gym.make("InvertedDoublePendulumBulletEnv-v0")
        if render:
            self.env.render(mode="human")
        self.sim = SimulatorWrapper(self.env)
        self.observation_space = self.env.observation_space
        self.action_space = self.env.action_space
        initial_obs = self.env.reset()
        return initial_obs

    def step(self, a):
        return self.sim.step(a)

    def render(self, mode='human', close=False):
        self.problem.render(mode=mode, close=close)

    def get_observation_space(self):
        return self.observation_space

    def get_action_space(self):
        return self.action_space


