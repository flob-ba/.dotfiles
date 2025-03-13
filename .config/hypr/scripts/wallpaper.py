#!/bin/python3

from astral.sun import golden_hour, blue_hour
from astral import LocationInfo, SunDirection
from astral import now
import time
import subprocess

IMG_NIGHT = "~/.wallpaper/outset_night.jpg"
IMG_MORNING = "~/.wallpaper/outset_morning.jpg"
IMG_NOON = "~/.wallpaper/outset_day.jpg"
IMG_EVENING = "~/.wallpaper/outset_evening.jpg"

WALLPAPER_CMD = "swww img --transition-type wave --transition-duration 2 --transition-fps 60"

latidute = 51.050407
longitude = 13.737262
city = LocationInfo("Dresden", "Germany", "Europe/Berlin", latidute, longitude)

current_wallpaper = None

if now(city.tzinfo) < blue_hour(city.observer, tzinfo=city.tzinfo)[0]:
    current_wallpaper = IMG_NIGHT
elif now(city.tzinfo) < golden_hour(city.observer, tzinfo=city.tzinfo)[1]:
    current_wallpaper = IMG_MORNING
elif now(city.tzinfo) < golden_hour(city.observer, direction=SunDirection.SETTING, tzinfo=city.tzinfo)[0]:
    current_wallpaper = IMG_NOON
elif now(city.tzinfo) < blue_hour(city.observer, direction=SunDirection.SETTING, tzinfo=city.tzinfo)[1]:
    current_wallpaper = IMG_EVENING
else:
    current_wallpaper = IMG_NIGHT

subprocess.run(f"{WALLPAPER_CMD} {current_wallpaper}", shell=True)

while True:
    next_wallpaper = None
    if now(city.tzinfo) < blue_hour(city.observer, tzinfo=city.tzinfo)[0]:
        next_wallpaper = IMG_NIGHT
    elif now(city.tzinfo) < golden_hour(city.observer, tzinfo=city.tzinfo)[1]:
        next_wallpaper = IMG_MORNING
    elif now(city.tzinfo) < golden_hour(city.observer, direction=SunDirection.SETTING, tzinfo=city.tzinfo)[0]:
        next_wallpaper = IMG_NOON
    elif now(city.tzinfo) < blue_hour(city.observer, direction=SunDirection.SETTING, tzinfo=city.tzinfo)[1]:
        next_wallpaper = IMG_EVENING
    else:
        next_wallpaper = IMG_NIGHT 

    if next_wallpaper != current_wallpaper:
        current_wallpaper = next_wallpaper
        subprocess.run(f"{WALLPAPER_CMD} {current_wallpaper}", shell=True)

    time.sleep(1)
