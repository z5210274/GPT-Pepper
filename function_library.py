import time

# Head Movements
def head_rotate_up(motion, speed, delay, radians):
    """
    Docstring for head_rotate_up
    This function rotates the robot's head up by the specified radians.
    Its angle limit is -0.7068 radians.
    """
    current = motion.getAngles("HeadPitch", True)[0]
    if (current - radians) < -0.7068:
        radians = -0.7 - current
    motion.changeAngles("HeadPitch", -1*abs(radians), speed)
    time.sleep(delay)

def head_rotate_down(motion, speed, delay, radians):
    """
    Docstring for head_rotate_down
    This function rotates the robot's head down by the specified radians.
    Its angle limit is 0.6371 radians.
    """
    current = motion.getAngles("HeadPitch", True)[0]
    if (current + radians) > 0.6371:
        radians = 0.63 - current
    motion.changeAngles("HeadPitch", abs(radians), speed)
    time.sleep(delay)

def head_rotate_left(motion, speed, delay, radians):
    """
    Docstring for head_rotate_left
    This function rotates the robot's head left by the specified radians.
    Its angle limit is 2.0857 radians.
    """
    current = motion.getAngles("HeadYaw", True)[0]
    if (current + radians) > 2.0857:
        radians = 2.08 - current
    motion.changeAngles("HeadYaw", abs(radians), speed)
    time.sleep(delay)

def head_rotate_right(motion, speed, delay, radians):
    """
    Docstring for head_rotate_right
    This function rotates the robot's head right by the specified radians.
    Its angle limit is -2.0857 radians.
    """
    current = motion.getAngles("HeadYaw", True)[0]
    if (current - radians) < -2.0857:
        radians = -2.08 - current
    motion.changeAngles("HeadYaw", -1*abs(radians), speed)
    time.sleep(delay)

# Shoulder Movements
def left_shoulder_rotate_front(motion, speed, delay, radians):
    """
    Docstring for left_shoulder_rotate_front
    This function rotates the left shoulder to the front by the specified radians.
    Its angle limit is -2.0857 radians.
    """
    current = motion.getAngles("LShoulderPitch", True)[0]
    if (current - radians) < -2.0857:
        radians = -2.08 - current
    motion.changeAngles("LShoulderPitch", -1*abs(radians), speed)
    time.sleep(delay)

def right_shoulder_rotate_front(motion, speed, delay, radians):
    """
    Docstring for right_shoulder_rotate_front
    This function rotates the right shoulder to the front by the specified radians.
    Its angle limit is -2.0857 radians.
    """
    current = motion.getAngles("RShoulderPitch", True)[0]
    if (current - radians) < -2.0857:
        radians = -2.08 - current
    motion.changeAngles("RShoulderPitch", -1*abs(radians), speed)
    time.sleep(delay)

def left_shoulder_rotate_back(motion, speed, delay, radians):
    """
    Docstring for left_shoulder_rotate_back
    This function rotates the left shoulder to the back by the specified radians.
    Its angle limit is 2.0857 radians.
    """
    current = motion.getAngles("LShoulderPitch", True)[0]
    if (current + radians) > 2.0857:
        radians = 2.08 - current
    motion.changeAngles("LShoulderPitch", abs(radians), speed)
    time.sleep(delay)

def right_shoulder_rotate_back(motion, speed, delay, radians):
    """
    Docstring for right_shoulder_rotate_back    
    This function rotates the right shoulder to the back by the specified radians.
    Its angle limit is 2.0857 radians.
    """
    current = motion.getAngles("RShoulderPitch", True)[0]
    if (current + radians) > 2.0857:
        radians = 2.08 - current
    motion.changeAngles("RShoulderPitch", abs(radians), speed)
    time.sleep(delay)

def left_shoulder_rotate_up(motion, speed, delay, radians):
    """
    Docstring for left_shoulder_rotate_up
    This function rotates the left shoulder sideways up by the specified radians.
    Its angle limit is 1.5620 radians.
    """
    current = motion.getAngles("LShoulderRoll", True)[0]
    if (current + radians) > 1.5620:
        radians = 1.56 - current
    motion.changeAngles("LShoulderRoll", abs(radians), speed)
    time.sleep(delay)

def right_shoulder_rotate_up(motion, speed, delay, radians):
    """
    Docstring for right_shoulder_rotate_up
    This function rotates the right shoulder sideways up by the specified radians.
    Its angle limit is -1.5620 radians.
    """
    current = motion.getAngles("RShoulderRoll", True)[0]
    if (current - radians) < -1.5620:
        radians = -1.56 - current
    motion.changeAngles("RShoulderRoll", -1*abs(radians), speed)
    time.sleep(delay)

def left_shoulder_rotate_down(motion, speed, delay, radians):
    """
    Docstring for left_shoulder_rotate_down
    This function rotates the left shoulder sideways down by the specified radians.
    Its angle limit is 0.0087 radians.
    """
    current = motion.getAngles("LShoulderRoll", True)[0]
    if (current - radians) < 0.0087:
        radians = 0.01 - current
    motion.changeAngles("LShoulderRoll", -1*abs(radians), speed)
    time.sleep(delay)

def right_shoulder_rotate_down(motion, speed, delay, radians):
    """
    Docstring for right_shoulder_rotate_down
    This function rotates the right shoulder sideways down by the specified radians.
    Its angle limit is -0.0087 radians.
    """
    current = motion.getAngles("RShoulderRoll", True)[0]
    if (current + radians) > -0.0087:
        radians = -0.01 - current
    motion.changeAngles("RShoulderRoll", abs(radians), speed)
    time.sleep(delay)

def left_shoulder_rotate_in(motion, speed, delay, radians):
    """
    Docstring for left_shoulder_rotate_in
    This function rotates the left shoulder/elbow inwards by the specified radians.
    Its angle limit is 2.0857 radians.
    """
    current = motion.getAngles("LElbowYaw", True)[0]
    if (current + radians) > 2.0857:
        radians = 2.08 - current
    motion.changeAngles("LElbowYaw", abs(radians), speed)
    time.sleep(delay)

def right_shoulder_rotate_in(motion, speed, delay, radians):
    """
    Docstring for right_shoulder_rotate_in
    This function rotates the right shoulder/elbow inwards by the specified radians.
    Its angle limit is -2.0857 radians.
    """
    current = motion.getAngles("RElbowYaw", True)[0]
    if (current - radians) < -2.0857:
        radians = -2.08 - current
    motion.changeAngles("RElbowYaw", -1*abs(radians), speed)
    time.sleep(delay)

def left_shoulder_rotate_out(motion, speed, delay, radians):
    """
    Docstring for left_shoulder_rotate_out
    This function rotates the left shoulder/elbow outwards by the specified radians.
    Its angle limit is -2.0857 radians.
    """
    current = motion.getAngles("LElbowYaw", True)[0]
    if (current - radians) < -2.0857:
        radians = -2.08 - current
    motion.changeAngles("LElbowYaw", -1*abs(radians), speed)
    time.sleep(delay)

def right_shoulder_rotate_out(motion, speed, delay, radians):
    """
    Docstring for right_shoulder_rotate_out
    This function rotates the right shoulder/elbow outwards by the specified radians.
    Its angle limit is 2.0857 radians.
    """
    current = motion.getAngles("RElbowYaw", True)[0]
    if (current + radians) > 2.0857:
        radians = 2.08 - current
    motion.changeAngles("RElbowYaw", abs(radians), speed)
    time.sleep(delay)

# Elbow Movements
def left_elbow_extend(motion, speed, delay, radians):
    """
    Docstring for left_elbow_extend
    This function extends the left elbow by the specified radians.
    Its angle limit is -0.0087 radians.
    """
    current = motion.getAngles("LElbowRoll", True)[0]
    if (current + radians) > -0.0087:
        radians = -0.01 - current 
    motion.changeAngles("LElbowRoll", abs(radians), speed)
    time.sleep(delay)

def right_elbow_extend(motion, speed, delay, radians):
    """
    Docstring for right_elbow_extend
    This function extends the right elbow by the specified radians.
    Its angle limit is 0.0087 radians.
    """
    current = motion.getAngles("RElbowRoll", True)[0]
    if (current - radians) < 0.0087:
        radians = 0.01 - current
    motion.changeAngles("RElbowRoll", -1*abs(radians), speed)
    time.sleep(delay)

def left_elbow_contract(motion, speed, delay, radians):
    """
    Docstring for left_elbow_contract
    This function contracts the left elbow by the specified radians.
    Its angle limit is -1.5620 radians.
    """
    current = motion.getAngles("LElbowRoll", True)[0]
    if (current - radians) < -1.5620:
        radians = -1.56 - current
    motion.changeAngles("LElbowRoll", -1*abs(radians), speed)
    time.sleep(delay)

def right_elbow_contract(motion, speed, delay, radians):
    """
    Docstring for right_elbow_contract
    This function contracts the right elbow by the specified radians.
    Its angle limit is 1.5620 radians.
    """
    current = motion.getAngles("RElbowRoll", True)[0]
    if (current + radians) > 1.5620:
        radians = 1.56 - current
    motion.changeAngles("RElbowRoll", abs(radians), speed)
    time.sleep(delay)

# Wrist Movements
def left_wrist_rotate_in(motion, speed, delay, radians):
    """
    Docstring for left_wrist_rotate_in
    This function rotates the left wrist inwards by the specified radians.
    Its angle limit is 1.8239 radians.
    """
    current = motion.getAngles("LWristYaw", True)[0]
    if (current + radians) > 1.8239:
        radians = 1.82 - current
    motion.changeAngles("LWristYaw", abs(radians), speed)
    time.sleep(delay)

def right_wrist_rotate_in(motion, speed, delay, radians):
    """
    Docstring for right_wrist_rotate_in
    This function rotates the right wrist inwards by the specified radians.
    Its angle limit is -1.8239 radians.
    """
    current = motion.getAngles("RWristYaw", True)[0]
    if (current - radians) < -1.8239:
        radians = -1.82 - current
    motion.changeAngles("RWristYaw", -1*abs(radians), speed)
    time.sleep(delay)

def left_wrist_rotate_out(motion, speed, delay, radians):
    """
    Docstring for left_wrist_rotate_out
    This function rotates the left wrist outwards by the specified radians.
    Its angle limit is -1.8239 radians.
    """
    current = motion.getAngles("LWristYaw", True)[0]
    if (current - radians) < -1.8239:
        radians = -1.82 - current
    motion.changeAngles("LWristYaw", -1*abs(radians), speed)
    time.sleep(delay)

def right_wrist_rotate_out(motion, speed, delay, radians):
    """
    Docstring for right_wrist_rotate_out
    This function rotates the right wrist outwards by the specified radians.
    Its angle limit is 1.8239 radians.
    """
    current = motion.getAngles("RWristYaw", True)[0]
    if (current + radians) > 1.8239:
        radians = 1.82 - current
    motion.changeAngles("RWristYaw", abs(radians), speed)
    time.sleep(delay)

# Hand Movements
def left_hand_open(motion, speed, delay, radians):
    """
    Docstring for left_hand_open
    This function opens the left hand by the specified radians.
    Its angle limit is 1.0 radians.
    """
    current = motion.getAngles("LHand", True)[0]
    if (current + radians) > 1.0:
        radians = 0.95 - current
    motion.changeAngles("LHand", abs(radians), speed)
    time.sleep(delay)

def right_hand_open(motion, speed, delay, radians):
    """
    Docstring for right_hand_open
    This function opens the right hand by the specified radians.
    Its angle limit is 1.0 radians.
    """
    current = motion.getAngles("RHand", True)[0]
    if (current + radians) > 1.0:
        radians = 0.95 - current
    motion.changeAngles("RHand", abs(radians), speed)
    time.sleep(delay)

def left_hand_close(motion, speed, delay, radians):
    """
    Docstring for left_hand_close
    This function closes the left hand by the specified radians.
    Its angle limit is 0.0 radians.
    """
    current = motion.getAngles("LHand", True)[0]
    if (current - radians) < 0.0:
        radians = 0.05 - current
    motion.changeAngles("LHand", -1*abs(radians), speed)
    time.sleep(delay)

def right_hand_close(motion, speed, delay, radians):
    """
    Docstring for right_hand_close
    This function closes the right hand by the specified radians.
    Its angle limit is 0.0 radians.
    """
    current = motion.getAngles("RHand", True)[0]
    if (current - radians) < 0.0:
        radians = 0.05 - current
    motion.changeAngles("RHand", -1*abs(radians), speed)
    time.sleep(delay)

# Hip Movements
def hip_rotate_left(motion, speed, delay, radians):
    """
    Docstring for hip_rotate_left
    This function bends the hip to the left by the specified radians.
    Its angle limit is 0.5149 radians.
    """
    current = motion.getAngles("HipRoll", True)[0]
    if (current + radians) > 0.5149:
        radians = 0.51 - current
    motion.changeAngles("HipRoll", abs(radians), speed)
    time.sleep(delay)

def hip_rotate_right(motion, speed, delay, radians):
    """
    Docstring for hip_rotate_right
    This function bends the hip to the right by the specified radians.
    Its angle limit is -0.5149 radians.
    """
    current = motion.getAngles("HipRoll", True)[0]
    if (current - radians) < -0.5149:
        radians = -0.51 - current
    motion.changeAngles("HipRoll", -1*abs(radians), speed)
    time.sleep(delay)

def hip_rotate_front(motion, speed, delay, radians):
    """
    Docstring for hip_rotate_front
    This function bends the hip forward by the specified radians.
    Its angle limit is -1.0385 radians.
    """
    current = motion.getAngles("HipPitch", True)[0]
    if (current - radians) < -1.0385:
        radians = -1.03 - current
    motion.changeAngles("HipPitch", -1*abs(radians), speed)
    time.sleep(delay)

def hip_rotate_back(motion, speed, delay, radians):
    """
    Docstring for hip_rotate_back
    This function bends the hip backward by the specified radians.
    Its angle limit is 1.0835 radians.
    """
    current = motion.getAngles("HipPitch", True)[0]
    if (current + radians) > 1.0835:
        radians = 1.08 - current
    motion.changeAngles("HipPitch", abs(radians), speed)
    time.sleep(delay)

# Knee Movements
def knee_rotate_front(motion, speed, delay, radians):
    """
    Docstring for knee_rotate_front
    This function bends the knee forward by the specified radians.
    Its angle limit is -0.5149 radians.
    """
    current = motion.getAngles("KneePitch", True)[0]
    if (current - radians) < -0.5149:
        radians = -0.51 - current
    motion.changeAngles("KneePitch", -1*abs(radians), speed)
    time.sleep(delay)

def knee_rotate_back(motion, speed, delay, radians):
    """
    Docstring for knee_rotate_back
    This function bends the knee backward by the specified radians.
    Its angle limit is 0.5149 radians.
    """
    current = motion.getAngles("KneePitch", True)[0]
    if (current + radians) > 0.5149:
        radians = 0.51 - current
    motion.changeAngles("KneePitch", abs(radians), speed)
    time.sleep(delay)

# Wheel Movements
def wheel_move_direction(motion, x, y, delay):
    motion.moveToward(x, y, 0)
    
def wheel_move_towards(motion, x, y, delay):
    motion.moveTo(x, y, 0)
    
def wheel_turn_left(motion, delay, radians):
    motion.moveTo(0, 0, radians)

def wheel_turn_right(motion, delay, radians):
    motion.moveTo(0, 0, -1*radians)

# Angle Interpolation for Simultaneous Joint Movements
def angle_interpolation(motion, names, angles, time_to_reach):
    """
    Docstring for angle_interpolation
    Set all angles in the provided names list to the corresponding angles in the angles list over the specified time_to_reach.
    - names: list of joint names as strings (e.g., ["RShoulderPitch", "LShoulderRoll"])
    - angles: list of target angles for each joint in radians (e.g., [1.0, -0.5])
    - time_to_reach: a float value of how many seconds to reach the target angles (e.g., 2.0)
    - True: ensures that all joints start and finish their movement at the same time
    """
    motion.angleInterpolation(names, angles, time_to_reach, True)