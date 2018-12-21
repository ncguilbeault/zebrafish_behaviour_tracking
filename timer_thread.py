'''Software Written by Nicholas Guilbeault 2018'''

# import python modules
import time
from PyQt5.QtCore import *

class TimerThread(QThread):

    time_signal = pyqtSignal(float)

    def __init__(self, sleep_time = 0.5):
        super(TimerThread, self).__init__()
        self.running = True
        self.sleep_time = sleep_time

    def run(self):
        while self.running:
            time_now = time.perf_counter()
            self.time_signal.emit(time_now)
            time.sleep(self.sleep_time)

    def close(self):
        self.running = False
