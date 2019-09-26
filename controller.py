"""
* PyPortal referee stopwatch for figure skating competitions
* Author(s): Don Korte
* Module:  controller.py has class that manages functionality based upon operation mode
* 
* series 7 moves buttons into display_xxx modules
* series 6 adds second screen (for tod set) using separate classes for each screen
*          moved initialization for screen textboxes into display classes
* series 5 this incorporates barry enhancements (interruption timer) 
* 20190816 has piezo beeper instead of audio .wav (controlled from mainline)
"""
import time
import board
from digitalio import DigitalInOut, Direction, Pull
import myconstants

class Controller:
    def __init__(self, display_main, display_todset, skating_info, beep_manager, rtc_manager):        
        self._display_main = display_main  
        self._display_todset = display_todset       
        self._skating_info = skating_info
        self._beep_manager = beep_manager
        self._rtc_manager = rtc_manager
        self._current_screen = "watch"              # "watch" (main), "todset", "talk" 

    def get_current_screen(self):
        return self._current_screen

    def set_current_screen(self, new_screen):
        if new_screen == "watch":
            self._current_screen = new_screen
            self._display_main.show_this_screen()
        elif new_screen == "todset":
            self._rtc_manager.read_clock()
            self._display_todset.set_desired_all(self._rtc_manager.get_hour(),self._rtc_manager.get_min(), self._rtc_manager.get_ampm())
            self._current_screen = new_screen
            self._display_todset.show_this_screen()
        else:
            pass

    def process_command_watch(self, input_key):
        if input_key == "Start" or input_key == "Start\nNew":
            self._display_main.set_btnSS("Stop")
            self._skating_info.show_program_phase("InProgram")
            self._skating_info.reset_main_time()
            self._skating_info.start_main_timer()
            self._skating_info.reset_interrupt_timer()
            self._skating_info.stop_call_timer()
            self._skating_info.stop_separation_timer()

            if self._skating_info.is_mode_program():  
                self._display_main.set_btnD("Interrupt")
            self._beep_manager.quick_chirp()

        elif input_key == "Stop":
            self._display_main._watch_display_box.color = myconstants.BLUE
            self._display_main.set_btnSS("Start\nNew")
            self._skating_info.show_program_phase("Between")
            self._skating_info.stop_main_timer()
            self._skating_info.stop_interrupt_timer()
            self._skating_info.start_separation_timer();
            if self._skating_info.is_mode_program():
                self._display_main.set_btnD("Call.Sk")
            self._beep_manager.quick_chirp()

        elif input_key == "Reset":
            self._display_main.set_btnSS("Start")
            self._skating_info.reset_main_time()
            self._beep_manager.quick_chirp()

        elif input_key == "Interrupt":
            self._display_main.set_btnD("Continue")  
            self._display_main.set_btnC("Talk")         
            self._skating_info.start_interrupt_timer()
            self._beep_manager.quick_chirp()

        elif input_key == "Continue":
            # self._btnD_button.selected = False  
            self._display_main.set_btnD("Interrupt") 
            self._display_main.set_btnC("..")          
            self._skating_info.stop_interrupt_timer()
            self._beep_manager.quick_chirp()

        elif input_key == "Whistle":
            self._beep_manager.set_beep_counter(30)

        elif input_key == "Warmup":
            self._display_main.set_btnA("Compete")
            self._display_main.set_btnSS("Start")
            if self._beep_manager.is_noisy_mode():
                self._display_main.set_btnC("Silent")
            else:
                self._display_main.set_btnC("Noisy")
            self._display_main.set_btnD("Clk.Set")
            self._skating_info.set_mode_warmup()
            self._skating_info.reset_main_time()
            self._skating_info.display_dur_info()
            self._skating_info.display_notes_panel()
            self._beep_manager.quick_chirp()

        elif input_key == "Compete":
            self._display_main.set_btnA("Warmup")
            self._display_main.set_btnSS("Start")
            self._display_main.set_btnC("..")
            self._display_main.set_btnD("Call.Sk")
            self._skating_info.set_mode_program()
            self._skating_info.reset_main_time()
            self._skating_info.reset_call_timer()
            self._skating_info.reset_separation_timer()
            self._skating_info.display_dur_info()
            self._skating_info.display_notes_panel(True)
            self._beep_manager.quick_chirp()

        elif input_key == "Call.Sk":
            self._display_main.set_btnSS("Start")
            self._skating_info.show_program_phase("Called")
            self._skating_info.start_call_timer()
            self._skating_info.reset_main_time()
            self._beep_manager.quick_chirp()

        elif input_key == "Chg.Dur":
            self._skating_info.cycle_to_next_available_duration()
            self._skating_info.display_dur_info()
            self._skating_info.display_time()
            self._skating_info.display_notes_panel()
            self._beep_manager.quick_chirp()            

        elif input_key == "Silent":
            self._beep_manager.set_quiet_mode()
            self._display_main.set_btnC("Noisy")
            self._skating_info.display_notes_panel()
            self._beep_manager.quick_chirp()                       

        elif input_key == "Noisy":
            self._beep_manager.set_noisy_mode()
            self._display_main.set_btnC("Silent")
            self._skating_info.display_notes_panel()
            self._beep_manager.quick_chirp()     

        elif input_key == "Clk.Set":
            self.set_current_screen("todset")
            self._beep_manager.quick_chirp()

        else:
            pass


    def process_command_todset(self, input_key):
        if input_key == "Set":
            # actually write the displayed time to the TOD CLOCK board here
            self._rtc_manager.set_clock(self._display_todset.get_desired_hours(), 
                                        self._display_todset.get_desired_minutes(), 
                                        self._display_todset.get_desired_ampm())
            self.set_current_screen("watch")
            self._beep_manager.quick_chirp()          

        elif input_key == "Cancel":
            self.set_current_screen("watch")
            self._beep_manager.quick_chirp()         

        elif input_key == "+ H":
            self._display_todset.increment_desired_hours()
            self._beep_manager.quick_chirp()       

        elif input_key == "- H":
            self._display_todset.decrement_desired_hours()
            self._beep_manager.quick_chirp()        

        elif input_key == "+ M":
            self._display_todset.increment_desired_minutes()
            self._beep_manager.quick_chirp()       

        elif input_key == "- M":
            self._display_todset.decrement_desired_minutes()
            self._beep_manager.quick_chirp()     

        elif input_key == "AM/PM":
            self._display_todset.toggle_desired_ampm()
            self._beep_manager.quick_chirp()

        else:
            pass