"""
# PyPortal referee stopwatch for figure skating competitions
# Author(s): Don Korte
# Module:  real_time_clock.py manages interaction with Real Time Clock board (i2c)
#  
# this for Adafruit PCF8523 Real Time Clock board  https://www.adafruit.com/product/3295
# learn guide: https://learn.adafruit.com/adafruit-pcf8523-real-time-clock/overview
# python library details: https://circuitpython.readthedocs.io/projects/pcf8523/en/latest/
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
import busio
import adafruit_pcf8523

class RealTimeClock:
    def __init__(self):
        # initialize beeper output bit on D3 connector
        self._myI2C = busio.I2C(board.SCL, board.SDA)
        self._rtc = adafruit_pcf8523.PCF8523(self._myI2C)
        self._current_hour = 0
        self._current_min = 0
        self._ampm = "am"
        self._current_time_from_clock = self._rtc.datetime

    def _first_ever_set_clock(self):
        t = time.struct_time((2019, 8, 23, 12, 55, 0, 6, -1, -1))
        self._rtc.datetime = t

    def set_clock(self, desired_hour, desired_min, desired_ampm):
    	useHour = desired_hour
    	if desired_hour == 12 and desired_ampm == "am":
    		useHour = 0
    	elif desired_hour == 12 and desired_ampm == "pm":
    		useHour = 12
    	elif desired_hour < 12 and desired_ampm == "pm":
    		useHour = desired_hour + 12
        t = time.struct_time((2019, 8, 23, useHour, desired_min, 0, 6, -1, -1))
        self._rtc.datetime = t

    def read_clock(self):
    	self._current_time_from_clock = self._rtc.datetime
    	self._current_hour = self._current_time_from_clock.tm_hour
    	self._current_min = self._current_time_from_clock.tm_min
        self._current_ampm = "am"
        if self._current_hour == 0:
        	self._current_hour = 12
        elif self._current_hour > 12:
        	self._current_hour = self._current_hour - 12
        	self._ampm = "pm"
        elif self._current_hour == 12:
        	self._ampm = "pm"


    def get_hour(self):
    	return self._current_hour

    def get_min(self):
    	return self._current_min

    def get_ampm(self):
    	return self._ampm

    def get_formatted_tod(self):
    	self.read_clock()
        minutes_as_int = self._current_min
        leading_zero = ""
        if minutes_as_int < 10:
            leading_zero = "0"
        text = leading_zero + str(minutes_as_int)
        return str(self._current_hour) + ":" + text + " " + self._ampm
