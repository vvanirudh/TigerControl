import tigercontrol
from tigercontrol.methods.optimizers.adam import Adam
from tigercontrol.methods.optimizers.losses import mse
import matplotlib.pyplot as plt

def test_adam(show=False):

    environment = tigercontrol.environment('ARMA-v0')
    x = environment.initialize(p=2,q=0)

    method = tigercontrol.method('LSTM')
    method.initialize(n=1, m=1, l=3, h=10, optimizer=Adam) # initialize with class
    method.predict(1.0) # call methods to verify it works
    method.update(1.0)

    optimizer = Adam(learning_rate=0.1)
    method = tigercontrol.method('LSTM')
    method.initialize(n=1, m=1, l=3, h=10, optimizer=optimizer) # reinitialize with instance

    loss = []
    for t in range(1000):
        y_pred = method.predict(x)
        y_true = environment.step()
        loss.append(mse(y_pred, y_true))
        method.update(y_true)
        x = y_true

    if show:
        plt.plot(loss)
        plt.show(block=False)
        plt.pause(3)
        plt.close()
    print("test_adam passed")



if __name__ == "__main__":
    test_adam(show=True)