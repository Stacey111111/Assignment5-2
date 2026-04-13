# Assignment 5 - Option 4 Implementation Guide

## Quick Start (Based on Your Lab Environment)

### Environment
- **Robot**: TurtleBot3 Waffle Pi
- **OS**: Ubuntu 22.04 with ROS2 Humble
- **Remote-PC**: Docker environment on Ubuntu 24.04 with NVIDIA GPU
- **Server**: Uses `llama.cpp` (GGUF) + `faster-whisper` + `espeak-ng`

---

## Files

| File | Description |
|------|-------------|
| `sample_code_servers.py` | Provided by instructor (DO NOT MODIFY much) |
| `sample_code_clients_OPTION4_COMPLETED.py` | **Your completed client with Option 4** |

---

## Running the Assignment

### Terminal 1: Start Server

```bash
[Remote-PC] cd ~/my_code/Robotics_Assignment_5/
[Remote-PC] python3 sample_code_servers.py
```

**Expected Output:**
```
[INFO] [nlp_topic_server]: Loading Faster-Whisper (small) onto GPU...
[INFO] [nlp_topic_server]: Whisper Loaded.
[INFO] [nlp_topic_server]: Loading LLM from ~/my_code/Robotics_Assignment_5/Assignment_5_demo/llama-2-7b-32k-instruct.Q4_K_M.gguf...
[INFO] [nlp_topic_server]: Large Language Model Loaded.
[INFO] [nlp_topic_server]: Natural Language Processing Server is up. Listening to request topic.
```

### Terminal 2: Start Client

```bash
[Remote-PC] cd ~/my_code/Robotics_Assignment_5/
[Remote-PC] python3 sample_code_clients_OPTION4_COMPLETED.py
```

**Menu:**
```
========================================
Natural Language Processing Client Test Menu
1. Test Text-to-Speech (eSpeak)
2. Test Speech-to-Text (Whisper)
3. Test LLM Generation (Llama-2)
4. Test Full Integration Pipeline for 1. to 3.
5. Exit
========================================
Select an option (1-5):
```

---

## Testing Option 4 (Your Requirement)

### Step 1: Select Option 4

```
Select an option (1-5): 4
```

### Step 2: Set Recording Duration

```
Enter recording duration in seconds [default: 5]: 5
```

### Step 3: Speak Your Question

```
[STEP 1/3] Recording and Transcribing Speech
------------------------------------------------------------
Server will record for 5 seconds.
Speak your question clearly NOW!
------------------------------------------------------------
```

**Speak clearly**: "What is machine learning?"

### Step 4: Wait for AI Response

```
Speech To Text Result : What is machine learning?

✓ Transcription successful!
   You said: "What is machine learning?"
------------------------------------------------------------

[STEP 2/3] Generating AI Response
------------------------------------------------------------
Sending your question to Large Language Model...
(This may take 10-30 seconds depending on GPU and model)

AI Response: Machine learning is a subset of artificial intelligence...
```

### Step 5: Listen to Response

```
[STEP 3/3] Speaking AI Response
------------------------------------------------------------
Sending response to eSpeak service...
Listen for the audio output!
------------------------------------------------------------
✓ eSpeak is now reading the response

============================================================
VOICE ASSISTANT SESSION COMPLETE
============================================================

Your Question:
  "What is machine learning?"

AI Response:
  Machine learning is a subset of artificial intelligence...

============================================================
✓ Full pipeline completed successfully!
  - Speech recorded and transcribed
  - AI response generated
  - Response spoken by eSpeak
============================================================
```

---

## Expected Flow

```
User Input (Voice)
    ↓
[STT] Whisper Transcription (GPU-accelerated)
    ↓
Transcribed Text
    ↓
[LLM] LLaMA Response Generation (GPU-accelerated)
    ↓
AI Response Text
    ↓
[TTS] eSpeak Speech Synthesis
    ↓
Audio Output (Spoken Response)
```

---

## What Option 4 Does (Code Explanation)

```python
def option_4_voice_assistant(self):
    # Step 1: Get recording duration from user
    duration = 5  # default
    
    # Step 2: Send STT request
    msg = Int32()
    msg.data = duration
    self.stt_pub.publish(msg)  # Server records audio
    self.stt_done.wait()        # Wait for transcription
    
    # Step 3: Send LLM request with transcription
    msg = String()
    msg.data = self.stt_result  # Use transcribed text
    self.llm_pub.publish(msg)   # Server generates response
    self.llm_done.wait()         # Wait for generation
    
    # Step 4: Send TTS request with LLM response
    msg = String()
    msg.data = self.llm_response  # Use generated text
    self.tts_pub.publish(msg)     # Server speaks response
```

---

## Performance (With GPU)

| Component | Time (GPU) | Time (CPU) |
|-----------|-----------|-----------|
| Whisper STT | 1-2 sec | 8-10 sec |
| LLaMA Generation | 5-15 sec | 30-60 sec |
| eSpeak TTS | 3-5 sec | 3-5 sec |
| **Total** | **10-25 sec** | **40-75 sec** |

---

## Adjustable Parameters (in sample_code_servers.py)

### Whisper Model Size
```python
# Line ~30
self.whisper_model = WhisperModel("small", device="cuda", compute_type="float16")

# Options: tiny, base, small, medium, large
# small = good balance for GPU
# medium = better accuracy, slower
# tiny/base = faster, lower accuracy
```

### LLaMA Model File
```python
# Line ~17
MODEL_PATH = os.path.expanduser("~/my_code/Robotics_Assignment_5/Assignment_5_demo/llama-2-7b-32k-instruct.Q4_K_M.gguf")

# Alternative (if available):
# MODEL_PATH = os.path.expanduser("~/my_code/.../llama-2-7b-chat.Q4_K_M.gguf")
```

### LLaMA Parameters
```python
# Line ~35-40
self.llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=512,           # Context window (increase for longer prompts)
    n_threads=4,         # CPU threads
    n_gpu_layers=33,     # GPU layers (increase for better GPU usage)
    chat_format="llama-2"
)
```

### System Prompt
```python
# Line ~80
{"role": "system", "content": "You are a Robot that follows instructions."}

# Change to customize AI behavior:
# "You are a helpful assistant."
# "You are a robotics expert."
# "You are a teacher explaining concepts simply."
```

### Max Tokens (Response Length)
```python
# Line ~88
for chunk in self.llm.create_chat_completion(
    messages=messages, 
    max_tokens=128,  # Increase for longer responses (e.g., 256, 512)
    stream=True
):
```

---

## Troubleshooting

### Issue: Server doesn't start

**Check:**
```bash
# Verify model file exists
ls ~/my_code/Robotics_Assignment_5/Assignment_5_demo/llama-2-7b-32k-instruct.Q4_K_M.gguf

# Check GPU
nvidia-smi

# Check dependencies
pip3 list | grep faster-whisper
pip3 list | grep llama-cpp-python
```

### Issue: No audio recorded

**Check:**
```bash
# List recording devices
arecord -l

# Test recording manually
arecord -d 3 test.wav
aplay test.wav
```

**Fix:**
```bash
# Install audio tools if missing
sudo apt-get install alsa-utils
```

### Issue: Whisper transcription empty

**Possible causes:**
- Background noise too loud
- Speaking too quietly
- Microphone not working

**Solution:**
- Speak clearly and loudly
- Reduce background noise
- Increase recording duration to 7-10 seconds

### Issue: LLM response too slow

**Solutions:**
```python
# In sample_code_servers.py:

# 1. Reduce max_tokens
max_tokens=64  # Instead of 128

# 2. Increase GPU layers
n_gpu_layers=40  # Instead of 33

# 3. Use smaller model (if available)
# Switch to smaller GGUF file
```

### Issue: eSpeak not speaking

**Check:**
```bash
# Test eSpeak manually
espeak-ng "Hello world"

# Install if missing
sudo apt-get install espeak-ng
```

---

## Demo Tips

### For Best Results:

1. **Clear Speech**: Speak clearly and at normal volume
2. **Quiet Environment**: Minimize background noise
3. **Good Questions**: Use simple, direct questions
   - ✅ "What is artificial intelligence?"
   - ✅ "Explain machine learning"
   - ✅ "How do robots work?"
   - ❌ Long, complex, multi-part questions

4. **Be Patient**: GPU processing takes 10-30 seconds total

### Example Demo Questions:

```
Option 4 Questions:
- "What is Python programming?"
- "Explain deep learning"
- "What are neural networks?"
- "How do self-driving cars work?"
- "What is reinforcement learning?"
```

---

## File Comparison

### Original vs Completed

**Original `sample_code_clients.py`:**
```python
elif choice == '4':
    print("Not Implemented. Please Implement as a requirement for Assignment 5.")
```

**Completed `sample_code_clients_OPTION4_COMPLETED.py`:**
```python
elif choice == '4':
    self.option_4_voice_assistant()

def option_4_voice_assistant(self):
    # Full implementation:
    # 1. Record and transcribe (STT)
    # 2. Generate response (LLM)
    # 3. Speak response (TTS)
```

---

## Assignment Completion Checklist

- [ ] Server starts without errors
- [ ] Client connects successfully
- [ ] Option 1 (TTS) works - eSpeak speaks text
- [ ] Option 2 (STT) works - Whisper transcribes speech
- [ ] Option 3 (LLM) works - LLaMA generates responses
- [ ] **Option 4 works - Full pipeline completes**
- [ ] Total time < 30 seconds (with GPU)
- [ ] Audio output is clear
- [ ] System prompt customized (optional)

---

## Summary

**What You Submit:**
- `sample_code_clients_OPTION4_COMPLETED.py` - Your completed client

**What It Does:**
1. Records your voice for N seconds
2. Transcribes speech using Whisper (GPU)
3. Generates AI response using LLaMA (GPU)
4. Speaks response using eSpeak

**Expected Performance:**
- Total pipeline: 10-30 seconds (with GPU)
- Accurate transcription
- Relevant AI responses
- Clear audio output

---

**Your Option 4 implementation is complete and ready for demo!** 🎉
