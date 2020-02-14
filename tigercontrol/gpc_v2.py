
"""
Gradient Pertubation Controller

written by Paula Gradu, Elad Hazan and Anirudha Majumdar 
"""

import jax.numpy as np
import tigercontrol
from tigercontrol.controllers import Controller
from jax import grad,jit
import jax.random as random
from tigercontrol.utils import generate_key
import jax
import scipy
from tigercontrol.controllers import LQR

# GPC definition
#### Personal note: ALT-GPC????
class GPC_v2(Controller):
    def __init__(self, A, B, Q = None, R = None, cost_fn = None, \
                    H = 3, HH = 3, lr = 0.001, include_bias = True):
        """
        Description: Initialize the dynamics of the model
        Args:
            A,B (float/numpy.ndarray): system dynamics
            H (postive int): history of the controller 
            HH (positive int): history of the system 
            K (float/numpy.ndarray): Starting policy (optional). Defaults to LQR gain.
            x (float/numpy.ndarray): initial state (optional)
        """

        n, m = B.shape # State & Action Dimensions

        #### PERSONAL NOTE: if these are None, automatically do sys id!!!!
        self.A, self.B = A, B # System Dynamics
        self.t = 1 # Time Counter (for decaying learning rate)
        #### PERSONAL NOTE: introduce lr schedule??
        self.lr, self.H = lr, H # Model Hyperparameters
        self.include_bias = include_bias

        # Model Parameters 
        # initial linear policy / perturbation contributions / bias
        self.K, self.M, self.bias = LQR(A, B, Q, R).K, np.zeros((H, m, n)), np.zeros((m, 1))

        # Past H + HH noises and H + HH + 1 states for unrolling
        self.w = np.zeros((H+HH, n, 1))
        self.x = np.zeros((H+HH+1, n, 1))

        # past action
        self.u = zeros((m, 1))

        # The Policy Cost Function
        def policy_loss(M, bias, w, x0, cost_t = cost_fn):
            y = x0
            for h in range(HH - 1):
                v = -self.K @ y + np.tensordot(M, w[h : h + H], axes = ([0, 2], [0, 1])) + bias
                y = A @ y + B @ v + w[h + H]
            # Don't update state at the end    
            v = -self.K @ y + np.tensordot(M, w[h : h + H], axes = ([0, 2], [0, 1])) + bias
            return  cost_fn(y, v)

        self.grad = grad(policy_loss, (0, 1))

        # If cost function stays the same throughout run, jit the gradient for efficiency
        if(cost_fn is not None):  
            self.grad = jit(self.grad)

    def update(self, cost = None):
        # 1. Get gradients
        delta_M, delta_bias = self.grad(self.M, self.bias, self.w, self.x[0], cost)

        # 2. Execute updates
        self.M -= self.lr/np.sqrt(self.t) * delta_M
        self.bias -= self.lr/np.sqrt(self.t) * delta_bias

    def get_action(self, x):
        # 1. Get new noise (will be located at w[-1])
        self.w = jax.ops.index_update(self.w, 0, x - self.A @ self.x[-1] - self.B @ self.u)
        self.w = np.roll(self.w, -1, axis = 0)

        # 2. Update x (new at x[-1] / oldest at x[0])
        self.x = jax.ops.index_update(self.x, 0, x)
        self.x = np.roll(self.x, -1, axis = 0)

        # 3. Update t
        self.t = self.t + 1 ## SHOULD THIS BE IN UPDATE INSTEAD ?

        # 4. Compute and return new action
        self.u = -self.K @ x + np.tensordot(self.M, self.w, \
            axes = ([0, 2], [0, 1])) + self.bias * self.include_bias

        return self.u
