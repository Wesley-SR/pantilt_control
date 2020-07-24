import pantilt_control_code as pt
import time

teleop = pt.StandardCommands('/dev/ttyUSB0')

for i in range(0, 1):


    teleop.teleoperation('left_and_up', 60)
    time.sleep(0.8)
    teleop.teleoperation('right_and_up', 60)
    time.sleep(0.8)
    teleop.teleoperation('left_and_up', 60)
    time.sleep(0.8)
    teleop.teleoperation('right_and_up', 60)
    time.sleep(0.8)
    teleop.teleoperation('left_and_down', 60)
    time.sleep(0.8)
    teleop.teleoperation('right_and_down', 60)
    time.sleep(0.8)
    teleop.teleoperation('left_and_down', 60)
    time.sleep(0.8)
    teleop.teleoperation('right_and_down', 60)
    time.sleep(0.8)


    teleop.stop()
    
    # teleop.teleoperation('right_and_up', 60)
    # time.sleep(1)
    # teleop.teleoperation('left_and_up', 60)
    #  time.sleep(1)
    # teleop.teleoperation('right_and_up', 60)
    # time.sleep(1)
    # teleop.teleoperation('left_and_up', 60)
    # time.sleep(1)
    # teleop.teleoperation('right_and_down', 60)
    # time.sleep(1)
    # teleop.teleoperation('left_and_down', 60)
    # teleop.teleoperation('right_and_down', 60)
    # time.sleep(1)
    # teleop.teleoperation('left_and_down', 60)
    # time.sleep(1)
    
    teleop.stop()


'''
# --------------- Advanced comands
set_pt = pt.AdvancedCommands('/dev/ttyUSB0')  # Enter with the pantilt USB port
set_pt.set_angle('tilt', 0)
set_pt.set_angle('pan', 100)

'''


'''
    teleop.teleoperation('left', 60)
    time.sleep(1.5)
    teleop.teleoperation('right', 60)
    time.sleep(3)
    teleop.teleoperation('left', 60)
    time.sleep(1.5)
    teleop.teleoperation('left_and_down', 60)
    time.sleep(1.5)
    teleop.teleoperation('right_and_down', 60)
    time.sleep(1.5)
'''