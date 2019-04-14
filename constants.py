"""
CONSTANTS (USER UPDATED)
"""

import datetime
import holidays

DVID = '/media/nkinar/sdcard/display-video/'       	# video location
DPICT = '/media/nkinar/sdcard/display-pict/'       	# picture location
START_TV_TIME = datetime.time(8, 0, 0)             	# 8 AM as the start time for TV
END_TV_TIME = datetime.time(17, 0, 0)           	# 5 PM as the end time for TV images
DELAY_WAIT_SEC = 15                              	# wait time to check the main loop
SECS_PER_PICTURE = 3                             	# Time between each picture
RUN_ON_WEEKEND = False                            	# True to run on the weekend
RUN_ON_HOLIDAY = False                         		# True to run during a statuatory holiday

# define holidays in Canada or another country (change country and province/state as required)
CA_HOLIDAYS = holidays.CountryHoliday('CA', prov='SK')

# extension for videos
VIDEO_EXT = '.mp4'
