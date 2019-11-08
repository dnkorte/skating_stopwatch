"""
# PyPortal referee stopwatch for figure skating competitions
# Author(s): Don Korte; inspired by calculator module by Melissa LeBlanc-Williams
# Module:  display_main.py class manages low level details of main stopwatch screen
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
from adafruit_display_shapes.rect import Rect
from adafruit_display_text.label import Label
from collections import namedtuple
from adafruit_button import Button
import myconstants

Coords = namedtuple("Point", "x y")

# Settings
BUTTON_WIDTH = 72
BUTTON_HEIGHT = 52
BUTTON_MARGIN = 8

class Display_Main:
    def __init__(self, this_group, font, fontbig):
        self._this_group = this_group
        self._font = font
        self._fontbig = fontbig

        self._watch_notes_background = Rect(4, 116, 232, 60, fill=myconstants.DARKGRAY, outline=myconstants.BLACK, stroke=2)
        self._watch_notes1_box = Label(self._font, text="", color=myconstants.WHITE, max_glyphs=38)
        self._watch_notes1_box.y = 128
        self._watch_notes2_box = Label(self._font, text="", color=myconstants.WHITE, max_glyphs=38)
        self._watch_notes2_box.y = 146
        self._watch_notes3_box = Label(self._font, text="", color=myconstants.WHITE, max_glyphs=38)
        self._watch_notes3_box.y = 164
        self._watch_notes_center = 120
        self._this_group.append(self._watch_notes_background)
        self._this_group.append(self._watch_notes1_box)
        self._this_group.append(self._watch_notes2_box)
        self._this_group.append(self._watch_notes3_box)

        self._watch_display_box = Label(self._fontbig, text="", color=myconstants.BLUE, max_glyphs=8)
        self._watch_display_text_rightedge = 230
        self._watch_display_box.y = 58    # was 66
        self._this_group.append(self._watch_display_box)

        self._mode_display_box = Label(self._font, text="", color=myconstants.WHITE, max_glyphs=20)
        self._mode_display_text_rightedge = 230
        self._mode_display_box.y = 8
        self._this_group.append(self._mode_display_box)

        self._dur1_textbox = Label(self._font, text="", color=myconstants.YELLOW, max_glyphs=4)
        self._dur1_textbox.y = 38
        self._dur1_textbox.x = 8
        self._this_group.append(self._dur1_textbox)

        self._dur2_textbox = Label(self._font, text="", color=myconstants.YELLOW, max_glyphs=4)
        self._dur2_textbox.y = 58
        self._dur2_textbox.x = 8
        self._this_group.append(self._dur2_textbox)

        self._dur3_textbox = Label(self._font, text="", color=myconstants.YELLOW, max_glyphs=6)
        self._dur3_textbox.y = 78
        self._dur3_textbox.x = 8
        self._this_group.append(self._dur3_textbox)

        self._half2_textbox = Label(self._font, text="", color=myconstants.GREEN, max_glyphs=8)
        self._half2_textbox.y = 98
        self._half2_textbox.x = 8
        self._this_group.append(self._half2_textbox)

        self._timewarn_textbox = Label(self._font, text="", color=myconstants.WHITE, max_glyphs=24)
        self._timewarn_text_rightedge = 230
        self._timewarn_textbox.y = 98
        self._this_group.append(self._timewarn_textbox)

        self._tod_textbox = Label(self._font, text="", color=myconstants.GREEN, max_glyphs=8)
        self._tod_textbox.y = 8
        self._tod_textbox.x = 8
        self._this_group.append(self._tod_textbox)

        # self._battbox1 = Rect(6, 109, 228, 4, fill=myconstants.GREEN, outline=myconstants.BLACK)
        self._battbox0 = Rect(6, 109, 22, 4, fill=myconstants.RED, outline=myconstants.BLACK)
        self._battbox1 = Rect(28, 109, 22, 4, fill=myconstants.RED, outline=myconstants.BLACK)
        self._battbox2 = Rect(50, 109, 22, 4, fill=myconstants.ORANGE, outline=myconstants.BLACK)
        self._battbox3 = Rect(72, 109, 22, 4, fill=myconstants.ORANGE, outline=myconstants.BLACK)
        self._battbox4 = Rect(94, 109, 22, 4, fill=myconstants.YELLOW, outline=myconstants.BLACK)
        self._battbox5 = Rect(116, 109, 22, 4, fill=myconstants.YELLOW, outline=myconstants.BLACK)
        self._battbox6 = Rect(138, 109, 22, 4, fill=myconstants.GREEN, outline=myconstants.BLACK)
        self._battbox7 = Rect(160, 109, 22, 4, fill=myconstants.GREEN, outline=myconstants.BLACK)
        self._battbox8 = Rect(182, 109, 22, 4, fill=myconstants.GREEN, outline=myconstants.BLACK)
        self._battbox9 = Rect(204, 109, 22, 4, fill=myconstants.GREEN, outline=myconstants.BLACK)
        self._this_group.append(self._battbox0)  
        self._this_group.append(self._battbox1)  
        self._this_group.append(self._battbox2)  
        self._this_group.append(self._battbox3)  
        self._this_group.append(self._battbox4)  
        self._this_group.append(self._battbox5)  
        self._this_group.append(self._battbox6)  
        self._this_group.append(self._battbox7)  
        self._this_group.append(self._battbox8)  
        self._this_group.append(self._battbox9)  
        
        self._buttons = []
        self._add_button(3, 0, "Whistle", 1, 1, myconstants.RED, myconstants.WHITE)
        self._btnSS = self._add_button(3, 1, "Start", 1, 2, myconstants.DARKORANGE, myconstants.BLACK)
        self._btnA = self._add_button(0, 3, "Warmup", 1, 1, myconstants.LIGHTBLUE, myconstants.WHITE)
        self._btnB = self._add_button(1, 3, "Chg.Dur", 1, 1, myconstants.DEEP_PURPLE, myconstants.WHITE)
        self._btnC = self._add_button(2, 3, "..", 1, 1, myconstants.PURPLE, myconstants.WHITE)
        self._btnD = self._add_button(3, 3, "Call.Sk", 1, 1, myconstants.SMOKY_GREEN, myconstants.WHITE)
        
        for b in self._buttons:
            self._this_group.append(b.group)


    def show_this_screen(self):
        board.DISPLAY.show(self._this_group)

    def set_text_wnb1(self, text):
        self._watch_notes1_box.text = text
        _, _, textwidth, _ = self._watch_notes1_box.bounding_box
        self._watch_notes1_box.x = self._watch_notes_center - int(textwidth/2)

    def set_text_wnb2(self, text):
        self._watch_notes2_box.text = text
        _, _, textwidth, _ = self._watch_notes2_box.bounding_box
        self._watch_notes2_box.x = self._watch_notes_center - int(textwidth/2)

    def set_text_wnb3(self, text):
        self._watch_notes3_box.text = text
        _, _, textwidth, _ = self._watch_notes3_box.bounding_box
        self._watch_notes3_box.x = self._watch_notes_center - int(textwidth/2)

    def set_text_tdb(self, text):
        self._watch_display_box.text = text
        _, _, textwidth, _ = self._watch_display_box.bounding_box
        self._watch_display_box.x = self._watch_display_text_rightedge - textwidth

    def set_text_mdb(self, text):
        self._mode_display_box.text = text
        _, _, textwidth, _ = self._mode_display_box.bounding_box
        self._mode_display_box.x = self._mode_display_text_rightedge - textwidth

    def set_text_timewarn(self, text):
        self._timewarn_textbox.text = text
        _, _, textwidth, _ = self._timewarn_textbox.bounding_box
        self._timewarn_textbox.x = self._timewarn_text_rightedge - textwidth

    def set_text_tod(self, text):
        self._tod_textbox.text = text

    def set_text_dur1(self, text):
        self._dur1_textbox.text = text
    def set_text_dur2(self, text):
        self._dur2_textbox.text = text
    def set_text_dur3(self, text):
        self._dur3_textbox.text = text

    def _set_half2_textbox(self, text):
        self._half2_textbox.text = text


    def _button_grid(self, row, col):
        return Coords(BUTTON_MARGIN * (row + 1) + BUTTON_WIDTH * row - (4),
                      BUTTON_MARGIN * (col + 1) + BUTTON_HEIGHT * col - (4))

    def _add_button(self, row, col, label, width=1, height=1, color=myconstants.WHITE, text_color=myconstants.BLACK):
        pos = self._button_grid(row, col)
        new_button = Button(x=pos.x, y=pos.y,
                            width=BUTTON_WIDTH * width + BUTTON_MARGIN * (width - 1),
                            height=BUTTON_HEIGHT * height + BUTTON_MARGIN * (height - 1),
                            label=label, label_font=self._font,
                            label_color=text_color, fill_color=color, style=Button.ROUNDRECT)
        self._buttons.append(new_button)
        return new_button

    def get_button_label(self, button_id):
        return button_id.label


    # called with the point coordinates of a screen touch event; if this is a button, return its id, else return None
    # if a button is clicked, it sets it so "selected" state so its color is inverse
    def see_if_any_button_clicked(self, point):  
        btn_clicked = None  
        for _, b in enumerate(self._buttons):
            # cycling through all buttons, this one contains the point touched
            if b.contains(point):
                b.selected = True
                btn_clicked = b
        return btn_clicked

    def set_btnA(self, label):
        self._btnA.label = label

    def set_btnB(self, label):
        self._btnB.label = label

    def set_btnC(self, label):
        self._btnC.label = label

    def set_btnD(self, label):
        self._btnD.label = label

    def set_btnSS(self, label):
        self._btnSS.label = label

    def unselect_this_button(self, input_key):
        if self._find_button(input_key) != None:
            self._find_button(input_key).selected = False
            # self._btnC_button.selected = False   

    def show_battery_status(self, charge_percent):
        # note charge percentage should be integer 0-100
        if charge_percent > 5:
            self._battbox0.fill = myconstants.RED
        else:
            self._battbox0.fill = myconstants.PURPLE

        if charge_percent > 10:
            self._battbox1.fill = myconstants.RED
        else:
            self._battbox1.fill = myconstants.BLACK

        if charge_percent > 20:
            self._battbox2.fill = myconstants.ORANGE
        else:
            self._battbox2.fill = myconstants.BLACK

        if charge_percent > 30:
            self._battbox3.fill = myconstants.ORANGE
        else:
            self._battbox3.fill = myconstants.BLACK

        if charge_percent > 40:
            self._battbox4.fill = myconstants.YELLOW
        else:
            self._battbox4.fill = myconstants.BLACK

        if charge_percent > 50:
            self._battbox5.fill = myconstants.YELLOW
        else:
            self._battbox5.fill = myconstants.BLACK

        if charge_percent > 60:
            self._battbox6.fill = myconstants.GREEN
        else:
            self._battbox6.fill = myconstants.BLACK

        if charge_percent > 70:
            self._battbox7.fill = myconstants.GREEN
        else:
            self._battbox7.fill = myconstants.BLACK

        if charge_percent > 80:
            self._battbox8.fill = myconstants.GREEN
        else:
            self._battbox8.fill = myconstants.BLACK

        if charge_percent > 90:
            self._battbox9.fill = myconstants.GREEN
        else:
            self._battbox9.fill = myconstants.BLACK

        # note if running on USB cable then percentage will be > 100
        if charge_percent > 100:
            self._battbox9.fill = myconstants.BLUE
            self._battbox8.fill = myconstants.BLUE
            self._battbox7.fill = myconstants.BLUE
            self._battbox6.fill = myconstants.BLUE
            self._battbox5.fill = myconstants.BLUE
            self._battbox4.fill = myconstants.BLUE
            self._battbox3.fill = myconstants.BLUE
            self._battbox2.fill = myconstants.BLUE
            self._battbox1.fill = myconstants.BLUE
            self._battbox0.fill = myconstants.BLUE