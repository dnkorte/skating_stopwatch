"""
# PyPortal referee stopwatch for figure skating competitions
# Author(s): Don Korte
# Module:   beeper.py manages piezo beeper attached to JST connector D3 (transistor driver)
#
# github: https://github.com/dnkorte/skating_stopwatch.git
# 
# MIT License
# 
# Copyright (c) 2019 Don Korte
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# 
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
            # we want a beep, but make it chirpy...
            if (self.get_beep_counter() % 3) > 0:
                self._beep_device.value = True
            else:
                self._beep_device.value = False
            self.decrement_beep_counter()
        else:
            self._beep_device.value = False

