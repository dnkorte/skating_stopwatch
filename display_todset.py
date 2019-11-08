"""
# PyPortal referee stopwatch for figure skating competitions
# Author(s): Don Korte; inspired by calculator module by Melissa LeBlanc-Williams
# Module:  display_todset.py class manages low level details of screen used to set Time of Day
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
from adafruit_bitmap_font import bitmap_font
import myconstants

Coords = namedtuple("Point", "x y")

# Settings
BUTTON_WIDTH = 72
BUTTON_HEIGHT = 52
BUTTON_MARGIN = 8

class Display_Todset:
    def __init__(self, this_group, font, fontbig):
        self._this_group = this_group
        self._font = font
        self._fontbig = fontbig

        self._desired_hours = 12
        self._desired_minutes = 15
        self._desired_ampm = "am"

        self.headertext = Label(self._font, text="Set the Clock", color=myconstants.WHITE, max_glyphs=14)
        _, _, textwidth, _ = self.headertext.bounding_box
        self.headertext.x = 312 - textwidth
        self.headertext.y = 12
        self._this_group.append(self.headertext)

        self._hours_display_box = Label(self._fontbig, text="", color=myconstants.YELLOW, max_glyphs=2)
        self._hours_display_text_rightedge = 101
        self._hours_display_box.y = 70      
        self._this_group.append(self._hours_display_box)

        self._colon_display_box = Label(self._fontbig, text=":", color=myconstants.YELLOW, max_glyphs=1)
        self._colon_display_box.x = 111   
        self._colon_display_box.y = 70    
        self._this_group.append(self._colon_display_box)

        self._minutes_display_box = Label(self._fontbig, text="", color=myconstants.YELLOW, max_glyphs=2)
        self._minutes_display_box.x = 136  
        self._minutes_display_box.y = 70      
        self._this_group.append(self._minutes_display_box)

        self._ampm_box = Label(self._font, text="", color=myconstants.BLUE, max_glyphs=2)
        self._ampm_box.x = 244
        self._ampm_box.y = 46
        self._this_group.append(self._ampm_box)

        self._buttons = []
        self._add_button(3, 1, "Set", 1, 1, myconstants.SMOKY_GREEN, myconstants.WHITE)
        self._add_button(3, 2, "Cancel", 1, 1, myconstants.RED, myconstants.WHITE)
        self._add_button(3, 3, "AM/PM", 1, 1, myconstants.BLUE, myconstants.WHITE)
        self._add_button_by_pixels(28, 124, "+ H", 1, 1, myconstants.BROWN, myconstants.WHITE)
        self._add_button_by_pixels(28, 184, "- H", 1, 1, myconstants.PURPLE, myconstants.WHITE)
        self._add_button_by_pixels(142, 124, "+ M", 1, 1, myconstants.BROWN, myconstants.WHITE)
        self._add_button_by_pixels(142, 184, "- M", 1, 1, myconstants.PURPLE, myconstants.WHITE)
        
        for b in self._buttons:
            self._this_group.append(b.group)

        self._show_text_hours()
        self._show_text_minutes()
        self._show_ampm()


    def show_this_screen(self):
        board.DISPLAY.show(self._this_group)


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

    def _add_button_by_pixels(self, x, y, label, width=1, height=1, color=myconstants.WHITE, text_color=myconstants.BLACK):
        new_button = Button(x=x, y=y,
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


    def _show_ampm(self):
        ampm = self._desired_ampm
        self._ampm_box.text = ampm.upper()
        if ampm == "am": 
            self._ampm_box.color = myconstants.BLUE
        else:   
            self._ampm_box.color = myconstants.RED

    def _show_text_hours(self):
        hours_as_int = self._desired_hours
        self._hours_display_box.text = str(hours_as_int)
        _, _, textwidth, _ = self._hours_display_box.bounding_box
        self._hours_display_box.x = self._hours_display_text_rightedge - textwidth

    def _show_text_minutes(self):
        minutes_as_int = self._desired_minutes
        leading_zero = ""
        if minutes_as_int < 10:
            leading_zero = "0"
        text = leading_zero + str(minutes_as_int)
        self._minutes_display_box.text = text

    def set_desired_all(self, hours, minutes, ampm):
        self._desired_hours = hours
        self._desired_minutes = minutes
        self._desired_ampm = ampm 
        self._show_text_hours()
        self._show_text_minutes()
        self._show_ampm()

    def get_desired_hours(self):
        return self._desired_hours

    def get_desired_minutes(self):
        return self._desired_minutes

    def get_desired_ampm(self):
        return self._desired_ampm

    def increment_desired_hours(self):
        self._desired_hours = self._desired_hours + 1
        if self._desired_hours > 12:
            self._desired_hours = 1
        self._show_text_hours()

    def decrement_desired_hours(self):
        self._desired_hours = self._desired_hours - 1
        if self._desired_hours < 1:
            self._desired_hours = 12
        self._show_text_hours()


    def increment_desired_minutes(self):
        self._desired_minutes = self._desired_minutes + 1
        if self._desired_minutes > 59:
            self._desired_minutes = 0
        self._show_text_minutes()

    def decrement_desired_minutes(self):
        self._desired_minutes = self._desired_minutes - 1
        if self._desired_minutes < 0:
            self._desired_minutes = 59
        self._show_text_minutes()


    def toggle_desired_ampm(self):
        if self._desired_ampm == "am":
            self._desired_ampm = "pm"
        else:
            self._desired_ampm = "am"
        self._show_ampm()

