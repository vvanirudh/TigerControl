# test the Autogressor model class

import ctsb
import jax.numpy as np
import matplotlib.pyplot as plt
from ctsb.models.optimizers import *

def test_autoregressor(steps=1000, show_plot=True):
    T = steps 
    p, q = 3, 3
    problem = ctsb.problem("ARMA-v0")
    cur_x = problem.initialize(p, q)

    model = ctsb.model("AutoRegressor")
    model.initialize(p, optimizer = Adam)
    loss = lambda y_true, y_pred: np.sum((y_true - y_pred)**2)
 
    results = []

    for i in range(T):
        cur_y_pred = model.predict(cur_x)
        #model.forecast(cur_x, 3)
        cur_y_true = problem.step()
        cur_loss = loss(cur_y_true, cur_y_pred)
        model.update(cur_y_true)
        cur_x = cur_y_true
        results.append(cur_loss)

    if show_plot:
        plt.plot(results)
        plt.title("Autoregressive model on ARMA problem")
        plt.show(block=False)
        plt.pause(3)
        plt.close()
    print("test_autoregressor passed")
    return

if __name__=="__main__":
    test_autoregressor()