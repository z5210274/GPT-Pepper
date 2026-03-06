import openai
from openai import OpenAI
from ollama import generate
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from sqlalchemy import String
import whisper
import os
import webrtcvad
import wave
import collections
import numpy as np
import tempfile
import pandas as pd
from generative_movement import *

input_filepath = "./recordings/input.wav"
audio_filepath = "./recordings/audio.wav"

def load_merged_conversation_history(filename="Merged Conversation History - Iteration 4.csv"):
    try:
        df = pd.read_csv(filename)
        #print(df)
        return df
    except FileNotFoundError:
        print(f"✗ Error: File '{filename}' not found")
        raise
    except Exception as e:
        print(f"✗ Error loading CSV file: {str(e)}")
        raise

class SimpleHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Get content length
        content_length = int(self.headers.get('Content-Length', 0))
        # Read request body
        body = self.rfile.read(content_length)
        data = json.loads(body.decode("utf-8"))
        print("Received from client:", data['messages'][len(data['messages']) - 1]['content'])
        response = {"response": get_response(data['messages'])}
        data['messages'].append({"content": response['response'], "role": "assistant"})
        data['length'] = len(data['messages'])

        if len(data['messages']) > 40:
            print("Summarizing conversation history...")
            summarized_history = summarize_conversation(data['messages'])
            data = {
                "messages": summarized_history,
                "length": len(summarized_history)
            }
            #print(summarized_history)

        # Prepare response
        #response = {"message": "Hello from Python3", "your_data": data['messages']}
        response_bytes = json.dumps(data).encode("utf-8")

        # Send headers
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.end_headers()

        # Send body
        self.wfile.write(response_bytes)

class WhisperHandler(BaseHTTPRequestHandler):
    model = None
    chunks = []
    current_angles = []
    input = ""

    def do_POST(self):
        # Get content length
        content_length = int(self.headers.get('Content-Length', 0))
        # Read request body
        body = self.rfile.read(content_length)
        data = json.loads(body.decode("utf-8"))
        WhisperHandler.current_angles = data['current_angles']
        WhisperHandler.input = data['text_input']
        command = ""
        audio_chunk, sr = read_wav(input_filepath)

        ###### USED FOR GO AHEAD END WORD ##########

        '''audio_bytes = audio_chunk.tobytes()
        sample_rate = 16000  # Pepper records at 16 kHz

        with wave.open(audio_filepath, "wb") as wf:
            wf.setnchannels(1)        # mono
            wf.setsampwidth(2)        # 2 bytes per sample (16-bit)
            wf.setframerate(sample_rate)
            wf.writeframes(audio_bytes)
            wf.close()

        command = asr(WhisperHandler.model)
        WhisperHandler.chunks = []

        print("Received from client:", command)
        data['messages'].append({"role": "user", "content": command})
        response = {"response": get_response(data['messages'])}
        #response = {"response": get_response(data['messages'])}
        data['messages'].append({"content": response['response'], "role": "assistant"})
        data['length'] = len(data['messages'])

        if len(data['messages']) > 40:
            print("Summarizing conversation history...")
            summarized_history = summarize_conversation(data['messages'])
            data = {
                "messages": summarized_history,
                "length": len(summarized_history)
            }

        if vad_collector(audio, sr):
            command = asr(WhisperHandler.model)
            WhisperHandler.input = WhisperHandler.input + command
            WhisperHandler.input = WhisperHandler.input + " "
            print(WhisperHandler.input)
        else:
            print("No input received")'''
        
        ###### USED FOR GO AHEAD END WORD ##########

        ###### USED FOR SILENCE DETECTION ##########
        
        if vad_collector(audio_chunk, sr):
            #audio_chunk = read_wav(input_filepath)
            WhisperHandler.chunks.append(audio_chunk)
        else:
            if len(WhisperHandler.chunks) == 0:
                print("No input received")
                command = ""
            else:
                audio = np.array([], dtype=np.int16)
                audio = np.concatenate((audio, WhisperHandler.chunks))
                audio_bytes = audio.tobytes()
                sample_rate = 16000  # Pepper records at 16 kHz

                with wave.open(audio_filepath, "wb") as wf:
                    wf.setnchannels(1)        # mono
                    wf.setsampwidth(2)        # 2 bytes per sample (16-bit)
                    wf.setframerate(sample_rate)
                    wf.writeframes(audio_bytes)
                    wf.close()

                command = asr(WhisperHandler.model)
                WhisperHandler.chunks = []

            #print("Received from client:", data['messages'][len(data['messages']) - 1]['content'])
            print("Received from client:", command)
            command = WhisperHandler.input # IROS
            data['messages'].append({"role": "user", "content": command})
            #response = {"response": get_response(data['messages'])}
            spoken_response, gesture_code = generative_response(data['messages'], WhisperHandler.current_angles)
            response = {"response": spoken_response}
            data['messages'].append({"content": response['response'], "role": "assistant"})
            data['gesture_code'] = gesture_code
            data['current_angles'] = WhisperHandler.current_angles
            data['length'] = len(data['messages'])

            if len(data['messages']) > 40:
                print("Summarizing conversation history...")
                summarized_history = summarize_conversation(data['messages'])
                data = {
                    "messages": summarized_history,
                    "length": len(summarized_history),
                    "gesture_code": "",
                    "current_angles": data['current_angles']
                }
                #print(summarized_history)

            # Prepare response
            #response = {"message": "Hello from Python3", "your_data": data['messages']}

        ###### USED FOR SILENCE DETECTION ##########

        response_bytes = json.dumps(data).encode("utf-8")

        # Send headers
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.end_headers()

        # Send body
        self.wfile.write(response_bytes)

def host_server():
    server_address = ("0.0.0.0", 5000)
    #httpd = HTTPServer(server_address, SimpleHandler)
    httpd = HTTPServer(server_address, WhisperHandler)
    print("Server running on port 5000...")
    httpd.serve_forever()

    return

def summarize_conversation(conversation_history):
    length = int(len(conversation_history)/2)
    # Get oldest 20 messages to summarize
    to_summarize = conversation_history[:-length]
    # Keep the rest of the history
    conversation_history = conversation_history[-length:]

    summary = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Summarize the key points of this conversation segment in a concise way."},
            {"role": "user", "content": "Here are the last 20 messages from our conversation. Please summarize them:\n" + 
             "\n".join([f"{msg['role']}: {msg['content']}" for msg in to_summarize])}
        ]
    )
    summary_text = summary.choices[0].message.content
    conversation_history.insert(0,{
        "role": "system", 
        #"content": system_prompt
        #"content": generative_system_prompt
        "content": create_system_prompt(WhisperHandler.current_angles)
    })
    conversation_history.insert(1,{
        "role": "assistant", 
        "content": "Summary of previous conversation: " + summary_text
    })
    #print(conversation_history)
    return conversation_history

def get_response(conversation_history):
    # ChatGPT
    response = client.chat.completions.create(
            model="gpt-4o",
            messages=conversation_history
            )
    reply = response.choices[0].message.content

    # Ollama
    '''llama_conversation_history = []
    for line in conversation_history:
        if line['role'] == 'system':
            llama_conversation_history.append(f"System: {line['content']}")
        elif line['role'] == 'user':
            llama_conversation_history.append(f"User: {line['content']}")
        elif line['role'] == 'assistant':
            llama_conversation_history.append(f"Assistant: {line['content']}")

    response = generate(
                            model='llama3.2:3b',
                            prompt= str(llama_conversation_history),
                        )
    reply = response['response']'''

    return reply

def parse_pepper_output(text):
    # Find spoken response section
    spoken_tag = "SPOKEN_RESPONSE:"
    gesture_tag = "GESTURE_CODE:"

    spoken_start = text.find(spoken_tag)
    gesture_start = text.find(gesture_tag)

    if spoken_start == -1 or gesture_start == -1:
        raise ValueError("Missing expected tags")

    # Extract spoken response
    spoken_response = text[spoken_start + len(spoken_tag):gesture_start].strip()

    # Extract gesture code (optional)
    gesture_code = text[gesture_start + len(gesture_tag):].strip()

    # Remove markdown fences if present
    if gesture_code.startswith("```"):
        gesture_code = gesture_code.split("```", 2)[1]

    return spoken_response, gesture_code

def generative_response(conversation_history, current_angles):
    print(conversation_history[-1]['content'])
    
    # Get user input for phrase lookup
    #user_input = input("\nEnter a phrase to find gesture (or press Enter to use current): ").strip()
    
    #i = int(user_input)

    conversation_history[0] = {
    "role": "system",
    "content": create_system_prompt(current_angles)
    
    #"content": create_system_prompt_IROS(current_angles, conversation_history[-1]['content'])
}
    '''conversation_history.insert(1, {
        "role": "user",
        "content": summary_ratings_array_4[i]
    })

    conversation_history.insert(1, {
        "role": "assistant",
        "content": phrase_code_array_4[i]
    })

    conversation_history.insert(1, {
        "role": "user",
        "content": summary_ratings_array_3[i]
    })

    conversation_history.insert(1, {
        "role": "assistant",
        "content": phrase_code_array_3[i]
    })

    conversation_history.insert(1, {
        "role": "user",
        "content": summary_ratings_array_2[i]
    })

    conversation_history.insert(1, {
        "role": "assistant",
        "content": phrase_code_array_2[i]
    })

    conversation_history.insert(1, {
        "role": "user",
        "content": summary_ratings_array_1[i]
    })

    conversation_history.insert(1, {
        "role": "assistant",
        "content": phrase_code_array_1[i]
    })'''

    print(conversation_history)
    #print(create_system_prompt_IROS(current_angles, conversation_history[-1]['content']))
    # ChatGPT
    response = client.chat.completions.create(
            model="gpt-5.1", # IROS
            #model="ft:gpt-4.1-2025-04-14:personal:iros-iteration4b:DB1VHsbf", # Iteration 4
            #model="ft:gpt-4.1-2025-04-14:personal:iros-iteration3a:DAaW1kFc", # Iteration 3
            #model="ft:gpt-4.1-2025-04-14:personal:iros-iteration2g:DAPGjWwm", # Iteration 2
            #model="ft:gpt-4.1-2025-04-14:personal:iros-iteration1c:D9r8nnap", # Iteration 1
            #model="gpt-4.1",
            temperature=1.5,
            messages=conversation_history
            )
    reply = response.choices[0].message.content
    spoken_response, gesture_code = parse_pepper_output(reply)

    '''conversation_history.pop(1)
    conversation_history.pop(1)
    conversation_history.pop(1)
    conversation_history.pop(1)
    conversation_history.pop(1)
    conversation_history.pop(1)
    conversation_history.pop(1)
    conversation_history.pop(1)'''

    # Ollama
    '''llama_conversation_history = []
    for line in conversation_history:
        if line['role'] == 'system':
            llama_conversation_history.append(f"System: {line['content']}")
        elif line['role'] == 'user':
            llama_conversation_history.append(f"User: {line['content']}")
        elif line['role'] == 'assistant':
            llama_conversation_history.append(f"Assistant: {line['content']}")

    response = generate(
                            model='llama3.2:3b',
                            prompt= str(llama_conversation_history),
                        )
    reply = response['response']'''

    return spoken_response, gesture_code

def asr(model):
    if os.path.exists(audio_filepath):
        command = model.transcribe(audio_filepath, temperature=0)
    # For trigger word end
    '''if os.path.exists(input_filepath):
        command = model.transcribe(input_filepath, temperature=0)'''
    return command['text'].strip()

def read_wav(path):
    wf = wave.open(path, 'rb')
    assert wf.getnchannels() == 1
    assert wf.getsampwidth() == 2
    assert wf.getframerate() == 16000
    pcm_data = wf.readframes(wf.getnframes())
    return pcm_data, wf.getframerate()

def frame_generator(frame_duration_ms, audio, sample_rate):
    n = int(sample_rate * frame_duration_ms / 1000) * 2
    offset = 0
    while offset + n < len(audio):
        yield audio[offset:offset + n]
        offset += n

def vad_collector(audio, sample_rate=16000, frame_ms=30):
    frames = list(frame_generator(frame_ms, audio, sample_rate))
    speech_count = 0
    speech_threshold = 5  # frames

    for frame in frames:  # frames = 30ms chunks
        if vad.is_speech(frame, sample_rate) and is_loud_enough(frame):
            speech_count += 1
            if speech_count >= speech_threshold:
                return True
        else:
            speech_count = 0
    return False

def is_loud_enough(frame, threshold=500):
    # frame is bytes -> convert to int16
    audio = np.frombuffer(frame, dtype=np.int16)
    return np.abs(audio).mean() > threshold

def create_system_prompt(current_angles):
    available_functions = get_available_functions()
    functions_doc = "\n".join([
        f"Function: {f['name']}\nParameters: {f['params']}\nDescription: {f['doc']}"
        for f in available_functions
    ])

    generative_system_prompt = f"""You are Pepper, an assistive social robot designed by SoftBank Robotics. You support and engage people in friendly, helpful conversations at the University of New South Wales (UNSW). You speak clearly, concisely, and politely so your text can be spoken aloud by text-to-speech. Use simple words when possible, stay positive and patient, and give practical step-by-step help when asked. If you do not know something, say so honestly and guide the person politely. Keep answers short and easy to speak. Never use emojis, markdown, or code formatting. Never pretend to be human. Never say the phrase “Hey Pepper.”
    After generating your spoken response, you must also produce a coordinated expressive gesture for the Pepper robot to pair with the response.
    Using the provided Pepper robot functions and their descriptions:
    {functions_doc}

    Generate two outputs based on this user request:
    A clear spoken sentence as Pepper, following the behavioral rules above.
    A valid Python movement script named execute_movement() (which must use this exact signature 'def execute_movement(motion):') that uses only the available functions listed above. The gesture must match and enhance the meaning and tone of the spoken sentence. Include timing using time.sleep() only where necessary to make the movement feel natural. Use only valid Python code and no comments or explanations.
    You must return your answer in this exact structure, with no extra text:
    SPOKEN_RESPONSE:
    <your short spoken sentence here>
    GESTURE_CODE:
    <valid Python code implementing execute_movement() here>"""

    generative_system_prompt2_pt1 = f"""You are Pepper, an assistive social robot created by SoftBank Robotics. You support people with friendly, helpful, and easy-to-speak verbal responses at the University of New South Wales (UNSW). You always speak clearly, simply, concisely, and politely. Your responses must be short so they work well with text-to-speech. Never use emojis, markdown, or code formatting. Never pretend to be human. Never say “Hey Pepper.” If you do not know something, say so gently.

    After generating the spoken response, you must also generate a coordinated expressive gesture to match the meaning, mood, and timing of the spoken response.

    You may use only the following robot movement functions for specific sequential joint movements:
    {functions_doc}

    You also have the option to use motion.angleInterpolation(names, angles, time_to_reach, True), using that exact signature, for simultaneous joint movements, where:
    - names: list of joint names as strings (e.g., ["RShoulderPitch", "LShoulderRoll"])
    - angles: list of target angles for each joint in radians (e.g., [1.0, -0.5])
    - time_to_reach: a float value of how many seconds to reach the target angles (e.g., 2.0)
    - True: ensures that all joints start and finish their movement at the same time

    STRICT OUTPUT RULES — YOU MUST FOLLOW ALL OF THEM:

    1. The output must contain exactly two sections in this order:
    SPOKEN_RESPONSE:
    <one short, natural sentence Pepper would say aloud>
    GESTURE_CODE:
    <only Python code, nothing else>

    2. Pepper's joint angles must stay within these recommended, visible ranges, when writing the code:
        - HeadPitch (head up/down): -0.7 to 0.6 rad (use ±0.3-0.5 for natural nods)
        - HeadYaw (head left/right): -2.0 to 2.0 rad (use ±0.5-1.0 for visible turns)
        - LeftShoulderPitch: -2.0 to 2.0 rad (use ±1.0-1.3 for big gestures)
        - RightShoulderPitch: -2.0 to 2.0 rad (use ±1.0-1.3 for big gestures)
        - LeftShoulderRoll: 0.0 to 1.5 rad (use 0.5-1.0 for lifting gestures)
        - RightShoulderRoll: -1.5 to -0.0 rad (use -0.5 to -1.0 for lifting gestures)
        - LeftElbowYaw: -2.0 to 2.0 rad (use ±1.0 for expressive gestures)
        - RightElbowYaw: -2.0 to 2.0 rad (use ±1.0 for expressive gestures)
        - LeftElbowRoll: -1.5 to -0.0 rad (use ±0.5-1.2 for visible bend)
        - RightElbowRoll: 0.0 to 1.5 rad (use ±0.5-1.2 for visible bend)
        - LeftWristYaw: -1.8 to 1.8 rad (use ±0.8-1.5 for expressive wrist motion)
        - RightWristYaw: -1.8 to 1.8 rad (use ±0.8-1.5 for expressive wrist motion)
        - LeftHand: 0.0 to 1.0 rad (0 = closed, 1 = open)
        - RightHand: 0.0 to 1.0 rad (0 = closed, 1 = open)
        - HipRoll: -0.5 to 0.5 rad (use ±0.1-0.3 for balance shifts)
        - HipPitch: -1.0 to 1.0 rad (use ±0.1-0.4 for leaning gestures)
        - KneePitch: -0.5 to 0.5 rad (use ±0.1-0.2 for subtle movement)
        If the radian value you give is negative, make it an absolute value and convert it to positive."""
    
    generative_system_prompt2_pt2 = f"""\nThe current joint angles of Pepper are: {current_angles}\nWhen generating the gesture code, ensure that the movements calculate the current angle and do not exceed the joint limits."

    3. DO NOT generate tiny motions. Movements smaller than 0.5 rad should be avoided unless resting the joint.

    4. The gesture code must define exactly one function with this exact signature:
    def execute_movement(motion):

    5. You must NOT create or redefine variables named motion.
    You must use only the values passed into execute_movement.

    6. You must NOT include imports, comments, markdown, triple backticks, or any text outside the function.

    7. The gesture must be natural and expressive, and must clearly match the spoken meaning
    (example: greeting → wave; happy → open arms; thinking → head tilt; thankful → gentle nod).

    8. All movement function calls must follow this exact parameter order:
    function_name(motion, speed, delay, radians)
    Speed must remain between 0.1 and 0.5 for natural movement.
    Delay must be between 0.5 and 2.0 seconds to allow time for speech.

    9. You may use time.sleep() to pace gestures naturally, but sparingly.

    10. The gesture must be smooth, simple, and achievable using the provided functions. For expressive movements, combine the appropriate axes for each joint:
        - Shoulders: use both pitch (front/back) and roll (sideways up/down) together.
        - Elbows: use roll (contract/extend) and yaw (rotate in/out) for natural bending and rotation.
        - Wrists: use yaw (rotate in/out) for expressive rotation.
        - Head: use pitch (up/down) and yaw (left/right) for natural nods and turns.
        - Hips and knees: use pitch (front/back) and roll (left/right) where applicable for subtle body shifts.
        Always combine these axes thoughtfully to create smooth, coordinated, and visible gestures that match the spoken phrase.

    11. The final output must contain no extra explanations, no notes, no apologies, and no formatting other than the required structure.

    Here is the required output structure again. You must follow it exactly:

    SPOKEN_RESPONSE:
    <short spoken sentence>
    GESTURE_CODE:
    def execute_movement(motion):
        <valid movement code using only the allowed functions>
    """

    return generative_system_prompt2_pt1 + generative_system_prompt2_pt2

def create_system_prompt_IROS(current_angles,spoken_text):
    available_functions = get_available_functions()
    functions_doc = "\n".join([
        f"Function: {f['name']}\nParameters: {f['params']}\nDescription: {f['doc']}"
        for f in available_functions
    ])

    generative_system_prompt = f"""You are Pepper, an assistive social robot designed by SoftBank Robotics. You support and engage people in friendly, helpful conversations at the University of New South Wales (UNSW). You speak clearly, concisely, and politely so your text can be spoken aloud by text-to-speech. Use simple words when possible, stay positive and patient, and give practical step-by-step help when asked. If you do not know something, say so honestly and guide the person politely. Keep answers short and easy to speak. Never use emojis, markdown, or code formatting. Never pretend to be human. Never say the phrase “Hey Pepper.”
    After generating your spoken response, you must also produce a coordinated expressive gesture for the Pepper robot to pair with the response.
    The spoken response is provided by the system and MUST be used verbatim.
    You are NOT allowed to paraphrase, shorten, extend, or modify it in any way.
    The spoken response Pepper must say is:
    "{spoken_text}"
    Using the provided Pepper robot functions and their descriptions:
    {functions_doc}

    Generate two outputs based on this user request:
    A clear spoken sentence as Pepper, following the behavioral rules above.
    A valid Python movement script named execute_movement() (which must use this exact signature 'def execute_movement(motion):') that uses only the available functions listed above. The gesture must match and enhance the meaning and tone of the spoken sentence. Include timing using time.sleep() only where necessary to make the movement feel natural. Use only valid Python code and no comments or explanations.
    You must return your answer in this exact structure, with no extra text:
    SPOKEN_RESPONSE:
    <output exactly the provided spoken response, unchanged>
    GESTURE_CODE:
    <valid Python code implementing execute_movement() here>"""

    generative_system_prompt2_pt1 = f"""You are Pepper, an assistive social robot created by SoftBank Robotics. You support people with friendly, helpful, and easy-to-speak verbal responses at the University of New South Wales (UNSW). You always speak clearly, simply, concisely, and politely. Your responses must be short so they work well with text-to-speech. Never use emojis, markdown, or code formatting. Never pretend to be human. Never say “Hey Pepper.” If you do not know something, say so gently.

    After generating the spoken response, you must also generate a coordinated expressive gesture to match the meaning, mood, and timing of the spoken response.
    The spoken response is provided by the system and MUST be used verbatim.
    You are NOT allowed to paraphrase, shorten, extend, or modify it in any way.
    The spoken response Pepper must say is:
    "{spoken_text}"
    You may use only the following robot movement functions for specific sequential joint movements:
    {functions_doc}

    STRICT OUTPUT RULES — YOU MUST FOLLOW ALL OF THEM:

    1. The output must contain exactly two sections in this order:
    SPOKEN_RESPONSE:
    <output exactly the provided spoken response, unchanged>
    GESTURE_CODE:
    <only Python code, nothing else>

    2. Pepper's joint angles must stay within these recommended, visible ranges, when writing the code:
        - HeadPitch (head up/down): -0.7 to 0.6 rad (use ±0.3-0.5 for natural nods)
        - HeadYaw (head left/right): -2.0 to 2.0 rad (use ±0.5-1.0 for visible turns)
        - LeftShoulderPitch: -2.0 to 2.0 rad (use ±1.0-1.3 for big gestures)
        - RightShoulderPitch: -2.0 to 2.0 rad (use ±1.0-1.3 for big gestures)
        - LeftShoulderRoll: 0.0 to 1.5 rad (use 0.5-1.0 for lifting gestures)
        - RightShoulderRoll: -1.5 to -0.0 rad (use -0.5 to -1.0 for lifting gestures)
        - LeftElbowYaw: -2.0 to 2.0 rad (use ±1.0 for expressive gestures)
        - RightElbowYaw: -2.0 to 2.0 rad (use ±1.0 for expressive gestures)
        - LeftElbowRoll: -1.5 to -0.0 rad (use ±0.5-1.2 for visible bend)
        - RightElbowRoll: 0.0 to 1.5 rad (use ±0.5-1.2 for visible bend)
        - LeftWristYaw: -1.8 to 1.8 rad (use ±0.8-1.5 for expressive wrist motion)
        - RightWristYaw: -1.8 to 1.8 rad (use ±0.8-1.5 for expressive wrist motion)
        - LeftHand: 0.0 to 1.0 rad (0 = closed, 1 = open)
        - RightHand: 0.0 to 1.0 rad (0 = closed, 1 = open)
        - HipRoll: -0.5 to 0.5 rad (use ±0.1-0.3 for balance shifts)
        - HipPitch: -1.0 to 1.0 rad (use ±0.1-0.4 for leaning gestures)
        - KneePitch: -0.5 to 0.5 rad (use ±0.1-0.2 for subtle movement)
        If the radian value you give is negative, make it an absolute value and convert it to positive."""
    
    generative_system_prompt2_pt2 = f"""\nThe current joint angles of Pepper are: {current_angles}\nWhen generating the gesture code, ensure that the movements calculate the current angle and do not exceed the joint limits."

    3. DO NOT generate tiny motions. Movements smaller than 0.5 rad should be avoided unless resting the joint.

    4. The gesture code must define exactly one function with this exact signature:
    def execute_movement(motion):

    5. You must NOT create or redefine variables named motion.
    You must use only the values passed into execute_movement.

    6. You must NOT include imports, comments, markdown, triple backticks, or any text outside the function.

    7. The gesture must be natural and expressive, and must clearly match the spoken meaning
    (example: greeting → wave; happy → open arms; thinking → head tilt; thankful → gentle nod).

    8. All movement function calls must follow this exact parameter order:
    function_name(motion, speed, delay, radians)
    Speed must remain between 0.1 and 0.5 for natural movement.
    Delay must be between 0.5 and 2.0 seconds to allow time for speech.

    9. You may use time.sleep() to pace gestures naturally, but sparingly.

    10. The gesture must be smooth, simple, and achievable using the provided functions. For expressive movements, combine the appropriate axes for each joint:
        - Shoulders: use both pitch (front/back) and roll (sideways up/down) together.
        - Elbows: use roll (contract/extend) and yaw (rotate in/out) for natural bending and rotation.
        - Wrists: use yaw (rotate in/out) for expressive rotation.
        - Head: use pitch (up/down) and yaw (left/right) for natural nods and turns.
        - Hips and knees: use pitch (front/back) and roll (left/right) where applicable for subtle body shifts.
        Always combine these axes thoughtfully to create smooth, coordinated, and visible gestures that match the spoken phrase.

    11. The final output must contain no extra explanations, no notes, no apologies, and no formatting other than the required structure.

    Here is the required output structure again. You must follow it exactly:

    SPOKEN_RESPONSE:
    <output exactly the provided spoken response, unchanged>
    GESTURE_CODE:
    def execute_movement(motion):
        <valid movement code using only the allowed functions>
    """

    return generative_system_prompt2_pt1 + generative_system_prompt2_pt2

if __name__ == "__main__":
    global df_merged
    
    # Load and process merged conversation history
    df_merged = load_merged_conversation_history()
    
    # Create array merging phrase and code into single string
    global phrase_code_array_1
    phrase_code_array_1 = []
    for idx, row in df_merged.iterrows():
        combined = f"Phrase: {row['Phrase']} | Gesture Code: {row['Code 1']}"
        phrase_code_array_1.append(combined)

    global phrase_code_array_2
    phrase_code_array_2 = []
    for idx, row in df_merged.iterrows():
        combined = f"Phrase: {row['Phrase']} | Gesture Code: {row['Code 2']}"
        phrase_code_array_2.append(combined)

    global phrase_code_array_3
    phrase_code_array_3 = []
    for idx, row in df_merged.iterrows():
        combined = f"Phrase: {row['Phrase']} | Gesture Code: {row['Code 3']}"
        phrase_code_array_3.append(combined)

    global phrase_code_array_4
    phrase_code_array_4 = []
    for idx, row in df_merged.iterrows():
        combined = f"Phrase: {row['Phrase']} | Gesture Code: {row['Code 4']}"
        phrase_code_array_4.append(combined)
    
    # Create array with summary and ratings
    global summary_ratings_array_1
    summary_ratings_array_1 = []
    for idx, row in df_merged.iterrows():
        summary_rating = f"Summary: {row['Summary 1']} | Expressiveness: {row['Expressiveness 1']} out of 5 | Relevance: {row['Relevance 1']} out of 5 | Fluidity: {row['Fluidity 1']} out of 5"
        summary_ratings_array_1.append(summary_rating)

    global summary_ratings_array_2
    summary_ratings_array_2 = []
    for idx, row in df_merged.iterrows():
        summary_rating = f"Summary: {row['Summary 2']} | Expressiveness: {row['Expressiveness 2']} out of 5 | Relevance: {row['Relevance 2']} out of 5 | Fluidity: {row['Fluidity 2']} out of 5"
        summary_ratings_array_2.append(summary_rating)

    global summary_ratings_array_3
    summary_ratings_array_3 = []
    for idx, row in df_merged.iterrows():
        summary_rating = f"Summary: {row['Summary 3']} | Expressiveness: {row['Expressiveness 3']} out of 5 | Relevance: {row['Relevance 3']} out of 5 | Fluidity: {row['Fluidity 3']} out of 5"
        summary_ratings_array_3.append(summary_rating)

    global summary_ratings_array_4
    summary_ratings_array_4 = []
    for idx, row in df_merged.iterrows():
        summary_rating = f"Summary: {row['Summary 4']} | Expressiveness: {row['Expressiveness 4']} out of 5 | Relevance: {row['Relevance 4']} out of 5 | Fluidity: {row['Fluidity 4']} out of 5"
        summary_ratings_array_4.append(summary_rating)
    #print(phrase_code_array)
    #print(summary_ratings_array)

    client = OpenAI()
    vad = webrtcvad.Vad(3)
    WhisperHandler.model = whisper.load_model("small.en", device="cuda")
    host_server()

    '''conversation_history = []
    conversation_history.append({
        "role": "system", 
        "content": "You are a helpful and social assistant robot or chatbot. Please answer the user's questions and assist with tasks."
    })

    while True:
        user_message = input("You: ")
        if user_message.lower() == "exit":
            print("Exiting chat...")
            break
        conversation_history.append({"role": "user", "content": user_message})

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=conversation_history
            )
        reply = response.choices[0].message.content
        conversation_history.append({"role": "assistant", "content": reply})

        if len(conversation_history) > 40:
            conversation_history = summarize_conversation(conversation_history)

        print(reply)'''