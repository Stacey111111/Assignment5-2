# Assignment 5 - Quick Reference

## Files to Use

| File | Source |
|------|--------|
| `sample_code_servers.py` | Provided by instructor (use as-is) |
| `sample_code_clients_OPTION4_COMPLETED.py` | Your completed client ⭐ |

---

## Running Demo (2 Terminals)

### Terminal 1 - Server
```bash
cd ~/my_code/Robotics_Assignment_5/
python3 sample_code_servers.py
```

### Terminal 2 - Client
```bash
cd ~/my_code/Robotics_Assignment_5/
python3 sample_code_clients_OPTION4_COMPLETED.py
```

---

## Demo Steps

```
1. Select Option 4
2. Press Enter (use default 5 seconds)
3. Speak clearly: "What is machine learning?"
4. Wait 10-30 seconds for processing
5. Listen to eSpeak response
```

---

## Option 4 Flow

```
Voice Input
    ↓
Whisper STT (1-2 sec)
    ↓
LLaMA LLM (5-15 sec)
    ↓
eSpeak TTS (3-5 sec)
    ↓
Audio Output
```

---

## Test Questions

- "What is Python?"
- "Explain AI"
- "What is machine learning?"
- "How do robots work?"

---

## Key Code (What You Added)

```python
def option_4_voice_assistant(self):
    # Record & Transcribe
    self.stt_pub.publish(Int32(data=duration))
    self.stt_done.wait()
    
    # Generate Response
    self.llm_pub.publish(String(data=self.stt_result))
    self.llm_done.wait()
    
    # Speak Response
    self.tts_pub.publish(String(data=self.llm_response))
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| No audio | Check `arecord -l` |
| Slow | Normal with GPU (10-30s total) |
| Empty transcription | Speak louder/clearer |

---

## Expected Timing (GPU)

- Whisper: 1-2 seconds
- LLaMA: 5-15 seconds  
- eSpeak: 3-5 seconds
- **Total: 10-25 seconds**

---

## What to Submit

✅ `sample_code_clients_OPTION4_COMPLETED.py`

---

**Ready for demo!** 🚀
