"""
An example to run of the half cheetah gym environment with random gaits.
"""

import tigercontrol
import numpy as np
import time

def test_humanoid(steps=1000, verbose=False):
    environment = tigercontrol.environment("PyBullet-Humanoid")
    environment.reset(render=verbose)

    sum_reward = 0
    amplitude1 = 0.5
    amplitude2 = 0.5
    speed = 40

    action = np.random.normal(size=environment.action_space)

    for step_counter in range(steps):
        action = 0.95 * action + np.random.normal(size=environment.action_space)
        _, reward, done, _ = environment.step(action)
        time.sleep(1. / 100.)

        sum_reward += reward
        if done:
            environment.reset()
            
    environment.close()
    print("test_humanoid passed")


if __name__ == '__main__':
    #test_humanoid(verbose=True)
    pass

