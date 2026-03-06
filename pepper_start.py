import inspect
from naoqi import ALProxy
import time
import threading
import sys
from function_library import *
import urllib2
import json
import sys
import codecs
import os
import paramiko
import cv2
import base64
import numpy as np

#PEPPER_IP = "192.168.1.143"
PEPPER_IP = "10.68.139.169"
#PEPPER_IP = "172.21.53.169"
PEPPER_PORT = 9559
recorder_filepath = '/home/nao/recordings/input.wav'
local_path = './recordings/input.wav'
recording = False
active_tablet = False
username = "nao"
password = "pepper"

system_prompt = """You are an assistive social robot Pepper, designed by Softbank Robotics designed to support and engage people in friendly, helpful conversations.
Your personality should be warm, polite, and encouraging. You are currently at a university and here is some information about the university on the website 'https://www.university.edu.au/'
You should:  
- Speak clearly and concisely so speech can be spoken aloud by text-to-speech.  
- Use simple words when possible, but remain respectful and natural.  
- Always stay positive, supportive, and patient.  
- When asked for help, give practical, step-by-step suggestions.  
- If you don't know something, say so honestly and redirect politely.  
- Avoid long paragraphs; keep answers short enough to be spoken easily.  
- Never output emojis, code formatting, or markdown just plain text sentences.  
- Do not roleplay as a human stay in your role as a helpful robot assistant.  
- Never say the phrase 'Hey Pepper'

Your goal is to make conversations smooth, supportive, and enjoyable."""

# A generic function to connect to any Pepper module
def connect_module(module_name, ip, port):
    try:
        proxy = ALProxy(module_name, ip, port)
        print("Connected to", module_name)
        return proxy
    except Exception as e:
        print("Could not connect to", module_name)
        print(e)
        return None

def buffer_input(asr, tts, delay):
    time.sleep(delay)
    asr.pause(False)
    tts.say("Go ahead")
    time.sleep(delay)

# A function to error handle and run a behaviors
def run_behavior(behavior_mgr, behavior_name):
    if behavior_mgr.isBehaviorInstalled(behavior_name):
        if not behavior_mgr.isBehaviorRunning(behavior_name):
            threading.Thread(target=behavior_mgr.runBehavior, args=(behavior_name,)).start()
        else:
            print("Behavior is already running:", behavior_name)
    else:
        print("Behavior not installed:", behavior_name)

def voice_chatbot(conversation_history, result_container, current_angles,input):
    url = "http://127.0.0.1:5000"
    data = {
        "messages": conversation_history,
        "length": len(conversation_history),
        "gesture_code": "",
        "current_angles": current_angles,
        "text_input": input
    }
    tmp_history = conversation_history
    req = urllib2.Request(url, data=json.dumps(data), headers={"Content-Type": "application/json"})

    response = urllib2.urlopen(req)
    data = json.loads(response.read())

    gesture_code = data['gesture_code']
    lines = gesture_code.splitlines()
    cleaned = []
    for line in lines:
        if line.strip().startswith("```"):
            continue
        if line.strip() == "python":
            continue
        cleaned.append(line)
    gesture_code = "\n".join(cleaned)
    print("Generated Gesture Code:\n", gesture_code)

    output = data['messages'][data['length'] - 1]['content']
    #data['messages'][data['length'] - 1]['content'] = final_response

    #conversation_history.append({"role": "assistant", "content": output})

    #if len(conversation_history) > 40:
    conversation_history = data['messages']
    if tmp_history != conversation_history:
        print("Assistant: " + output)

    #result_container["output"] = output
    #result_container["conversation_history"] = conversation_history
    return output, gesture_code, conversation_history

def post_angles(angles):    
    url = "http://127.0.0.1:5003"

def vision_image(image):
    url = "http://127.0.0.1:5001"
    width = image[0]
    height = image[1]
    array = image[6]

    img = np.fromstring(array, dtype=np.uint8).reshape((height, width, 3))
    img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    _, img_encoded = cv2.imencode('.jpg', img_bgr)
    img_b64 = base64.b64encode(img_encoded.tobytes())

    data = {
        "image": img_b64
    }
    req = urllib2.Request(url, data=json.dumps(data), headers={"Content-Type": "application/json"})
    response = urllib2.urlopen(req)
    result = json.loads(response.read())
    persons = result.get("persons", [])

    persons = result.get("persons", [])
    if len(persons) > 0:
        # Track the first person
        p = persons[0]
        face_x = p["cx"]
        face_y = int(p["y1"] + (p["y2"] - p["y1"]) * 0.25)  # ~25% down from the top

        yaw, pitch = pixel_to_head_angles(face_x, face_y, width, height)

        #yaw, pitch = pixel_to_head_angles(p["cx"], p["cy"], width, height)
        #motion.setAngles(["HeadYaw", "HeadPitch"], [yaw, pitch], 0.1)
        head_yaw_limit = 0.4  # about 23 degrees
        if abs(yaw) > head_yaw_limit:
            # Rotate body towards the person
            motion.moveTo(0.0, 0.0, yaw)  # rotate in place by yaw
            # Reset head to center (optional)
            motion.setAngles("HeadYaw", 0.0, 0.2)
        print("Person detected at (cx, cy):", (p["cx"], p["cy"]), "-> Head angles (yaw, pitch):", (yaw, pitch))

    return persons

def pixel_to_head_angles(x, y, frame_width, frame_height):
    yaw_range = 1.0
    pitch_range = 0.5
    dx = (x - frame_width / 2) / float(frame_width / 2)
    dy = (y - frame_height / 2) / float(frame_height / 2)
    yaw = -dx * yaw_range
    pitch = -dy * pitch_range
    return yaw, pitch

def execute_generated_movement(code, motion):
    """Execute the generated movement code safely (Python 2.7)"""
    import time
    # Add necessary imports and variables
    setup_code = """
import time
from function_library import *
"""
    # Combine setup and generated code
    full_code = setup_code + "\n" + code

    # Create function namespace
    namespace = {
        'motion': motion,
    }

    # Execute the code
    exec full_code in namespace

    # Execute the main function if it exists
    if 'execute_movement' in namespace:
        func = namespace['execute_movement']
        argspec = inspect.getargspec(func)  # Python 2.7
        args_to_pass = []
        for arg in argspec.args:
            if arg == 'motion':
                args_to_pass.append(motion)
        func(*args_to_pass)

    return True


if __name__ == "__main__":
    # Connect to modules
    tts = connect_module("ALTextToSpeech", PEPPER_IP, PEPPER_PORT)
    #tts.say("Hello, I am connected.")
    asr = connect_module("ALSpeechRecognition", PEPPER_IP, PEPPER_PORT)
    motion = connect_module("ALMotion", PEPPER_IP, PEPPER_PORT)
    behavior_mgr = connect_module("ALBehaviorManager", PEPPER_IP, PEPPER_PORT)
    memory = connect_module("ALMemory", PEPPER_IP, PEPPER_PORT)
    battery_proxy = connect_module("ALBattery", PEPPER_IP, PEPPER_PORT)
    recorder = connect_module("ALAudioRecorder", PEPPER_IP, PEPPER_PORT)
    animated_speech = connect_module("ALAnimatedSpeech", PEPPER_IP, PEPPER_PORT)
    config = {"bodyLanguageMode": "contextual"}  
    speaking_movement = connect_module("ALSpeakingMovement", PEPPER_IP, PEPPER_PORT)
    #speaking_movement.setEnabled(True)
    tablet_service = connect_module("ALTabletService", PEPPER_IP, PEPPER_PORT)
    camera_proxy = connect_module("ALVideoDevice", PEPPER_IP, PEPPER_PORT)
    basic_awareness = connect_module("ALBasicAwareness", PEPPER_IP, PEPPER_PORT)
    recorder.stopMicrophonesRecording()
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(PEPPER_IP, username=username, password=password)

    #print(behavior_mgr.getInstalledBehaviors())

    conversation_history = []
    conversation_history.append({
        "role": "system", 
        "content": system_prompt
        #"content": "You are a helpful and social assistant robot/chatbot called Pepper, developed by Softbank Robotics. Please answer the user's questions and assist with tasks using no more than 3 sentences (Please keep it short). Please answer as if you are speaking to the person and not texting and using thing's like emojis. If you are responding with numbers, make sure to format them as words."
    })

    sys.stdout = codecs.getwriter("utf-8")(sys.stdout)

    if tts and motion and behavior_mgr and memory and asr and recorder and battery_proxy and ssh and animated_speech and speaking_movement and basic_awareness:
        print("All modules connected successfully.")
        #tts.say("Captain Pepper, on duty!")
        asr.pause(True)
        asr.setLanguage("English")
        #vocabulary = ["exit", "shrug", "hello", "repeat", "battery", "add word", "hey pepper"]
        vocabulary = ["hey pepper", "hi pepper", "show tablet", "close tablet", "show website", "close website", "open google", "play tic tac toe", "open manual", "go ahead", "hello there"]
        asr.setVocabulary(vocabulary, True)
        asr.pause(False)
        subscriber = asr.subscribe("Test_ASR")
        # Camera Parameters
        camera_id = 0
        resolution = 2
        color_space = 11
        fps = 10
        vision = camera_proxy.subscribeCamera("pepper_stream", camera_id, resolution, color_space, fps)
        basic_awareness.startAwareness()
        basic_awareness.setEngagementMode("FullyEngaged")
        basic_awareness.setTrackingMode("BodyRotation")

        memory.insertData("WordRecognized", ["", 0.0])

        while True:
            data = memory.getData("WordRecognized")
            #print(data)
            #command = data[0].strip().lower() if data and data[1] >= 0.45 else ""
            #conf = data[1]
            '''if data[1] < 0.5:
                print(data[0])
                print(data[1])'''
            #command = command.replace("<...>", "").replace("/...>","").strip()

            '''image = camera_proxy.getImageRemote(vision)
            if image is not None:
                print(threading.Thread(target=vision_image, args=(image,)).start())'''

            command = ""
            command = raw_input("Text input command: ").strip().lower() if command == "" else command
            command = raw_input("Text input command: ").strip().lower()
            
            '''if command != "":
                #print(command)
                conversation_history.append({"role": "user", "content": command})
                output, conversation_history = chatbot(conversation_history)
                tts.say(str(output))'''

            if command == "exit":
                asr.unsubscribe("Test_ASR")
                tts.say("Goodbye!")
                print("Exiting...")
                memory.insertData("WordRecognized", ["", 0.0])
                break
            
            if active_tablet == False:
                if command == "show tablet" or command == "show website":
                    print("Showing tablet")
                    active_tablet = True
                    tablet_service.showWebview("https://www.university.edu.au/", verify=False)

            if active_tablet == False:
                if command == "open google":
                    print("Opening Google")
                    active_tablet = True
                    tablet_service.showWebview("https://www.google.com/", verify=False)

            if active_tablet == False:
                if command == "open manual":
                    print("Opening Manual")
                    active_tablet = True
                    tablet_service.showWebview("http://192.168.1.122:5002/manual.html", verify=False)
                    #tablet_service.showWebview("http://10.35.247.50:5002/manual.html", verify=False)

            if active_tablet == False:
                if command == "play tic tac toe":
                    print("Playing Tic Tac Toe")
                    active_tablet = True
                    #tablet_service.showWebview("https://playtictactoe.org/", verify=False)
                    tablet_service.showWebview("http://192.168.1.122:5002/pepper_tictactoe.html", verify=False)
                    #tablet_service.showWebview("http://127.0.0.1:5002/pepper_tictactoe.html", verify=False)
                    #tablet_service.showWebview("http://10.35.247.50:5002/pepper_tictactoe.html", verify=False)
                    #tablet_service.executeJS("ALMemory.raiseEvent('tictactoe/robotMove', 4);")
                    

            if command == "close tablet" or command == "close website":
                if active_tablet == True:
                    print("Closing tablet")
                    active_tablet = False
                    tablet_service.hideWebview()
                else:
                    tablet_service.hideWebview()

            if command == "text input":
                input = raw_input("Enter your text input for the chatbot: ").strip()
                tmp_history = conversation_history
                result_container = {}

                joint_names = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll",
                                "LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll",
                                "RWristYaw", "LWristYaw", "RHand", "LHand", "HipRoll", "HipPitch", "KneePitch", "HeadPitch", "HeadYaw"]

                # useSensors=True reads the current physical angles
                current_angles_list = motion.getAngles(joint_names, True)  # returns list of radians

                current_angles = dict(zip(joint_names, current_angles_list))

                output, gesture_code, conversation_history = voice_chatbot(conversation_history, result_container, current_angles,input)

                if output and conversation_history and tmp_history != conversation_history:
                    output_utf8 = output.encode('utf-8')
                    asr.pause(True)
                    tts.post.say(output_utf8)
                    #tts.say(output_utf8)
                    execute_generated_movement(gesture_code, motion)
                    #animated_speech.say(output_utf8, config)
                    time.sleep(3)
                    names = [
                        "RShoulderPitch","RShoulderRoll","RElbowYaw","RElbowRoll","RWristYaw",
                        "LShoulderPitch","LShoulderRoll","LElbowYaw","LElbowRoll","LWristYaw",
                        "HeadYaw","HeadPitch",
                        "RHand","LHand"
                    ]

                    angles = [
                        1.5, -0.15, 1.2, 0.3, 0.0,
                        1.5,  0.15, -1.2, -0.3, 0.0,
                        0.0, 0.0,
                        0.0, 0.0
                    ]


                    time_to_reach = 2.0
                    motion.angleInterpolation(names, angles, time_to_reach, True)
                    print("Reset!")
                    asr.pause(False)
                    recording = False

                final_response = "SPOKEN_RESPONSE:\n<"+output+">\nGESTURE_CODE:\n<"+gesture_code+">"
                conversation_history[len(conversation_history) - 1]['content'] = final_response
                # IROS
                #print(conversation_history)
                #conversation_history.pop()
                #conversation_history.pop()

            # For trigger word end
            '''if recording == True:
                if command == "go ahead":
                    recorder.stopMicrophonesRecording()
                    tts.say("Okay")
                    print("Sending Chunk...")
                    sftp = ssh.open_sftp()
                    sftp.get(recorder_filepath, local_path)
                    sftp.close()
                    tmp_history = conversation_history
                    output, conversation_history = voice_chatbot(conversation_history, result_container)

                    output_utf8 = output.encode('utf-8')
                    asr.pause(True)
                    #tts.post.say(output_utf8)
                    #tts.say(output_utf8)
                    animated_speech.say(output_utf8, config)
                    time.sleep(1)
                    asr.pause(False)
                    recording = False'''

            if recording == False:
                if command == "hey pepper" or command == "hi pepper":
                    tts.stopAll()
                    print("Recording")
                    tts.say("Go ahead")
                    print("Listening...")
                    recording = True
                    result_container = {}
                    # For trigger word end
                    #recorder.startMicrophonesRecording(recorder_filepath, "wav", 16000, [1,0,0,0])

                    # For silence detection
                    while recording == True:
                        recorder.startMicrophonesRecording(recorder_filepath, "wav", 16000, [1,0,0,0])

                        time.sleep(2)

                        recorder.stopMicrophonesRecording()
                        print("Sending Chunk...")
                        sftp = ssh.open_sftp()
                        sftp.get(recorder_filepath, local_path)
                        sftp.close()
                        tmp_history = conversation_history

                        joint_names = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll",
                                        "LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll",
                                        "RWristYaw", "LWristYaw", "RHand", "LHand", "HipRoll", "HipPitch", "KneePitch", "HeadPitch", "HeadYaw"]

                        # useSensors=True reads the current physical angles
                        current_angles_list = motion.getAngles(joint_names, True)  # returns list of radians

                        current_angles = dict(zip(joint_names, current_angles_list))

                        output, gesture_code, conversation_history = voice_chatbot(conversation_history, result_container, current_angles,"")
                        print("Chunk sent!")

                        if output and conversation_history and tmp_history != conversation_history:
                            output_utf8 = output.encode('utf-8')
                            asr.pause(True)
                            tts.post.say(output_utf8)
                            #tts.say(output_utf8)
                            execute_generated_movement(gesture_code, motion)
                            #animated_speech.say(output_utf8, config)
                            time.sleep(3)
                            names = ["RShoulderPitch","RShoulderRoll","RElbowYaw","RElbowRoll","RWristYaw",
                                    "LShoulderPitch","LShoulderRoll","LElbowYaw","LElbowRoll","LWristYaw"]
                            angles = [1.5, -0.15, 1.2, 0.3, 0.0,
                                    1.5,  0.15, -1.2, -0.3, 0.0]
                            time_to_reach = 2.0
                            motion.angleInterpolation(names, angles, time_to_reach, True)
                            print("Reset!")
                            asr.pause(False)
                            recording = False

                        final_response = "SPOKEN_RESPONSE:\n<"+output+">\nGESTURE_CODE:\n<"+gesture_code+">"
                        conversation_history[len(conversation_history) - 1]['content'] = final_response
                        print(conversation_history)

            if command == "hello there":
                tts.post.say("Hello there")
                speed = 0.3
                delay = 1.0
                right_shoulder_rotate_up(motion, speed, delay, 1.3)
                right_shoulder_rotate_front(motion, speed, delay, 2.0)
                right_elbow_extend(motion, speed, delay, 0.5)
                right_wrist_rotate_out(motion, speed, delay, 1.5)
                right_hand_open(motion, speed, delay, 1.0)
                head_rotate_up(motion, speed, delay, 0.5)

            memory.removeData("WordRecognized")
            memory.insertData("WordRecognized", ["", 0.0])


            time.sleep(0.2)
