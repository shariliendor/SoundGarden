import python_weather
import asyncio
import random
from datetime import datetime

SCALE_NOTES = ["A", "A\#", "B", "C", "C\#", "D", "D\#", "E", "F", "F\#", "G", "G\#"]

 # I know mode isn't the right word but I don't know what to call it lol
SCALE_MODES = ["Major", "Minor"]

# the number of half steps between each note in the scale
intervals = {
    "Major": [2, 2, 1, 2, 2, 2],
    "Minor": [2, 1, 2, 2, 1, 2]
}

# Checking the weather takes a while, so only check it every once in a while
weather = None
weather_check_interval = 10 # in minutes
last_weather_check = 0

def get_note_list(start_note, mode):
    notes = [start_note]
    index = SCALE_NOTES.index(start_note)

    for interval in intervals[mode]:
        index += interval
        notes.append(SCALE_NOTES[index % len(SCALE_NOTES)])
    
    return notes

async def get_scale() -> list[str]:
    weather = await get_weather()

    hour: int = weather.datetime.hour
    description: str = weather.description
    temp: int = weather.temperature

    scale = get_mapped_scale(hour, description, temp)

    return scale


async def get_weather():
    curr_time = datetime.now()

    if last_weather_check != 0:
        if (curr_time - weather_last_checked).min < weather_check_interval:
            return weather


    # Declare the client. The measuring unit used defaults to the metric system (celcius, km/h, etc.)
    async with python_weather.Client(unit=python_weather.IMPERIAL) as client:

        weather = await client.get('Bellingham')

        # update weather_last_checked
        weather_last_checked = time.time()

        return weather
    

def get_mapped_scale(hour: int, description: int, temp: int) -> list[str]:
    # scale start is determined by the hour for testing
    scale_start: str = SCALE_NOTES[hour % 12]

    # scale mode is random for testing
    scale_mode: str = random.choice(SCALE_MODES)

    scale = get_note_list(scale_start, scale_mode)

    return scale