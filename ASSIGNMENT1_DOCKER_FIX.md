# Assignment 5 Audio Fix - For Assignment 1 Docker Setup

## 📋 Problem Analysis

Your Assignment 1 Docker setup uses:
- ✅ PulseAudio socket mounting (good for desktop audio)
- ✅ Audio tools installed in Dockerfile (alsa-utils, espeak-ng)
- ❌ **Missing `/dev/snd` device mapping** (needed for microphone)

**Error you're seeing:**
```
arecord: main:831: audio open error: No such file or directory
```

**Root cause:** 
While PulseAudio is configured, the container cannot access the raw ALSA audio devices (`/dev/snd`) needed for microphone recording with `arecord`.

---

## ⚡ Solution: Modify docker-compose.yml

### Option 1: Quick Fix (Edit Existing File)

**Edit your `docker-compose.yml` file and add this section:**

```yaml
services:
  remote_pc_humble:
    # ... existing configuration ...
    
    # ADD THIS SECTION (after "ipc: host")
    devices:
      - /dev/snd:/dev/snd
    
    # ... rest of configuration ...
```

**Complete modified section:**

```yaml
services:
  remote_pc_humble:
    build: 
      context: ./
    image: ai_humble
    container_name: remote_pc_humble
    network_mode: host
    privileged: true
    ipc: host
    
    # ============ ADD THIS ============
    devices:
      - /dev/snd:/dev/snd
    # ==================================
    
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    
    # ... rest remains the same ...
```

### Option 2: Use Modified File (Recommended)

I've created a corrected `docker-compose.yml` for you with the fix already applied.

**Steps:**
```bash
# 1. Backup your original
cd ~/assignment1_docker_folder/  # Your Assignment 1 folder
cp docker-compose.yml docker-compose.yml.backup

# 2. Copy the fixed version
# (Use the docker-compose.yml file I created)

# 3. Rebuild and restart
docker-compose down
docker-compose up -d

# 4. Enter container
docker exec -it remote_pc_humble bash
```

---

## 🚀 Step-by-Step Fix Procedure

### Step 1: Stop Running Container

```bash
# In your Assignment 1 Docker folder
cd ~/path/to/assignment1_docker/

# Stop the container
docker-compose down

# Or if using docker commands:
docker stop remote_pc_humble
```

### Step 2: Edit docker-compose.yml

```bash
# Open the file
nano docker-compose.yml
# or
code docker-compose.yml
# or
gedit docker-compose.yml
```

**Find this section:**
```yaml
    ipc: host
    deploy:
      resources:
```

**Add between them:**
```yaml
    ipc: host
    devices:                    # ← ADD THIS
      - /dev/snd:/dev/snd       # ← ADD THIS
    deploy:
      resources:
```

**Save and exit.**

### Step 3: Restart Container

```bash
# Rebuild and start (in case of changes)
docker-compose up -d --build

# Or just start if no rebuild needed
docker-compose up -d
```

### Step 4: Verify Fix

```bash
# Enter container
docker exec -it remote_pc_humble bash

# Inside container, check audio devices
ls -la /dev/snd/

# Expected output:
# total 0
# drwxr-xr-x  3 root root       200 Apr 13 12:34 .
# drwxr-xr-x 20 root root      4440 Apr 13 12:34 ..
# drwxr-xr-x  2 root root        60 Apr 13 12:34 by-path
# crw-rw----+ 1 root audio 116,  0 Apr 13 12:34 controlC0
# crw-rw----+ 1 root audio 116, 16 Apr 13 12:34 pcmC0D0c
# crw-rw----+ 1 root audio 116, 17 Apr 13 12:34 pcmC0D0p
# crw-rw----+ 1 root audio 116,  1 Apr 13 12:34 seq
# crw-rw----+ 1 root audio 116, 33 Apr 13 12:34 timer

# Test microphone
arecord -d 3 test.wav

# Should record without errors

# Test playback
aplay test.wav

# Should play back
```

### Step 5: Test Assignment 5

```bash
# Inside container
cd /root/my_code/Robotics_Assignment_5/
python3 test_whisper.py

# Expected output:
# Initializing Whisper
# Whisper Ready.
# Recording for 5 seconds using arecord. Speak now!
# Recording finished.
# Transcribing.
# You said: [your speech]
# Speaking: '[your speech]'
```

---

## 🔍 Why This Works

### Your Original Setup

```yaml
# PulseAudio socket (for desktop audio output)
volumes:
  - /run/user/${HOST_UID}/pulse/native:/tmp/pulse_socket
  - ${USER_HOME}/.config/pulse/cookie:/root/.config/pulse/cookie

environment:
  - PULSE_SERVER=unix:/tmp/pulse_socket
```

**What this does:**
- ✅ Allows desktop audio playback (speakers)
- ✅ Works for GUI applications
- ❌ Doesn't provide direct access to ALSA devices
- ❌ Doesn't work with `arecord` (needs raw device access)

### With Our Fix

```yaml
devices:
  - /dev/snd:/dev/snd
```

**What this adds:**
- ✅ Direct access to ALSA audio devices
- ✅ Microphone recording with `arecord` works
- ✅ Both PulseAudio AND ALSA work
- ✅ Full audio functionality

---

## 🐛 Troubleshooting

### Issue 1: Container won't start after modification

**Error:**
```
Error response from daemon: error gathering device information while adding custom device "/dev/snd": no such file or directory
```

**Cause:** Host machine doesn't have `/dev/snd/`

**Solution:**
```bash
# On host, check audio devices
ls -la /dev/snd/

# If empty, check audio drivers
sudo alsa force-reload

# Reboot if needed
sudo reboot
```

### Issue 2: Permission denied inside container

**Error:**
```
arecord: main:831: audio open error: Permission denied
```

**Cause:** User not in audio group

**Solution:**
```bash
# Inside container
usermod -aG audio root

# Or add to docker-compose.yml:
group_add:
  - audio
```

### Issue 3: Multiple containers issue (TA mentioned)

**Problem:** Other students' containers are running

**Solution:**
```bash
# Check all running containers
docker ps -a

# Stop all
docker stop $(docker ps -q)

# Start only yours
cd ~/your_assignment_folder/
docker-compose up -d
```

### Issue 4: Environment variables not set

**Problem:** ${HOST_UID} or ${USER_HOME} not defined

**Solution:**
```bash
# Check current values
echo $HOST_UID
echo $USER_HOME

# If empty, set them:
export HOST_UID=$(id -u)
export USER_HOME=$HOME

# Then restart:
docker-compose down
docker-compose up -d

# Or create .env file:
echo "HOST_UID=$(id -u)" > .env
echo "USER_HOME=$HOME" >> .env
```

---

## 📝 Alternative: One-Time Fix Without Editing File

If you can't or don't want to edit docker-compose.yml:

```bash
# Stop the compose container
docker-compose down

# Start manually with device
docker run -it \
  --name remote_pc_humble_audio \
  --privileged \
  --net=host \
  --ipc=host \
  --device=/dev/snd \
  --gpus all \
  -e DISPLAY=$DISPLAY \
  -e NVIDIA_VISIBLE_DEVICES=all \
  -e NVIDIA_DRIVER_CAPABILITIES=all \
  -e ROS_DOMAIN_ID=30 \
  -e TURTLEBOT3_MODEL=waffle_pi \
  -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
  -v ~/my_code:/root/my_code \
  ai_humble \
  /bin/bash

# Inside container, test
arecord -d 3 test.wav
python3 /root/my_code/Robotics_Assignment_5/test_whisper.py
```

---

## ✅ Verification Checklist

After applying the fix:

- [ ] docker-compose.yml contains `devices: - /dev/snd:/dev/snd`
- [ ] Container starts successfully: `docker-compose up -d`
- [ ] Can enter container: `docker exec -it remote_pc_humble bash`
- [ ] Audio devices visible: `ls /dev/snd/` shows files
- [ ] Can list microphones: `arecord -l` shows devices
- [ ] Can record: `arecord -d 3 test.wav` works
- [ ] Can playback: `aplay test.wav` works
- [ ] Whisper test works: `python3 test_whisper.py` succeeds

---

## 🎯 Summary

### What Changed

**Before (Original docker-compose.yml):**
```yaml
services:
  remote_pc_humble:
    privileged: true
    ipc: host
    deploy:
      resources:
        ...
```

**After (Fixed docker-compose.yml):**
```yaml
services:
  remote_pc_humble:
    privileged: true
    ipc: host
    devices:              # ← ADDED
      - /dev/snd:/dev/snd # ← ADDED
    deploy:
      resources:
        ...
```

**Just 2 lines added!**

### Impact

- ✅ Microphone recording now works
- ✅ `arecord` command works
- ✅ Assignment 5 `test_whisper.py` works
- ✅ Full NLP pipeline works
- ✅ Both ALSA and PulseAudio work
- ✅ No other functionality affected

---

## 📞 Need Help?

If issues persist, collect this debug info:

```bash
# On host machine (outside Docker)
echo "=== Host Audio ==="
arecord -l
ls -la /dev/snd/

echo "=== Docker Info ==="
docker --version
docker-compose --version

echo "=== Environment ==="
echo $HOST_UID
echo $USER_HOME

echo "=== Container Status ==="
docker ps -a

# Inside container
echo "=== Container Audio ==="
ls -la /dev/snd/
arecord -l
groups
```

Send this to your TA.

---

## 🎓 For Your Reference

**Files I created for you:**
1. `docker-compose.yml` - Modified version with audio fix
2. This guide - Step-by-step instructions

**What you need to do:**
1. Add `devices: - /dev/snd:/dev/snd` to your docker-compose.yml
2. Run `docker-compose down` then `docker-compose up -d`
3. Test with `arecord -d 3 test.wav`
4. Run Assignment 5: `python3 test_whisper.py`

---

**The fix is simple: just add 2 lines to docker-compose.yml!** 🎉
