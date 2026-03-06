from function_library import *
import openai
from openai import OpenAI
import inspect
import sys
import time
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

def get_available_functions():
    """Get all movement functions from function_library"""
    functions = []
    for name, obj in inspect.getmembers(sys.modules['function_library']):
        if inspect.isfunction(obj) and any(x in name for x in ['shoulder', 'elbow', 'wrist', 'hand', 'head', 'hip', 'knee', 'wheel']):
            functions.append({
                'name': name,
                'params': inspect.signature(obj).parameters,
                'doc': obj.__doc__ or "No documentation available"

            })
    return functions

class OpenAIHandler(BaseHTTPRequestHandler):
    available_functions = get_available_functions()

    def do_POST(self):
        # Get content length
        content_length = int(self.headers.get('Content-Length', 0))
        # Read request body
        body = self.rfile.read(content_length)
        data = json.loads(body.decode("utf-8"))
        print("Received from client:", data['messages'][len(data['messages']) - 1]['content'])
        response = {"response": generative_groundzero((data['messages']), self.available_functions)}
        code_data = response['response']

        response_bytes = json.dumps(code_data).encode("utf-8")

        # Send headers
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.end_headers()

        # Send body
        self.wfile.write(response_bytes)

def host_server():
    server_address = ("0.0.0.0", 5003)
    httpd = HTTPServer(server_address, OpenAIHandler)
    print("Server running on port 5003...")
    httpd.serve_forever()

    return

def generative_codesign(prompt, model="gpt-4o"):
    client = OpenAI()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def generative_groundzero(description, model="gpt-4o"):
    client = OpenAI()
     # Create function documentation for GPT
    available_functions = get_available_functions()
    functions_doc = "\n".join([
        f"Function: {f['name']}\nParameters: {f['params']}\nDescription: {f['doc']}"
        for f in available_functions
    ])
    
    prompt = f"""
    Given these available Pepper robot functions and their descriptions:
    {functions_doc}
    
    Generate a valid sequence of expressive robotic movements to create a gesture that accommodates this speech phrase for the Pepper robot developed by Softbank Robotics: "{description}"
    Use only the available functions listed above.
    Return only valid Python code without explanations or any comments.
    Include proper timing and sequencing using time.sleep() sparingly for fluent speech, along with separating the relevant movements with the words.
    When writing the relevant words, use the function tts.post.say("word") to have Pepper say the words while performing the movements.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a robotics programming assistant. Generate valid Python code for Pepper robot movements."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content

def execute_generated_movement(code, motion, speed=0.2, delay=1.0):
    """Execute the generated movement code safely"""
    try:
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
            'time': time,
            'speed': speed,
            'delay': delay
        }
        
        # Execute the code
        exec(full_code, namespace)
        
        # Execute the main function if it exists
        if 'execute_movement' in namespace:
            namespace['execute_movement'](motion, speed, delay)
            
        return True
    except Exception as e:
        print(f"Error executing movement: {e}")
        return False

def interactive_movement_generator():
    """Interactive CLI for generating and executing movements"""
    client = OpenAI()
        
    available_functions = get_available_functions()
    
    while True:
        # Get user input from http
        description = input("\nWhat is the phrase you want Pepper to pair its gestures with (or 'exit' to quit): ")
        if description.lower() == 'exit':
            break
            
        print("\nGenerating movement sequence...")
        generated_code = generative_groundzero(description, available_functions)
        
        print("\nGenerated code:")
        print(generated_code)
        
        # Upload code to http
            
if __name__ == "__main__":
    interactive_movement_generator()
    #host_server()
    #print(get_available_functions())
    #print(generative_groundzero("Hello there, my name is Pepper"))