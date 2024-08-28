from wrapper import Wrapper

w = Wrapper()
best_pwm_seq, best_time = w.run(40)
print(best_pwm_seq, best_time)

# # thermistor test
# import time
# import math
# from struct import unpack, pack
# from serial import Serial
#
# device = Serial("COM5", baudrate=9600, timeout=1)
# time.sleep(2)
# device.write(b"\x02")
# time.sleep(2)
# analog = device.read_all()
# voltage = unpack(">H", analog)[0] / 0xffff * 5  # big-endian for unsigned short
# print(voltage)
# resistance = 10000 / (5.0 / voltage - 1.0)
# # thermistor equation using 3435 beta value to find the temp
# temp_kelvin = 1.0 / (math.log(resistance / 10000) / 3435 + 1.0 / 298)
# temp_celsius = temp_kelvin - 273.15
# print(temp_celsius)
#
# device.write(b"\x01")
# device.write(pack("B", 2))
# time.sleep(2)
# print(device.read_all())
#
# while True:
#     device.write(b"\x01")
#     device.write(pack("B", 1))
#     time.sleep(3)
#     device.write(b"\x02")
#     time.sleep(2)
#     analog = device.read_all()
#     voltage = unpack(">H", analog)[0] / 0xffff * 5  # big-endian for unsigned short
#     print(voltage)
#     resistance = 10000 / (5.0 / voltage - 1.0)
#     # thermistor equation using 3435 beta value to find the temp
#     temp_kelvin = 1.0 / (math.log(resistance / 10000) / 3435 + 1.0 / 298)
#     temp_celsius = temp_kelvin - 273.15
#     print(temp_celsius)
