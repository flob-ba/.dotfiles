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

if now() < blue_hour(city.observer)[0]:
    current_wallpaper = IMG_NIGHT
elif now() < golden_hour(city.observer)[1]:
    current_wallpaper = IMG_MORNING
elif now() < golden_hour(city.observer, direction=SunDirection.SETTING)[0]:
    current_wallpaper = IMG_NOON
elif now() < blue_hour(city.observer, direction=SunDirection.SETTING)[1]:
    current_wallpaper = IMG_EVENING
else:
    current_wallpaper = IMG_NIGHT

subprocess.run(f"{WALLPAPER_CMD} {current_wallpaper}", shell=True)
print(f"Set wallpaper to {current_wallpaper}")

while True:
    next_wallpaper = None
    if now() < blue_hour(city.observer)[0]:
        next_wallpaper = IMG_NIGHT
    elif now() < golden_hour(city.observer)[1]:
        next_wallpaper = IMG_MORNING
    elif now() < golden_hour(city.observer, direction=SunDirection.SETTING)[0]:
        next_wallpaper = IMG_NOON
    elif now() < blue_hour(city.observer, direction=SunDirection.SETTING)[1]:
        next_wallpaper = IMG_EVENING
    else:
        next_wallpaper = IMG_NIGHT
   
    if next_wallpaper != current_wallpaper:
        current_wallpaper = next_wallpaper
        subprocess.run(f"{WALLPAPER_CMD} {current_wallpaper}", shell=True)
        print(f"Set wallpaper to {curent_wallpaper}")

    time.sleep(1)
