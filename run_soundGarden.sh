
#!/bin/bash

set -e

# Project directory
cd /home/soundGarden/SoundGarden

# Activate virtual environment
source /home/soundGarden/SoundGarden/soundGardenVENV/bin/activate

# Tell Python which graphical display to use
export DISPLAY=:0

# Tell Python which PyAudio interface to use
export XDG_RUNTIME_DIR=/run/user/1000
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus
export PULSE_SERVER=unix:/run/user/1000/pulse/native

# Allow access to the desktop's X11 session
export XAUTHORITY=/home/soundGarden/.Xauthority

# Log diagnostic information
echo "Starting SoundGarden at $(date)" >> /home/soundGarden/SoundGarden/script.log
echo "DISPLAY=$DISPLAY" >> /home/soundGarden/SoundGarden/script.log

# Launch application
python -u /home/soundGarden/SoundGarden/main.py >> /home/soundGarden/SoundGarden/script.log 2>&1

