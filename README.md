# GPT-Pepper
Generating expressive robot co-speech gestures via an iterative Large Language Model-based framework (uses GPT-4.1).

## Versions
- NAOqi v2.5
- Python 3.10
- Python 2.7

## File Description
- chatbot.py (Runs the OpenAI API call on Python for LLM output while also processes speech-end detection for real-time transcription and HTTPS handling with pepper_start.py)
- pepper_start.py (Runs all the NAOqi Framework calls to communicate with Pepper robot and HTTPS handling with chatbot.py)
- function_library.py (Contains all the individual primitive joint movement functions for Pepper robot control and LLM construction)
- generative_movement.py (Contains helper functions for co-speech code generation and execution on Pepper robot)
- summarizer.py (Summarizes all the feedback comments collected in the iterative online user study)

We have also included the Co-speech_system_prompt.txt for easy inspection of system prompt used for co-speech generative movement.

## Commands to Run Code
For deployment on robot:
To be run on a Python 2.7 terminal:
'''
python ./pepper_start.py
'''
To be run on a Python 3.10 terminal:
'''
python ./chatbot.py
'''

A clean release is currently being worked on

This is the initial version to upload the main code files and prompts for inspection.

Codebase is not formatted or operational
