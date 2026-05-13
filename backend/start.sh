#!/bin/bash
# Start Xvfb (virtual display)
rm /tmp/.X99-lock

Xvfb :99 -screen 0 1280x720x24 &
sleep 1

# Start window manager
fluxbox &
sleep 1

# Start x11vnc (VNC server)
x11vnc -display :99 -bg -nopw -listen 0.0.0.0 -xkb -rfbport 5900 -forever -threads -o /tmp/x11vnc.log &
sleep 1

# Start noVNC (web client on port 6080)
/opt/noVNC/utils/novnc_proxy --vnc 127.0.0.1:5900 --listen 6080 &
sleep 1

# Start the backend app with debugpy and uvicorn
exec python -m debugpy --listen 0.0.0.0:5678 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
