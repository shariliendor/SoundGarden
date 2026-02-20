import python_weather
import asyncio
import random

SCALE_NOTES = ["A", "A\#", "B", "C", "C\#", "D", "D\#", "E", "F", "F\#", "G", "G\#"]

 # I know mode isn't the right word but I don't know what to call it lol
SCALE_MODES = ["Major", "Minor"]

async def main() -> None:
    weather = await get_weather()

    hour: int = weather.datetime.hour
    description: str = weather.description
    temp: int = weather.temperature

    scale = get_scale(hour, description, temp)

    print(scale)


async def get_weather():
    # Declare the client. The measuring unit used defaults to the metric system (celcius, km/h, etc.)
    async with python_weather.Client(unit=python_weather.IMPERIAL) as client:

        # Fetch a weather forecast from a city.
        weather = await client.get('Bellingham')

        return weather
    

def get_scale(hour: int, description: int, temp: int) -> str:
    # scale start is determined by the hour for testing
    scale_start: str = SCALE_NOTES[hour % 12]

    # scale mode is random for testing
    scale_mode: str = random.choice(SCALE_MODES)

    scale = f'{scale_start} {scale_mode}'

    return scale


if __name__ == '__main__':
  asyncio.run(main())