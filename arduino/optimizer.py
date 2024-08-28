from skopt import gp_minimize
# from sklearn.gaussian_process import GaussianProcessRegressor

class Optimizer:
    """
    Class to optimize PWM sequence
    """
    def __init__(self, wrapper):
        self.wrapper = wrapper

    def objective(self, seq):
        """
        Measure time for a given PWM sequence to reach stable target temperature
        """
        return self.wrapper.evaluate(seq)

    def optimize(self, space):
        """
        Optimize over the search space
        """
        result = gp_minimize(self.objective, space, n_calls=50, random_state=41)
        best_pwm_seq = result.x
        best_time = result.fun
        return best_pwm_seq, best_time
