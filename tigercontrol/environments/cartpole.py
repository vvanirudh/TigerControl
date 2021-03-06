"""
Non-PyBullet implementation of CartPole
"""
import jax
import jax.numpy as np
import jax.random as random

import tigercontrol
from tigercontrol.utils import generate_key
from tigercontrol.environments import Environment

# necessary for rendering
from gym.envs.classic_control import rendering

# Losses
C_x, C_u = (np.diag(np.array([0.2, 0.05, 1.0, 0.05])), np.diag(np.array([0.05])))
cartpole_basic_loss = jax.jit(lambda x, u: x.T @ C_x @ x + u.T @ C_u @ u)

class CartPole(Environment):
    """
    Description:
        A pole is attached by an un-actuated joint to a cart, which moves along a frictionless track. 
        The pendulum starts upright, and the goal is to prevent it from falling over by increasing 
        and reducing the cart's velocity.
    """
    
    metadata = {
        'render.modes': ['human', 'rgb_array'],
        'video.frames_per_second' : 50
    }

    def __init__(self, **kwargs):
        self.rollout_controller = None
        self.gravity = 9.8
        self.masscart = 1.0
        self.masspole = 0.1
        self.total_mass = (self.masspole + self.masscart)
        self.length = 0.5 # actually half the pole's length
        self.polemass_length = (self.masspole * self.length)
        self.force_mag = 10.0
        self.tau = 0.02  # seconds between state updates

        # Angle at which to fail the episode
        self.theta_threshold_radians = 15 * 2 * np.pi / 360
        self.x_threshold = 2.4

        self.action_space = (1,)
        self.observation_space = (4,)
        self.n, self.m = 4, 1
        self.viewer = None
        self._state = None

        def _dynamics(x_0, u): # dynamics
            # x_0, u = np.squeeze(x_0, axis=1), np.squeeze(u, axis=1)
            x, x_dot, theta, theta_dot = np.split(x_0, 4)
            force = self.force_mag * np.clip(u, -1.0, 1.0) # iLQR may struggle with clipping due to lack of gradient
            costh = np.cos(theta)
            sinth = np.sin(theta)
            temp = (force + self.polemass_length * theta_dot * theta_dot * sinth) / self.total_mass
            thetaacc = (self.gravity*sinth - costh*temp) / (self.length * (4.0/3.0 - self.masspole*costh*costh / self.total_mass))
            xacc = temp - self.polemass_length * thetaacc * costh / self.total_mass
            x  = x + self.tau * x_dot # use euler integration by default
            x_dot = x_dot + self.tau * xacc
            theta = theta + self.tau * theta_dot
            theta_dot = theta_dot + self.tau * thetaacc
            state = np.hstack((x, x_dot, theta, theta_dot))
            return state
        self._dynamics = jax.jit(_dynamics) # MUST store as self._dynamics for default rollout implementation to work
        # C_x, C_u = (np.diag(np.array([0.2, 0.05, 1.0, 0.05])), np.diag(np.array([0.05])))
        # self._loss = jax.jit(lambda x, u: x.T @ C_x @ x + u.T @ C_u @ u) # MUST store as self._loss
        self._loss = kwargs.get('loss')

        # stack the jacobians of environment dynamics gradient
        jacobian = jax.jacrev(self._dynamics, argnums=(0,1))
        # jacobian[0], jacobian[1] = np.squeeze(jacobian[0], axis=(1,3)), np.squeeze(jacobian[1], axis=(1,3))
        self._dynamics_jacobian = jax.jit(lambda x, u: np.hstack(jacobian(x, u)))
        '''
        def dyn_jac_aux(x,u):
            j = jacobian(x,u)
            return np.hstack((np.squeeze(j[0], axis=(1,3)), np.squeeze(j[1], axis=(1,3))))
        self._dynamics_jacobian = jax.jit(dyn_jac_aux)'''

        # stack the gradients of environment loss
        loss_grad = jax.grad(self._loss, argnums=(0,1))
        self._loss_grad = jax.jit(lambda x, u: np.hstack(loss_grad(x, u)))

        # block the hessian of environment loss
        block_hessian = lambda A: np.vstack([np.hstack([A[0][0], A[0][1]]), np.hstack([A[1][0], A[1][1]])])
        hessian = jax.hessian(self._loss, argnums=(0,1))
        self._loss_hessian = jax.jit(lambda x, u: block_hessian(hessian(x,u)))
        '''
        def _rollout(act, dyn, x_0, T):
            def f(x, i):
                u = act(x)
                x_next = dyn(x, u)
                return x_next, np.hstack((x, u))
            _, trajectory = jax.lax.scan(f, x_0, np.arange(T))
            return trajectory
        self._rollout = jax.jit(_rollout, static_argnums=(0,1,3))'''
    '''
    def get_state_dim(self):
        return self.n

    def get_action_dim(self):
        return self.m

    def get_dynamics(self):
        return self._dynamics

    def get_state(self):
        return self._state

    def get_dynamics_jacobian(self):
        return self._dynamics_jacobian

    def get_loss(self):
        return self._loss

    def get_loss_grad(self):
        return self._loss_grad

    def get_loss_hessian(self):
        return self._loss_hessian'''

    def reset(self):
        """ Description: Reset the environment and return the start state """
        self._state = random.uniform(generate_key(),shape=(4,), minval=-0.05, maxval=0.05)
        #self._state = np.array([0.0, 0.03, 0.03, 0.03]) # reproducible results
        return self._state
        
    def step(self, action):
        """ Description: updates internal state <- dynamcics(state, action) and returns state, cost, and done boolean """
        # if type(action) == np.ndarray: action = action[0]
        old_state = self._state
        self._state = self._dynamics(self._state, action)
        x, theta = self._state[0], self._state[2]
        x_lim, th_lim = self.x_threshold, self.theta_threshold_radians
        # done = bool(x < -x_lim or x > x_lim or theta < -th_lim or theta > th_lim)
        # cost = self._loss(old_state, action)
        return self._state

    '''
    def rollout(self, controller, T, dynamics_grad=False, loss_grad=False, loss_hessian=False):
        # Description: Roll out trajectory of given baby_controller.
        if self.rollout_controller != controller: self.rollout_controller = controller
        x = self._state
        trajectory = self._rollout(controller.get_action, self._dynamics, x, T)
        transcript = {'x': trajectory[:,:self.n], 'u': trajectory[:,self.n:]}

        # optional derivatives
        if dynamics_grad: transcript['dynamics_grad'] = []
        if loss_grad: transcript['loss_grad'] = []
        if loss_hessian: transcript['loss_hessian'] = []
        for x, u in zip(transcript['x'], transcript['u']):
            if dynamics_grad: transcript['dynamics_grad'].append(self._dynamics_jacobian(x, u))
            if loss_grad: transcript['loss_grad'].append(self._loss_grad(x, u))
            if loss_hessian: transcript['loss_hessian'].append(self._loss_hessian(x, u))
        return transcript'''

    def render(self, mode='human'):
        """ Description: Renders on screen an image of the current cartpole state """
        screen_width = 600
        screen_height = 400

        world_width = self.x_threshold*2
        scale = screen_width/world_width
        carty = 100 # TOP OF CART
        polewidth = 10.0
        polelen = scale * (2 * self.length)
        cartwidth = 50.0
        cartheight = 30.0

        if self.viewer is None:
            self.viewer = rendering.Viewer(screen_width, screen_height)
            l,r,t,b = -cartwidth/2, cartwidth/2, cartheight/2, -cartheight/2
            axleoffset =cartheight/4.0
            cart = rendering.FilledPolygon([(l,b), (l,t), (r,t), (r,b)])
            self.carttrans = rendering.Transform()
            cart.add_attr(self.carttrans)
            self.viewer.add_geom(cart)
            l,r,t,b = -polewidth/2,polewidth/2,polelen-polewidth/2,-polewidth/2
            pole = rendering.FilledPolygon([(l,b), (l,t), (r,t), (r,b)])
            pole.set_color(.8,.6,.4)
            self.poletrans = rendering.Transform(translation=(0, axleoffset))
            pole.add_attr(self.poletrans)
            pole.add_attr(self.carttrans)
            self.viewer.add_geom(pole)
            self.axle = rendering.make_circle(polewidth/2)
            self.axle.add_attr(self.poletrans)
            self.axle.add_attr(self.carttrans)
            self.axle.set_color(.5,.5,.8)
            self.viewer.add_geom(self.axle)
            self.track = rendering.Line((0,carty), (screen_width,carty))
            self.track.set_color(0,0,0)
            self.viewer.add_geom(self.track)
            self._pole_geom = pole
        if self._state is None: return None

        # Edit the pole polygon vertex
        pole = self._pole_geom
        l,r,t,b = -polewidth/2,polewidth/2,polelen-polewidth/2,-polewidth/2
        pole.v = [(l,b), (l,t), (r,t), (r,b)]
        x = self._state
        cartx = x[0]*scale+screen_width/2.0 # MIDDLE OF CART
        self.carttrans.set_translation(cartx, carty)
        self.poletrans.set_rotation(-x[2])
        return self.viewer.render(return_rgb_array = mode=='rgb_array')

    def close(self):
        """ Description: Close the environment and return memory """
        if self.viewer:
            self.viewer.close()
            self.viewer = None



