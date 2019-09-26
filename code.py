"""
* PyPortal referee stopwatch for figure skating competitions
* Author(s): Don Korte
* Module:  code.py is mainline initialization and master loop
* 
* series 7 moves buttons into display_xxx modules
* series 6 adds second screen (for tod set) using separate classes for each screen
*          moved initialization for screen textboxes into display classes
* series 5 this incorporates barry enhancements (interruption timer) 
* 20190816 has piezo beeper instead of audio .wav (controlled from mainline)
"""
import time
from collections import namedtuple
import board
from digitalio import DigitalInOut, Direction, Pull
import displayio
from adafruit_display_text.label import Label
from adafruit_bitmap_font import bitmap_font
import terminalio   # added by dnk per https://learn.adafruit.com/circuitpython-display-support-using-displayio?view=all
from adafruit_display_shapes.rect import Rect
from adafruit_button import Button
import adafruit_touchscreen
from analogio import AnalogIn

from display_main import Display_Main
from display_todset import Display_Todset
from skating_info import Skating_Info
from controller import Controller
from beeper import Beep_Manager
from real_time_clock import RealTimeClock
import myconstants
import battery_checker

# initial splash screen just so it doesn't look dead for so long while it loads fonts 
# cwd = ("/"+__file__).rsplit('/', 1)[0]      # the current working directory (where this file is)
# startup_background = cwd+"/pyportal_splash.bmp"
splash = displayio.Group()
board.DISPLAY.show(splash)
f = open("boot_splash_stopwatch.bmp", "rb")
background = displayio.OnDiskBitmap(f)
face = displayio.TileGrid(background, pixel_shader=displayio.ColorConverter(), x=0, y=0)
splash.append(face)
board.DISPLAY.wait_for_frame()

Coords = namedtuple("Point", "x y")

ts = adafruit_touchscreen.Touchscreen(board.TOUCH_XL, board.TOUCH_XR,
                                      board.TOUCH_YD, board.TOUCH_YU,
                                      calibration=((5200, 59000), (5800, 57000)),
                                      size=(320, 240))

# Load the font
font = bitmap_font.load_font("/fonts/Arial-12.bdf")
fontBig = bitmap_font.load_font("/fonts/Roboto-Bold-75.bdf")
# fontBig = bitmap_font.load_font("/fonts/RobotoMono-Bold-78.bdf")
# now preload the fonts so they display more quickly the first time
glyphs = b'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-,.: '
font.load_glyphs(glyphs)
fontBig.load_glyphs(glyphs)

# ======================== Make the main display context (watch) ========================
# Make a background color fill
color_bitmap = displayio.Bitmap(320, 240, 1)
color_palette = displayio.Palette(1)
color_palette[0] = myconstants.BLACK
bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
watch_group = displayio.Group(max_size=35)
watch_group.append(bg_sprite)

# ============ create secondary screen for TOD Clock Setting (not initially shown) ==============
todset_group = displayio.Group(max_size=35)
bg_sprite_tod = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
todset_group.append(bg_sprite_tod)

# =========================== setup the classes for item management ========================
display_main = Display_Main(watch_group, font, fontBig)
display_todset = Display_Todset(todset_group, font, fontBig)
beep_manager = Beep_Manager()
rtc_manager = RealTimeClock()
skating_info = Skating_Info(display_main, beep_manager, rtc_manager)
controller = Controller(display_main, display_todset, skating_info, beep_manager, rtc_manager)

controller.set_current_screen("watch")
display_main.set_text_tod(rtc_manager.get_formatted_tod())

cur_button_label = ""         # will hold "label" (the display text) of most recently clicked button 
cur_button_id = None          # will hold id of most recently clicked button
screensaver_timer = 0         # counts how long before screen dims if no touches
batt_counter = 0              # counts holw long between battery updates
tod_timer = 0                 # update time of day display only every 60 sec
watch_timer = 0               # update big (main) timer DISPLAY every 0.5 sec to reduce lagtime at startup
while True:
    point = ts.touch_point
    # if the screen is currently being touched (probably a button being pressed)
    if point is not None:
        screensaver_timer = 0      # register the touch for screensaver countdown

        if controller.get_current_screen() == "watch":
            cur_button_id = display_main.see_if_any_button_clicked(point)
            if cur_button_id != None:
                cur_button_label = display_main.get_button_label(cur_button_id)
        elif controller.get_current_screen() == "todset":
            cur_button_id = display_todset.see_if_any_button_clicked(point)
            if cur_button_id != None:
                cur_button_label = display_todset.get_button_label(cur_button_id)

    # here, no button is pressed, so we check to see if a button was recently pressed/released
    # but has not been processed yet.  if an unprocessed command is pending, then deselect
    # the button and then process the command, then indicate that it has been processed
    elif cur_button_id != None:
        cur_button_id.selected = False

        if controller.get_current_screen() == "watch":
            controller.process_command_watch(cur_button_label)
        elif controller.get_current_screen() == "todset":
            controller.process_command_todset(cur_button_label)

        cur_button_label = ""
        cur_button_id = None

    watch_timer += 1
    if watch_timer >= 2:
        if controller.get_current_screen() == "watch":
            skating_info.display_time()         # only in watch mode
            skating_info.display_notes_panel()  # onoy in watch mode
            watch_timer = 0

    tod_timer = tod_timer + 1
    if tod_timer >= 600:
        if controller.get_current_screen() == "watch":
            display_main.set_text_tod(rtc_manager.get_formatted_tod())
        tod_timer = 0

    screensaver_timer = screensaver_timer + 1
    if screensaver_timer > 6000:
        board.DISPLAY.brightness = 0.02
    elif screensaver_timer > 5900:
        board.DISPLAY.brightness = 0.1
    else:
        board.DISPLAY.brightness = 1
      
    batt_counter = batt_counter + 1
    # if batt_counter > 9:            # update battery voltage once per second for testing...
    if batt_counter > 600:            # update battery voltage every 1 minute for real
        batt_counter = 0
        raw_volts = battery_checker.get_voltage()
        batt_percent = battery_checker.get_battery_pct()
        # display_main.set_text_wnb3("Vbat:"+str(raw_volts)+" PCT:"+str(batt_percent))
        display_main.show_battery_status(batt_percent) 

    beep_manager.process_beep()
    time.sleep(0.1)