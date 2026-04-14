# Docker Audio Fix - Quick Reference (Assignment 1 Docker)

## 🎯 The Fix (2 Lines!)

Edit your `docker-compose.yml`:

### Before:
```yaml
services:
  remote_pc_humble:
    privileged: true
    ipc: host
    deploy:
      resources:
        ...
```

### After:
```yaml
services:
  remote_pc_humble:
    privileged: true
    ipc: host
    devices:              # ← ADD THIS LINE
      - /dev/snd:/dev/snd # ← ADD THIS LINE
    deploy:
      resources:
        ...
```

---

## 🚀 Quick Steps

```bash
# 1. Stop container
cd ~/your_assignment1_folder/
docker-compose down

# 2. Edit docker-compose.yml
nano docker-compose.yml
# Add the 2 lines shown above

# 3. Restart
docker-compose up -d

# 4. Test
docker exec -it remote_pc_humble bash
arecord -d 3 test.wav
aplay test.wav
```

---

## ✅ Verify Success

```bash
# Inside container:
ls /dev/snd/           # Should show audio devices
arecord -l             # Should list microphones
arecord -d 3 test.wav  # Should record
aplay test.wav         # Should play back
```

---

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Container won't start | Check `ls /dev/snd/` on host |
| Permission denied | Already has `privileged: true`, should work |
| Still no audio | Stop ALL containers, restart yours |
| Multiple users issue | `docker stop $(docker ps -q)` |

---

## 📍 Exact Location in File

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
    
    # ====== INSERT HERE ======
    devices:
      - /dev/snd:/dev/snd
    # =========================
    
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

---

## 🎯 Why This Works

Your original setup has PulseAudio (for speakers) but not ALSA devices (for microphone).

Adding `/dev/snd:/dev/snd` gives direct access to microphone hardware.

---

## ⚡ One-Command Alternative

Can't edit file? Use this instead:

```bash
docker-compose down

docker run -it --name remote_pc_humble --privileged --net=host --device=/dev/snd --gpus all -e ROS_DOMAIN_ID=30 -e TURTLEBOT3_MODEL=waffle_pi -v ~/my_code:/root/my_code ai_humble /bin/bash
```

---

## 📞 Still Not Working?

Collect this info for TA:

```bash
# Host
ls /dev/snd/
docker-compose --version

# Container
docker exec -it remote_pc_humble bash -c "ls /dev/snd/ && arecord -l"
```

---

**Fix = 2 lines in docker-compose.yml** ✨
