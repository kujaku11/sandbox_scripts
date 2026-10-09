import winsound
import time

def beep(frequency, duration):
    winsound.Beep(frequency, duration)  # 1000 Hz, 0.5 seconds

while True:
    beep(1000, 100)
    time.sleep(30)  # wait 10 seconds before next beep
