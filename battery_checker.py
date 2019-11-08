"""
# PyPortal referee stopwatch for figure skating competitions
# Author(s): Don Korte
# Module:  battery_checker.py holds code to read battery status
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

import board
from digitalio import DigitalInOut, Direction, Pull
from analogio import AnalogIn

# 20190912 modified to use A3 (on connector D4) instead of A1 (on conn D3) 
# because the power pin on connector D3 is compromised on 1st prototype unit

# TRULY, you need to reference board.D4 for the analog signal on the D4 connector.  runtime error claims there is no A3
analog_in_pin = AnalogIn(board.D4)

# note that in the stopwatch box, we divide the battery voltage by 2 in a resistive divider (because it will hopefully be > 3.3v), 
# then buffer it with a voltage-follower transistor.  so the voltage we actually read with the a/d is actually 0.6v less than
# 50 pct of the actual battery voltage.  the get_voltage() function reads and returns the actual voltage READ.  the adjustments
# for buffering and scaling are figured out in the get_battery_pct() function
# 
# ALSO note that there is a wierd hardware issue in the PyPortal.  the analog reference voltage used actually changes according
# to the power supply voltage given to the pyportal.   In this stopwatch, we backfeed 5v (from the PowerBoost 1000) into 
# the Vcc pin on D4 (as recommended in the Portable PyPortal guide https://learn.adafruit.com/portable-pyportal, instead of
# powering it from the MicroUSB connector (in actual use -- during development it is powered from MicroUSB).   If you read the
# scaled battery voltage using the a/d you get different values depending on the power supply configuration.
# 
# EXAMPLE: hooked up as described above.  the actual voltage measured at a/d pin by Fluke Multimeter is 1.36v

# 								software scaling multiplier for a/d:
# Test 1:  with USB power ON, but PowerBoost OFF	5.0			3.3
# 			get_voltage returns:					2.07v		1.36v
# Test 2:	with USB power ON, and PowerBoost ON
# 													1.33v		0.87v
# Test 3:	with USB power OFF, and PowerBoost ON
# 													1.33v		0.87v
# So, turning the PowerBoost ON (supplying 5v to the Vcc which normally sits at 3.3v) causes the apparent internal Vref to change.
# 
# Since we will normally operate this device on battery (PowerBoost) without connection to desktop on MicroUSB
# the software is set to use a 5v scaling multiplier when reading a/d.   If it returns > 1.5 volts we just assume we are on MicroUSB
# 												

def get_voltage():
    avg = 0
    num_readings = 5
    for _ in range(num_readings):
        avg += analog_in_pin.value        
    avg /= num_readings
    analog_volts = avg * (5 / 65536)       
    # analog_volts = analog_in_pin.reference_voltage  
    return analog_volts

def get_voltageXX():
	# @wallarug suggested fix for saturation issues
	return 1.0 * analog_in_pin.value / 65535 * 3.25


def get_battery_pct():
    raw_volts = get_voltage()
    # we want 4.1v battery to indicate 100 % --> this yields 1.45 raw_volts read (2.05 - 0.6)
    # and we want 3.2v battery to indicate 0 % --> this yields 1.00 raw_volts read (1.6 - 0.6)
    batt_percent = 100 * (raw_volts - 1.00) / (1.45 - 1.00)
    return batt_percent