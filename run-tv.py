"""
SWSL-TV
A simple Python project to display images and/or video on an HDMI TV using
the Asus Tinkerboard S and Python scripts.  This is ideal for a laboratory TV
that shows pictures of research to lab visitors.

I want to watch television! I want to watch television! I want to watch television!
--Mike Teavee
Charlie and the Chocolate Factory by Roald Dahl

SOFTWARE REQUIREMENTS
Linux (Tinker OS, most recent version)
python3
xset
feh         					to display images
gstreamer and gst-launch       	to display video

PYTHON3 libraries (installed using pip, can be installed into a virtualenv if required)
delegator
holidays

HARDWARE REQUIREMENTS
Asus Tinkerboard S with Tinker OS installed

SETUP
See github readme.md for this project

REFERENCES:
[1] https://stackoverflow.com/questions/10048249/

Copyright 2019 Nicholas J. Kinar
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated 
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, 
copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom 
the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

# IMPORTS
import os
import time
import datetime
from threading import Thread

import delegator
import holidays
from constants import *


# NON-CHANGING CONSTANTS
DRIVE_MNT_CMD = 'mount'
OFF_MONITOR_CMD = 'xset dpms force off'
ON_MONITOR_CMD = 'xset dpms force on'
DPMS_FIRST_CMD = 'xset -dpms'
DPMS_SECOND_CMD = 'xset s off'
CHECK_MONITOR_CMD = 'xset -q'
MONITOR_IS_STR = 'Monitor is'
ON_STR = 'On'
OFF_STR = 'Off'
VIDEO_RUN_CMD = 'gst-launch-1.0 playbin uri=file:{0} video_sink=rkximagesink'
PICTURE_CMD = 'feh --recursive --randomize --auto-zoom -F -D {0} --auto-rotate --cycle-once'
##########################################################


class RunTV:

    def __init__(self):
        self.vid_run = None
        self.pict_run = None
        self.run_flag = False

    def turn_off_monitor(self):
        delegator.run(OFF_MONITOR_CMD)

    def turn_on_monitor(self):
        delegator.run(DPMS_FIRST_CMD)
        delegator.run(DPMS_SECOND_CMD)

    def get_all_files_in_dir(self, folder, ext):
        out = []
        try:
            for file in os.listdir(folder):
                if file.endswith(ext):
                    out.append(folder + file)
            return out
        except FileNotFoundError:
            return []

    def get_all_video_files_in_dir(self):
        return self.get_all_files_in_dir(DVID, VIDEO_EXT)

    def run_all_video_in_dir(self):
        fn = self.get_all_video_files_in_dir()
        if not fn:  # list is empty, no files are in directory
            return
        for f in fn:
            cmd = VIDEO_RUN_CMD.format(f)
            self.vid_run = delegator.run(cmd, block=False)
            self.vid_run.block()
            if not self.run_flag:
                return

    def check_dir_empty(self, d):
        if os.path.exists(d) and os.path.isdir(d):
            if not os.listdir(d):
                return True
            else:
                return False
        else:
            return True

    def display_all_pict_in_dir(self):
        if self.check_dir_empty(DPICT):
            return
        cmd = PICTURE_CMD.format(SECS_PER_PICTURE)
        self.pict_run = delegator.run(cmd, cwd=DPICT)
        self.pict_run.block()

    def check_run_flag(self):
        return self.run_flag

    def run_all_display(self):
        self.run_flag = True
        while True:
            if not self.check_run_flag():
                return
            self.run_all_video_in_dir()
            if not self.check_run_flag():
                return
            self.display_all_pict_in_dir()
            if not self.check_run_flag():
                return

    def run_all_display_thread(self):
        self.run_all_display()

    def kill_process(self, x):
        if x is not None:
            x.kill()

    def killall_process(self):
        self.run_flag = False
        self.kill_process(self.vid_run)
        self.kill_process(self.pict_run)

    def turn_on_operation(self):
        self.turn_on_monitor()
        self.run_all_display()

    def turn_off_operation(self):
        self.turn_off_monitor()
        self.killall_process()

    def turn_on_operation_thread(self):
        thread = Thread(target=self.turn_on_operation)
        thread.start()

    def turn_off_operation_thread(self):
        thread = Thread(target=self.turn_off_operation)
        thread.start()
        thread.join()

    def get_time(self):
        return datetime.datetime.now()

    def is_weekday(self, dt=None):
        if dt is None:
            dt = self.get_time()
        weekno = dt.weekday()
        if weekno < 5:
            return True
        return False

    def is_holiday(self, dt=None):
        if dt is None:
            dt = self.get_time()
        if dt in CA_HOLIDAYS:
            return True
        return False

    def is_time_between(self, begin_time, end_time):
        """
        :param begin_time:
        :param end_time:
        :param check_time:
        :return:
        """

        # check to see if we want to run on Sat/Sun
        dt = self.get_time()
        if not self.is_weekday(dt) and not RUN_ON_WEEKEND:
            return False

        # check to see if this is a holiday
        if self.is_holiday(dt) and not RUN_ON_HOLIDAY:
            return False

        # time must be between hours of operation (reference [1])
        check_time = dt.time()
        if begin_time < end_time:
            return check_time >= begin_time and check_time <= end_time
        else:  # crosses midnight
            return check_time >= begin_time or check_time <= end_time

    def check_time(self):
        return self.is_time_between(START_TV_TIME, END_TV_TIME)

    def startup(self):
        self.turn_off_operation()       # ensure that the TV is off to start
        while True:
            if self.check_time():       # turn on the TV only if we are between the hours
                if not self.run_flag:
                    self.turn_on_operation_thread()
            else:   # turn off the TV if we are not between the hours
                if self.run_flag:
                    self.turn_off_operation_thread()
            # WAIT
            time.sleep(DELAY_WAIT_SEC)


######################################################################################


def main():
    rtv = RunTV()
    rtv.startup()


if __name__ == '__main__':
    main()
