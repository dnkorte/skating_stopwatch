"""
* PyPortal referee stopwatch for figure skating competitions
* Author(s): Don Korte
* Module:  skating_info.py manages all knowledge about figure skating parameters and status
* 
* series 5 this incorporates barry enhancements (interruption timer) 
* 20190816 has piezo beeper instead of audio .wav (controlled from mainline)
"""
import time
import board
from digitalio import DigitalInOut, Direction, Pull
import myconstants

class Skating_Info:
    def __init__(self, display_main, beep_manager, rtc_manager):
        self._display_main = display_main
        self._beep_manager = beep_manager
        self._rtc_manager = rtc_manager
        self._warmupduration_sec = 240
        self._mode = "program"                  # "program" or "warmup"
        self._alert_silent_or_beep = "B"        # "B" or "S"
        self._current_screen = "watch"          # "watch" or "setprog" or "settime"

        self._current_main_num_of_seconds = 0
        self._main_timer_running = "no"              # "no" or "yes"
        self._main_timer_direction = "up"            # "up" or "down"
        # note this timer needs to be CORRECT, and not lose time when processor gets busy
        # so for this one (only) we calculate duration based on interrupt-driven system clock
        self._main_timer_start_reference = 0         # will get value from time.monotonic() when timer starts
        self._skater_call_timer_start_reference = 0         # will get value from time.monotonic() when timer starts
        self._skater_separation_timer_start_reference = 0   # will get value from time.monotonic() when timer starts
        self._interrupt_timer_start_reference = 0           # will get value from time.monotonic() when timer starts

        self._seconds_since_skater_call = 0
        self._skater_call_timer_running = "no"  # "no" or "yes"

        self._seconds_since_last_skater_ended = 0
        self._skater_separation_timer_running = "no"

        
        self._cur_duration_index = 0
        self._programdurations = [90, 120, 140, 150, 160, 180, 210, 240, 60, 70, 75, 90, 100, 110, 130, 150, 160, 190, 220]
        self._maxorwindow_values = ["W", "W", "W", "W", "W", "W", "W", "W", "M", "M", "M", "M", "M", "M", "M", "M", "M", "M", "M"]
        self._programduration_sec = self._programdurations[self._cur_duration_index]
        self._max_or_window = self._maxorwindow_values[self._cur_duration_index]

        self._interrupt_timer_running = "no"
        self._interrupt_started_at_seconds = 0     # 0 means not interrupted, positive value is number of seconds into prog that int started
        self._seconds_since_interrupt_started = 0  
        self._number_of_interruption_events = 0

        self.set_mode_program()

        self.reset_main_time()
        self.display_dur_info()
        self._display_main.set_text_wnb1("Since Skater Called: --")
        self._display_main.set_text_wnb2("Since Last Skater End: --")
        self._display_main.set_text_wnb3("No Interruptions")

    def _format_timestring(self, full_seconds):
        full_seconds_abs = abs(full_seconds)
        num_minutes = int(full_seconds_abs / 60)
        num_seconds = full_seconds_abs - (num_minutes * 60)
        sign = ""
        if full_seconds < 0:
            sign = "-"
        leading_zero = ""
        if num_seconds < 10:
            leading_zero = "0"
        return sign + str(num_minutes) + ":" + leading_zero + str(num_seconds)

    def set_mode_program(self):
        self._mode = "program"
        self._display_main.set_text_mdb("Competing")

    # iff in program mode, set its phase;  do nothing if in warmup mode
    def show_program_phase(self, phase):
        if self._mode == "program":
            self._display_main.set_text_mdb("Compete-"+phase)

    def set_mode_warmup(self):
        self._mode = "warmup"
        self._display_main.set_text_mdb("Warming Up")

    def is_mode_warmup(self):
        if self._mode == "warmup":
            return True
        else:
            return False

    def is_mode_program(self):
        if self._mode == "program":
            return True
        else:
            return False
    
    def reset_separation_timer(self):
        self._skater_separation_timer_running = "no"
        self._seconds_since_last_skater_ended = 0

    def start_separation_timer(self):
        self._skater_separation_timer_running = "yes"
        self._seconds_since_last_skater_ended = 0
        self._skater_separation_timer_start_reference = time.monotonic()

    def stop_separation_timer(self):
        self._skater_separation_timer_running = "no"

    def reset_call_timer(self):
        self._skater_call_timer_running = "no"
        self._seconds_since_skater_call = 0

    def start_call_timer(self):
        self._skater_call_timer_running = "yes"
        self._seconds_since_skater_call = 0
        self._skater_call_timer_start_reference = time.monotonic()

    def stop_call_timer(self):
        self._skater_call_timer_running = "no"


    def reset_interrupt_timer(self):
        self._interrupt_timer_running = "no"
        self._interrupt_started_at_seconds = 0     
        self._seconds_since_interrupt_started = 0 
        self._number_of_interruption_events = 0
        self._display_main._watch_notes3_box.color = myconstants.WHITE

    def start_interrupt_timer(self):
        self._interrupt_timer_running = "yes"
        self._interrupt_started_at_seconds = self._current_main_num_of_seconds     
        self._seconds_since_interrupt_started = 0 
        self._interrupt_timer_start_reference = time.monotonic()
        self.advance_number_of_interruptions()

    def stop_interrupt_timer(self):
        self._interrupt_timer_running = "no"

    def reset_number_of_interruptions(self): 
        self._number_of_interruption_events = 0

    def advance_number_of_interruptions(self): 
        self._number_of_interruption_events = self._number_of_interruption_events + 1

    def get_number_of_interruptions(self):
        return self._number_of_interruption_events


    def reset_main_time(self):
        if self._mode == "program":
            self._current_main_num_of_seconds = 0
            self._main_timer_direction = "up"
            self._main_timer_running = "no"
        else:
            self._current_main_num_of_seconds = self._warmupduration_sec
            self._main_timer_direction = "down"
            self._main_timer_running = "no"
        self._display_main._watch_display_box.color = myconstants.BLUE
        self._display_main.set_text_tdb(self._format_timestring(self._current_main_num_of_seconds))
        self._display_main._set_half2_textbox("")
        self._display_main.set_text_timewarn("")

    def start_main_timer(self):
        self._main_timer_running  = "yes"
        self._main_timer_start_reference = time.monotonic()

    def stop_main_timer(self):
        self._main_timer_running = "no"

    def update_times(self):
        timenow = time.monotonic()
        if self._main_timer_running == "yes":
            if self._main_timer_direction == "up":
                self._current_main_num_of_seconds = int(timenow - self._main_timer_start_reference)
            else:
                self._current_main_num_of_seconds = self._warmupduration_sec - int(timenow - self._main_timer_start_reference)

        if self._skater_call_timer_running == "yes":
            self._seconds_since_skater_call = int(timenow - self._skater_call_timer_start_reference)

        if self._skater_separation_timer_running == "yes":
            self._seconds_since_last_skater_ended = int(timenow - self._skater_separation_timer_start_reference)

        if self._interrupt_timer_running == "yes":
            self._seconds_since_interrupt_started = int(timenow - self._interrupt_timer_start_reference)

    def display_time(self):
        self.update_times()
        self._display_main.set_text_tdb(self._format_timestring(self._current_main_num_of_seconds))  
        if self._mode == "program" and self._main_timer_running == "yes":
            if self._max_or_window == "M":
                # for MAX programs - initially green; yellow at dur-5, red at dur
                if self._current_main_num_of_seconds > self._programduration_sec:
                    self._display_main._watch_display_box.color = myconstants.RED
                    self._display_main.set_text_timewarn("Too Long")
                elif self._current_main_num_of_seconds >= self._programduration_sec - 5:
                    self._display_main._watch_display_box.color = myconstants.YELLOW
                    self._display_main.set_text_timewarn("The end is near")
                else:
                    self._display_main._watch_display_box.color = myconstants.GREEN
                    self._display_main.set_text_timewarn("")
            else:
                # for +/- programs - initially red (short-not scored); orange at progdur-30 (short-deduct);
                # green at dur-10, yellow at dur+5, red at dur+10
                if self._current_main_num_of_seconds > self._programduration_sec + 10:
                    self._display_main._watch_display_box.color = myconstants.RED
                    self._display_main.set_text_timewarn("Too Long")
                elif self._current_main_num_of_seconds >= self._programduration_sec + 5:
                    self._display_main._watch_display_box.color = myconstants.YELLOW
                    self._display_main.set_text_timewarn("The end is near")
                elif self._current_main_num_of_seconds >= self._programduration_sec - 10:
                    self._display_main._watch_display_box.color = myconstants.GREEN
                    self._display_main.set_text_timewarn("")
                elif self._current_main_num_of_seconds >= self._programduration_sec - 30:
                    self._display_main._watch_display_box.color = myconstants.ORANGE
                    self._display_main.set_text_timewarn("Short-Deduct")
                elif self._current_main_num_of_seconds >= 1:
                    self._display_main._watch_display_box.color = myconstants.RED
                    self._display_main.set_text_timewarn("Too Short-No Score")
                else:
                    self._display_main.set_text_timewarn("")

            if self._current_main_num_of_seconds > (self._programduration_sec / 2):
                self._display_main._set_half2_textbox("2nd Half")

        if self._mode == "warmup" and self._main_timer_running == "yes":
            # for warmups - initially green; yellow at 60s, orange at 5, red at 0 and below
            if self._current_main_num_of_seconds > 60:
                self._display_main._watch_display_box.color = myconstants.GREEN
            elif self._current_main_num_of_seconds >=  5:
                self._display_main._watch_display_box.color = myconstants.YELLOW
            elif self._current_main_num_of_seconds >= 0:
                self._display_main._watch_display_box.color = myconstants.ORANGE
            else:
                self._display_main._watch_display_box.color = myconstants.RED

            if (self._current_main_num_of_seconds < 60) and (self._current_main_num_of_seconds > 0):
                self._display_main.set_text_timewarn("Final Minute")
            elif (self._current_main_num_of_seconds < 0):
                self._display_main.set_text_timewarn("Warmup Over")
            else:
                self._display_main.set_text_timewarn("")

        if self._main_timer_running == "no":
            self._display_main._watch_display_box.color = myconstants.BLUE
      

    # note if called when changing from warmup to program modes must write text even tho timers not running
    def display_notes_panel(self, modeChange=False):
        self.update_times()
        if self._mode == "program":
            if self._skater_call_timer_running == "yes" or modeChange:
                if (self._seconds_since_skater_call >= 0):
                    self._display_main.set_text_wnb1("Since Skater Called: " + self._format_timestring(self._seconds_since_skater_call))
                else:
                    self._display_main.set_text_wnb1("Since Skater Called: --")

                if self._seconds_since_skater_call >= 30:
                    self._display_main._watch_notes1_box.color = myconstants.RED
                else:
                    self._display_main._watch_notes1_box.color = myconstants.WHITE

            if self._skater_separation_timer_running == "yes" or modeChange:
                if self._seconds_since_last_skater_ended >= 0:
                    self._display_main.set_text_wnb2("Since Last Skater End: " + self._format_timestring(self._seconds_since_last_skater_ended))
                else:
                    self._display_main.set_text_wnb2("Since Last Skater End: --")

            beep_at_seconds = self._programduration_sec
            if self._max_or_window == "W": 
                beep_at_seconds = self._programduration_sec + 10
            if self._current_main_num_of_seconds == beep_at_seconds:
                self._beep_manager.set_beep_counter(2)

            if self.get_number_of_interruptions() == 0:
                self._display_main.set_text_wnb3("No Interruptions")
                pass
            else:
                message = "Interrupt @ " + self._format_timestring(self._interrupt_started_at_seconds)
                message = message + "   Dur: " + str(self._seconds_since_interrupt_started) + "s"
                self._display_main.set_text_wnb3(message)

                if self._seconds_since_interrupt_started > 40:
                    self._display_main._watch_notes3_box.color = myconstants.RED
                elif self._seconds_since_interrupt_started > 10:
                    self._display_main._watch_notes3_box.color = myconstants.ORANGE
                else:
                    self._display_main._watch_notes3_box.color = myconstants.WHITE

        if self._mode == "warmup":
            if self._beep_manager.is_noisy_mode():
                self._display_main.set_text_wnb1("(makes beeps on button-press)")
                self._display_main.set_text_wnb2("Click SILENT to eliminate")
            else:
                self._display_main.set_text_wnb1("(no beeps on button-press)")
                self._display_main.set_text_wnb2("Click NOISY to restore")
            self._display_main.set_text_wnb3("")

            if self._current_main_num_of_seconds == 0 or self._current_main_num_of_seconds == 60:
                self._beep_manager.set_beep_counter(2)

    def display_dur_info(self):
        if self._mode == "program":
            self._display_main.set_text_dur1("DUR")
            self._display_main.set_text_dur2(self._format_timestring(self._programduration_sec))
            if self._max_or_window == "M":
                self._display_main.set_text_dur3("MAX")
            else:
                self._display_main.set_text_dur3("+ / -")
        else:
            self._display_main.set_text_dur1("DUR")
            self._display_main.set_text_dur2(self._format_timestring(self._warmupduration_sec))
            self._display_main.set_text_dur3("")

    def cycle_to_next_available_duration(self):        
        if self.is_mode_warmup():
            oldDur = self._warmupduration_sec
            oldCount = self._current_main_num_of_seconds
            if oldDur == 180:
                self._warmupduration_sec = 360
                self._current_main_num_of_seconds = self._warmupduration_sec - (oldDur - oldCount)
            else:
                self._warmupduration_sec = oldDur - 60
                self._current_main_num_of_seconds = oldCount - 60
        else:
            oldIndex = self._cur_duration_index
            newIndex = oldIndex + 1
            if newIndex >= len(self._programdurations):
                newIndex = 0
            self._cur_duration_index = newIndex
            self._programduration_sec = self._programdurations[self._cur_duration_index]
            self._max_or_window = self._maxorwindow_values[self._cur_duration_index]