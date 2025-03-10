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

while True:
    if now() < blue_hour(city.observer)[0]:
        subprocess.run(f"{WALLPAPER_CMD} {IMG_NIGHT}", shell=True)
        print("NIGHT 1")
    elif now() < golden_hour(city.observer)[1]:
        subprocess.run(f"{WALLPAPER_CMD} {IMG_MORNING}", shell=True)
        print("MORNING")
    elif now() < golden_hour(city.observer, direction=SunDirection.SETTING)[0]:
        subprocess.run(f"{WALLPAPER_CMD} {IMG_NOON}", shell=True)
        print("NOON")
    elif now() < blue_hour(city.observer, direction=SunDirection.SETTING)[1]:
        subprocess.run(f"{WALLPAPER_CMD} {IMG_EVENING}", shell=True)
        print("EVENING")
    else:
        subprocess.run(f"{WALLPAPER_CMD} {IMG_NIGHT}", shell=True)
        print("NIGHT 2")
    
    time.sleep(60)

