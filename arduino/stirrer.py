from serial import Serial
from struct import pack
import time

class Stirrer:
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

    def set_stir(self, stir):
        self.device.write(b"\x03")
        self.device.write(pack("B", stir))

s = Stirrer()
while True:
    s.set_stir(0)
    time.sleep(3)
    s.set_stir(1)
    time.sleep(3)
