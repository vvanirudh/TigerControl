from ctsb.problems.control.tests.test_lds import test_lds
from ctsb.problems.control.tests.test_lstm_output import test_lstm
from ctsb.problems.control.tests.test_rnn_output import test_rnn
from ctsb.problems.control.tests.test_cartpole import test_cartpole
from ctsb.problems.control.tests.test_cartpole_double import test_cartpole_double
from ctsb.problems.control.tests.test_cartpole_swingup import test_cartpole_swingup
from ctsb.problems.control.tests.test_simulator_wrapper import test_simulator_wrapper
from ctsb.problems.control.tests.test_kuka import test_kuka
from ctsb.problems.control.tests.test_kuka_diverse import test_kuka_diverse
from ctsb.problems.control.tests.test_minitaur import test_minitaur
from ctsb.problems.control.tests.test_ant import test_ant
from ctsb.problems.control.tests.test_humanoid import test_humanoid


def run_all_tests(steps=1000, show=False):
    print("\nrunning all control problems tests...\n")
    test_lds(steps=steps, show_plot=show)
    test_lstm(steps=steps, show_plot=show)
    test_rnn(steps=steps, show_plot=show)
    print("\nall control problems tests passed\n")
    print("\nrunning all pybullet problems tests...\n")
    test_simulator_wrapper(verbose=show)
    test_cartpole(verbose=show)
    test_cartpole_swingup(verbose=show)
    test_cartpole_double(verbose=show)
    test_kuka(verbose=show)
    test_kuka_diverse(verbose=show)
    test_minitaur(verbose=show)
    test_ant(verbose=show)
    test_humanoid(verbose=show)
    print("\nall pybullet problems tests passed\n")
  
if __name__ == "__main__":
    run_all_tests(show=True)