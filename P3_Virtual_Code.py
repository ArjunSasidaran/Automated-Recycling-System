ip_address = 'localhost' # Enter your IP Address here
project_identifier = 'P3B' # Enter the project identifier i.e. P3A or P3B

# SERVO TABLE CONFIGURATION
short_tower_angle = 315 # enter the value in degrees for the identification tower 
tall_tower_angle = 90 # enter the value in degrees for the classification tower
drop_tube_angle = 180 # enter the value in degrees for the drop tube. clockwise rotation from zero degrees

# BIN CONFIGURATION
# Configuration for the colors for the bins and the lines leading to those bins.
# Note: The line leading up to the bin will be the same color as the bin 

bin1_offset = 0.13 # offset in meters
bin1_color = [1,0,0] # e.g. [1,0,0] for red
bin1_metallic = False

bin2_offset = 0.13
bin2_color = [0,1,0]
bin2_metallic = False

bin3_offset = 0.13
bin3_color = [0,0,1]
bin3_metallic = False

bin4_offset = 0.13
bin4_color = [0,0,0]
bin4_metallic = False
#--------------------------------------------------------------------------------
import sys
sys.path.append('../')
from Common.simulation_project_library import *

hardware = False
if project_identifier == 'P3A':
    table_configuration = [short_tower_angle,tall_tower_angle,drop_tube_angle]
    configuration_information = [table_configuration, None] # Configuring just the table
    QLabs = configure_environment(project_identifier, ip_address, hardware,configuration_information).QLabs
    table = servo_table(ip_address,QLabs,table_configuration,hardware)
    arm = qarm(project_identifier,ip_address,QLabs,hardware)
else:
    table_configuration = [short_tower_angle,tall_tower_angle,drop_tube_angle]
    bin_configuration = [[bin1_offset,bin2_offset,bin3_offset,bin4_offset],[bin1_color,bin2_color,bin3_color,bin4_color],[bin1_metallic,bin2_metallic, bin3_metallic,bin4_metallic]]
    configuration_information = [table_configuration, bin_configuration]
    QLabs = configure_environment(project_identifier, ip_address, hardware,configuration_information).QLabs
    table = servo_table(ip_address,QLabs,table_configuration,hardware)
    arm = qarm(project_identifier,ip_address,QLabs,hardware)
    bot = qbot(0.1,ip_address,QLabs,project_identifier,hardware)
#--------------------------------------------------------------------------------
# STUDENT CODE BEGINS
#---------------------------------------------------------------------------------
import random
import time

# variable declaration
bin_destination = None 
properties = None 
has_loaded = True

bin_color = {
    'Bin01':bin1_color,
    'Bin02':bin2_color,
    'Bin03':bin3_color,
    'Bin04':bin4_color
}

# get home x and y position of qbot
home_x, home_y, _ = bot.position()
# speed of qbot
speed = 0.05

def dispense_container():
    # generates a random container 
    container_Id = random.randint(0,6)
    # dispenses container and returns properties in a three item list
    properties = table.dispense_container(container_Id,True)
    print(properties)
    return properties

def move_container(container_count):
    # picks up container and moves arm to hopper
    arm.move_arm(0.659,0.0,0.279)
    time.sleep(2)
    arm.control_gripper(36)
    time.sleep(2)
    arm.move_arm(0.04,-0.574,0.570)
    time.sleep(2)

    # depending on the number of containers in hopper, the arm moves to a different spot on hopper
    if container_count == 1:
        arm.rotate_base(-16)
        time.sleep(1)
        arm.rotate_elbow(5)
        time.sleep(2)
        arm.control_gripper(-15)
        time.sleep(3)
        arm.rotate_shoulder(-40)
        time.sleep(0.5)
        arm.home()
    if container_count == 2:
        arm.rotate_base(-6.5)
        time.sleep(1)
        arm.rotate_elbow(5)
        time.sleep(2)
        arm.control_gripper(-15)
        time.sleep(3)
        arm.rotate_shoulder(-40)
        time.sleep(2)
        arm.home()
    if container_count == 3:
        arm.rotate_base(2)
        time.sleep(1)
        arm.rotate_elbow(5)
        time.sleep(2)
        arm.control_gripper(-15)
        time.sleep(3)
        arm.rotate_shoulder(-40)
        time.sleep(2)
        arm.home()
   


def load_container():
    #variable declaration
    global bin_destination, properties, has_loaded
    total_mass = 0
    container_count = 0
    flag = True 

    # checks if less than three containers are on hopper
    while(container_count < 3 and flag):
        # checks if there is a container currently dispensed
        if has_loaded:
            properties = dispense_container()
        # checks if there are any previous containers on bin 
        if container_count == 0:
            # get location of the first bin 
            first_bin = properties[2]
            bin_destination = bin_color[first_bin]
            has_loaded = True
        mass = properties[1] 
        curr_bin = properties[2] # bin location of the container currently being placed in hopper
        container_count += 1
        total_mass += mass
        # checks if current bin is going to same location as first bin and if total mass on hopper is less than 90
        if(first_bin == curr_bin and total_mass <= 90):
            move_container(container_count)
            time.sleep(2)
        else:
            has_loaded = False
            flag = False


def follow_line(left, right):
    # if both IR sensors detect line
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


def drive_to_bin_and_dispense(target_color):
    # activating sensors
    bot.activate_line_following_sensor()
    bot.activate_color_sensor()
    bot.activate_ultrasonic_sensor()
    # threshold distance to check color
    threshold = 0.1
    # flag for loop
    is_finished = False
    
    while not is_finished:
        # get distance to closest bin
        distance = bot.read_ultrasonic_sensor()
        # if qbot is close enough to a bin
        if distance <= threshold:
            # check the color of the bin
            detected_color = bot.read_color_sensor()[0]
            # if the color is the same as the target bin
            if detected_color == target_color:
                # dispense the containers into bin and exit loop
                bot.rotate(-10)
                bot.forward_distance(0.2)
                dispense_bin()
                is_finished = True

        # get left and right IR sensors
        left_IR, right_IR = bot.line_following_sensors()
        # follow line based on sensor input
        follow_line(left_IR, right_IR)

    # deactivate sensors and stop qbot
    bot.deactivate_color_sensor()
    bot.deactivate_ultrasonic_sensor()
    bot.stop()


def drive_to_home():
    # get initial x and y position of qbot
    x, y, _ = bot.position()
    # while position of qbot is not the home position
    while abs(home_x - x) > 0.04 or abs(home_y - y) > 0.04:
        # update most recent position
        x, y, _ = bot.position()
        # get left and right IR sensors
        left_IR, right_IR = bot.line_following_sensors()
        # follow line based on sensor input
        follow_line(left_IR, right_IR)

    # stop qbot and deactivate line sensors
    bot.stop()
    bot.deactivate_line_following_sensor()

    
def dispense_bin():
    # activate stepper motor
    bot.activate_stepper_motor()
    
    # dump containers
    bot.rotate_hopper(50)
    time.sleep(2.0)
    bot.rotate_hopper(-50)

    # deactivate stepper motor
    bot.deactivate_stepper_motor()


def main():
    # initial qbot and loading setup
    # we need this since the qbot never returns to the
    # exact same position as the first one
    
    bot.rotate(-100)
    load_container()
    bot.rotate(100)
    
    # main loop
    while True:
        # drive qbot to correct bin and dispense containers
        drive_to_bin_and_dispense(bin_destination)
        # drive back to home position
        drive_to_home()
        
        # adjust qbot to loading position
        bot.forward_distance(0.1)
        bot.rotate(90)
        bot.forward_distance(0.055)

        # load containers onto qbot
        load_container()

        # return qbot to line path
        bot.rotate(-200)
        bot.forward_distance(0.055)
        bot.rotate(100)


# running main
main()

#---------------------------------------------------------------------------------
# STUDENT CODE ENDS
#---------------------------------------------------------------------------------
    

    

