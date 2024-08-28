from serial import Serial
from struct import unpack, pack
import time
import math

# send pwm sequence, read temperature values
class Heater:
    """
    Class for heaters using Arduino
    """
    def __init__(self, com: str = None):
        self.device = None
        self.connect_arduino(com)

    def connect_arduino(self, com: str = None):
        """
        Creates serial connection
        """
        if com is None:
            self.device = Serial("COM5", baudrate=9600, timeout=1)
        else:
            self.device = Serial(com, baudrate=9600, timeout=1)
        time.sleep(2)

    def write_and_read(self, seq):
        """
        Send PWM sequence to Arduino
        """
        temp_seq = []
        for pwm in seq:
            print(pwm)
            # write
            self.device.write(b"\x01")
            self.device.write(pack("B", pwm))
            time.sleep(3)  # apply each PWM value for 2 seconds

            # read
            self.device.write(b"\x02")
            time.sleep(3)
            analog = self.device.read_all()
            voltage = int(unpack(">H", analog)[0]) * 5 / 0xffff  # big-endian for unsigned short
            resistance = 10000 / (5.0 / voltage - 1.0)
            # thermistor equation using 3435 beta value to find the temp
            temp_kelvin = 1.0 / (math.log(resistance / 10000) / 3435 + 1.0 / 298)
            temp_celsius = temp_kelvin - 273.15
            print(temp_celsius)
            temp_seq.append(temp_celsius)

        return temp_seq
