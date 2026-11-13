
#!/bin/bash

set -e

# Project directory
cd /home/soundGarden/SoundGarden

# Activate virtual environment
source /home/soundGarden/SoundGarden/soundGardenVENV/bin/activate

# Tell Python which graphical display to use
export DISPLAY=:0

# Allow access to the desktop's X11 session
export XAUTHORITY=/home/soundGarden/.Xauthority

# Log diagnostic information
echo "Starting SoundGarden at $(date)" >> /home/soundGarden/SoundGarden/script.log
echo "DISPLAY=$DISPLAY" >> /home/soundGarden/SoundGarden/script.log

# Launch application
python -u /home/soundGarden/SoundGarden/main.py >> /home/soundGarden/SoundGarden/script.log 2>&1

