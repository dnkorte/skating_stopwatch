"""
* PyPortal referee stopwatch for figure skating competitions
* Author(s): Don Korte
* Module:   beeper.py manages piezo beeper attached to JST connector D3 (transistor driver)
* 
* series 5 this incorporates barry enhancements (interruption timer) 
* 20190912 modified to use D3 for beeper instead of D4
* 20190816 has piezo beeper instead of audio .wav (controlled from mainline)
"""
import time
import board
from digitalio import DigitalInOut, Direction, Pull
import myconstants

class Beep_Manager:
    def __init__(self):
        # initialize beeper output bit on D3 connector
        self._beep_device = DigitalInOut(board.D3)
        self._beep_device.direction = Direction.OUTPUT
        # this schedules beeper in cycle intervals (0=off, 1= 0.1s, 2= 0.2s, etc)
        self._beepcounter = 0    
        self._noisymode = True


    # note for beeps, num_of_loops is number of program main loops to sound beeper.  one loop = 0.1s
    def set_beep_counter(self, num_of_loops):
        self._beepcounter = num_of_loops

    def get_beep_counter(self):
        return self._beepcounter

    def decrement_beep_counter(self):
        self._beepcounter = self._beepcounter - 1
        if self._beepcounter < 0:
            self._beepcounter = 0

    def set_quiet_mode(self):
        self._noisymode = False

    def set_noisy_mode(self):
        self._noisymode = True

    def is_noisy_mode(self):
        return self._noisymode

    def quick_chirp(self):
        if self._noisymode:
            self._beep_device.value = True
            time.sleep(0.01)
            self._beep_device.value = False

    def process_beep(self):
        if self.get_beep_counter() > 0:
            self._beep_device.value = True
            self.decrement_beep_counter()
        else:
            self._beep_device.value = False

