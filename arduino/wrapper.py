from heater import Heater
from optimizer import Optimizer
from skopt.space import Integer

class Wrapper:
    """
    Wrapper for the heater and optimizer
    """
    def __init__(self):
        self.controller = Heater()
        self.optimizer = Optimizer(self)
        self.target_temp = None

    def evaluate(self, seq):
        """
        Evaluate the temperatures and time for a given pwm sequence
        """
        temp_seq = self.controller.write_and_read(seq)

        # process temperature sequence from heater (rtn) to get the time
        tolerance = 1.0  # ±1 degree
        stability_duration = 30  # 30 secs
        max_duration = 5 * 60  # 20 mins
        stability_start_time = None

        for i, temp in enumerate(temp_seq):
            elapsed_time = i * 2  # each temp reading is 2 seconds apart

            if elapsed_time >= max_duration:
                return max_duration

            if abs(temp - self.target_temp) <= tolerance:
                if stability_start_time is None:
                    stability_start_time = elapsed_time
                elif elapsed_time - stability_start_time >= stability_duration:
                    return elapsed_time
            else:
                stability_start_time = None

        return max_duration

    def run(self, target_temp):
        """
        Run optimization
        """
        self.target_temp = target_temp
        pwm = Integer(0, 255)
        max_sequence_length = 5 * 60  # 20 mins
        space = [pwm] * max_sequence_length
        best_pwm_seq, best_time = self.optimizer.optimize(space)
        return best_pwm_seq, best_time
