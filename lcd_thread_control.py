import threading
import time


class LcdThread (threading.Thread):
    """
    Thread running the 4x20 LCD. Designed to respond to operation mode changes
    via API.
    """
    # Mode 0 - exits thread
    # Mode 1 - Display room temperatures and pressure
    # Mode 2 - Display Pi Zero's CPU temperature and temperature trend and date

    def __init__(self, mode=1):
        self._mode_cache = 0
        self.mode = mode
        self.lock = threading.RLock()
        super(LcdThread, self).__init__()

    def set_mode(self, mode):  # you can use a proper setter if you want
        with self.lock:
            self.mode = mode

    def run(self):
        while True:
            with self.lock:
                if self.mode == 0:
                    print("Mode 0, exiting...")
                    #lcd.clear()
                    break
                # just so we don't continually print the mode, print only on change
                if self.mode != self._mode_cache:
                    print("Current mode: {}".format(self.mode))
                    self._mode_cache = self.mode
            time.sleep(0.1)  # let it breathe


current_mode = 1  # initial mode

blink_thread = LcdThread(current_mode)
blink_thread.start()

while current_mode != 0:  # main loop until 0 mode is selected
    time.sleep(0.1)  # wait a little for an update
    current_mode = int(input("Enter 0 to Exit or 1/2/3 to continue\n"))  # add validation?
    blink_thread.set_mode(current_mode)
