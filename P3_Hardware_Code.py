ip_address = '' # Enter your IP Address here
project_identifier = 'P3B' # Enter the project identifier i.e. P3A or P3B
#--------------------------------------------------------------------------------
import sys
sys.path.append('../')
from Common.hardware_project_library import *

hardware = True
QLabs = configure_environment(project_identifier, ip_address, hardware).QLabs
if project_identifier == 'P3A':
    arm = qarm(project_identifier,ip_address,QLabs,hardware)
    table = servo_table(ip_address,QLabs,None,hardware)
else:
    speed = 0.1 # in m/s
    bot = qbot(speed,ip_address,QLabs,project_identifier,hardware)
#--------------------------------------------------------------------------------
# STUDENT CODE BEGINS
#---------------------------------------------------------------------------------
import time

bot.activate_line_following_sensor()
bot.activate_color_sensor()
bot.activate_stepper_motor()
speed = 0.05

while True:
    try:
        detected_color = bot.read_color_sensor()[0]
        if detected_color[0] > 0.6:
            bot.stop()
            bot.rotate_stepper_ccw(1.0)
            time.sleep(1.0)
            bot.rotate_stepper_cw(1.0)
            break
    except:
        pass
    left, right = bot.line_following_sensors()
    
    if left == right == 1:
        # move qbot straight
        bot.set_wheel_speed([speed, speed])
    # if only left sensor detects line
    elif left == 1 and right == 0:
        # move qbot slightly to the left
        bot.set_wheel_speed([speed * 0.5, speed])
    # if only right sensor detects line
    elif left == 0 and right == 1:
        # move qbot slightly to the right
        bot.set_wheel_speed([speed, speed * 0.5])

bot.deactivate_stepper_motor()
bot.deactivate_line_following_sensor()
bot.deactivate_color_sensor()



#---------------------------------------------------------------------------------
# STUDENT CODE ENDS
#---------------------------------------------------------------------------------
    

    

