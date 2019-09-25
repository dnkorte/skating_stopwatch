"""
* PyPortal referee stopwatch for figure skating competitions
* Author(s): Don Korte
* Module:  battery_checker.py holds code to read battery status
"""

import board
from digitalio import DigitalInOut, Direction, Pull
from analogio import AnalogIn

# 20190912 modified to use A3 (on connector D4) instead of A1 (on conn D3) 
# because the power pin on connector D3 is compromised on 1st prototype unit
# TRULY, you need to use board.D4 for the analog signal on the D4 connector.  runtime error claims there is no A3
analog_in_pin = AnalogIn(board.D4)

def get_voltage():
    avg = 0
    num_readings = 5
    for _ in range(num_readings):
        avg += analog_in_pin.value        
    avg /= num_readings
    # scaled_analog_volts = (avg * 2) * (3.3 / 65536)       # because resistively divided by 2 in hardware
    # analog_volts = avg * (analog_in_pin.reference_voltage / 65536)   
    analog_volts = avg * (5 / 65536)       
    # analog_volts = analog_in_pin.reference_voltage  
    return analog_volts


def get_battery_pct():
    raw_volts = get_voltage()
    # we want 4.1v battery to indicate 100 % --> this yields 1.45 raw_volts read
    # and we want 3.2v battery to indicate 0 % --> this yielsds 1.00 raw_volts read
    batt_percent = 100 * (raw_volts - 1.00) / (1.45 - 1.00)
    return batt_percent