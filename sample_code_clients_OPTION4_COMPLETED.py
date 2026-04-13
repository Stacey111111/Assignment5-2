#!/usr/bin/env python3
# Sample Code for Robotics_Assignment_5
# Copyright: 2026 CS 4379K / CS 5342 Introduction to Autonomous Robotics, Robotics and Autonomous Systems

# Natural Language Processing ROS2 Integration Code for Assignment 5.

# This code will give you an introduction to integrate natural language pipeline to ROS2. This code will run as-is.

# Refer to the Lab PowerPoint materials and Appendix of Assignment 3 to learn more about coding on ROS2 and the hardware architecture of Turtlebot3.
# You can run this code either on the Jetson Xavier NX and Remote-PC docker image on the same network.
# You would need a basic understanding of Python Data Structure and Object Oriented Programming to understand this code.

import sys
import threading
import time
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Int32

# Sample code for testing sample_code_servers for Assignment 5 on CLI interface.
# This code sends request for Natural Language Processing to Server running on Remote-PC.

class NLPClient(Node):
    def __init__(self):
        super().__init__('nlp_topic_client')
        
        # Publishers (Sending Requests)
        self.tts_pub = self.create_publisher(String, '/tts_request', 10)
        self.stt_pub = self.create_publisher(Int32, '/stt_request', 10)
        self.llm_pub = self.create_publisher(String, '/llm_request', 10)

        # Subscribers (Receiving Responses)
        self.stt_sub = self.create_subscription(String, '/stt_result', self.stt_callback, 10)
        self.llm_sub = self.create_subscription(String, '/llm_response_stream', self.llm_callback, 10)

        # Events to block the CLI menu while waiting for the server
        self.stt_done = threading.Event()
        self.llm_done = threading.Event()
        
        # Storage for responses (needed for Option 4)
        self.stt_result = ""
        self.llm_response = ""

    # Callbacks (Handling Server Responses)
    def stt_callback(self, msg):
        print(f"\nSpeech To Text Result : {msg.data}")
        self.stt_result = msg.data  # Store the result
        self.stt_done.set() # Unblock the menu

    def llm_callback(self, msg):
        if msg.data == "[DONE]":
            print("\n")
            self.llm_done.set() # Unblock the menu
        else:
            # Stream tokens directly to terminal without newlines
            sys.stdout.write(msg.data)
            sys.stdout.flush()
            self.llm_response += msg.data  # Accumulate the response


    # Text Interactive Menu

    def show_menu(self):
        while rclpy.ok():
            print("\n" + "="*40)
            print("Natural Language Processing Client Test Menu")
            print("1. Test Text-to-Speech (eSpeak)")
            print("2. Test Speech-to-Text (Whisper)")
            print("3. Test LLM Generation (Llama-2)")
            print("4. Test Full Integration Pipeline for 1. to 3.")
            print("5. Exit")
            print("="*40)
            
            choice = input("Select an option (1-5): ")
            
            if choice == '1':
                text = input("Enter text to speak: ")
                msg = String()
                msg.data = text
                self.tts_pub.publish(msg)
                print("Text to Speech request sent to Remote-PC. Listen for the audio.")
                
            elif choice == '2':
                try:
                    dur = int(input("Enter recording duration (seconds): "))
                    msg = Int32()
                    msg.data = dur
                    self.stt_done.clear()
                    self.stt_pub.publish(msg)
                    print(f"Server on Remote-PC is recording for {dur} seconds. Speak now.")
                    self.stt_done.wait() # Pause menu until server responds
                except ValueError:
                    print("Please enter a valid number.")
                    
            elif choice == '3':
                prompt = input("Enter your prompt for the Large Language Model: ")
                msg = String()
                msg.data = prompt
                self.llm_done.clear()
                self.llm_response = ""  # Clear previous response
                self.llm_pub.publish(msg)
                
                print("Large Language Model: ", end="", flush=True)
                self.llm_done.wait() # Pause menu until server sends [DONE]
                
            elif choice == '4':
                ##############################################################################
                # Option 4: Full Voice Assistant Pipeline
                # Integrates Speech-to-Text, Language Model, and Text-to-Speech
                ##############################################################################
                self.option_4_voice_assistant()
                
            elif choice == '5':
                print("Exiting...")
                return
            else:
                print("Invalid choice.")

    def option_4_voice_assistant(self):
        """
        Full Voice Assistant Pipeline - Assignment 5 Requirement
        
        This function integrates the three NLP services:
        1. Speech-to-Text (Whisper) - Records and transcribes user's voice
        2. Language Model (LLaMA) - Generates AI response to the transcription
        3. Text-to-Speech (eSpeak) - Speaks the AI response back to user
        
        Flow:
        User speaks -> Whisper transcribes -> LLaMA generates response -> eSpeak reads it
        """
        print("\n" + "="*60)
        print("OPTION 4: Full Voice Assistant Pipeline")
        print("="*60)
        print("This will:")
        print("  1. Record your voice (Speech-to-Text)")
        print("  2. Generate AI response (Language Model)")
        print("  3. Speak response back (Text-to-Speech)")
        print("="*60)
        
        # ====================================================================
        # STEP 1: Get Recording Duration
        # ====================================================================
        try:
            dur_input = input("\nEnter recording duration in seconds [default: 5]: ")
            duration = int(dur_input) if dur_input.strip() else 5
        except ValueError:
            print("Invalid input. Using default duration of 5 seconds.")
            duration = 5
        
        # ====================================================================
        # STEP 2: Record and Transcribe (Speech-to-Text)
        # ====================================================================
        print(f"\n[STEP 1/3] Recording and Transcribing Speech")
        print("-"*60)
        print(f"Server will record for {duration} seconds.")
        print("Speak your question clearly NOW!")
        print("-"*60)
        
        # Send recording request
        msg = Int32()
        msg.data = duration
        self.stt_done.clear()
        self.stt_result = ""  # Clear previous result
        self.stt_pub.publish(msg)
        
        # Wait for transcription to complete
        self.stt_done.wait()
        
        # Check if transcription was successful
        if not self.stt_result or len(self.stt_result.strip()) == 0:
            print("\n✗ ERROR: Transcription failed or returned empty result.")
            print("Please try again with clearer speech in a quieter environment.")
            return
        
        print(f"\n✓ Transcription successful!")
        print(f"   You said: \"{self.stt_result}\"")
        print("-"*60)
        
        # ====================================================================
        # STEP 3: Generate AI Response (Language Model)
        # ====================================================================
        print(f"\n[STEP 2/3] Generating AI Response")
        print("-"*60)
        print("Sending your question to Large Language Model...")
        print("(This may take 10-30 seconds depending on GPU and model)")
        print("\nAI Response: ", end="", flush=True)
        
        # Send LLM request with the transcribed text
        msg = String()
        msg.data = self.stt_result
        self.llm_done.clear()
        self.llm_response = ""  # Clear previous response
        self.llm_pub.publish(msg)
        
        # Wait for LLM to finish generating (streaming tokens will appear)
        self.llm_done.wait()
        
        # Check if LLM response was generated
        if not self.llm_response or len(self.llm_response.strip()) == 0:
            print("\n✗ ERROR: Language Model failed to generate response.")
            return
        
        print()  # New line after streamed response
        print("-"*60)
        print(f"✓ Response generated ({len(self.llm_response)} characters)")
        print("-"*60)
        
        # ====================================================================
        # STEP 4: Speak the Response (Text-to-Speech)
        # ====================================================================
        print(f"\n[STEP 3/3] Speaking AI Response")
        print("-"*60)
        print("Sending response to eSpeak service...")
        print("Listen for the audio output!")
        print("-"*60)
        
        # Send TTS request with the LLM response
        msg = String()
        msg.data = self.llm_response.strip()
        self.tts_pub.publish(msg)
        
        # Give eSpeak a moment to start speaking
        time.sleep(1)
        
        print("✓ eSpeak is now reading the response")
        
        # ====================================================================
        # STEP 5: Display Summary
        # ====================================================================
        print("\n" + "="*60)
        print("VOICE ASSISTANT SESSION COMPLETE")
        print("="*60)
        print(f"\nYour Question:")
        print(f"  \"{self.stt_result}\"")
        print(f"\nAI Response:")
        print(f"  {self.llm_response.strip()}")
        print("\n" + "="*60)
        print("✓ Full pipeline completed successfully!")
        print("  - Speech recorded and transcribed")
        print("  - AI response generated")
        print("  - Response spoken by eSpeak")
        print("="*60)

def main(args=None):
    rclpy.init(args=args)
    client = NLPClient()
    
    # Spin ROS 2 callbacks in a background thread so input() doesn't block them
    spin_thread = threading.Thread(target=rclpy.spin, args=(client,), daemon=True)
    spin_thread.start()
    
    try:
        # Run the interactive menu in the main thread
        client.show_menu()
    except KeyboardInterrupt:
        pass
    finally:
        client.destroy_node()
        rclpy.shutdown()
        spin_thread.join()

if __name__ == '__main__':
    main()
