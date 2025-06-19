#!/bin/python3

from astral.sun import golden_hour, blue_hour
from astral import LocationInfo, SunDirection
from astral import now
import time
import subprocess

IMG_NIGHT = "~/.wallpaper/gruvbox_outset_night.jpg"
IMG_MORNING = "~/.wallpaper/gruvbox_outset_morning.jpg"
IMG_NOON = "~/.wallpaper/gruvbox_outset_day.jpg"
IMG_EVENING = "~/.wallpaper/gruvbox_outset_evening.jpg"

WALLPAPER_CMD = "swww img --transition-type wave --transition-duration 2 --transition-fps 60"

LATITUDE = 51.050407
LONGITUDE = 13.737262
CITY = LocationInfo("Dresden", "Germany", "Europe/Berlin", LATITUDE, LONGITUDE)

def get_current_wallpaper():
    if now(CITY.tzinfo) < blue_hour(CITY.observer, tzinfo=CITY.tzinfo)[0]:
        return IMG_NIGHT
    elif now(CITY.tzinfo) < golden_hour(CITY.observer, tzinfo=CITY.tzinfo)[1]:
        return IMG_MORNING
    elif now(CITY.tzinfo) < golden_hour(CITY.observer, direction=SunDirection.SETTING, tzinfo=CITY.tzinfo)[0]:
        return IMG_NOON
    elif now(CITY.tzinfo) < blue_hour(CITY.observer, direction=SunDirection.SETTING, tzinfo=CITY.tzinfo)[1]:
        return IMG_EVENING
    else:
        return IMG_NIGHT

def set_wallpaper(wallpaper: str):
    subprocess.run(f"{WALLPAPER_CMD} {wallpaper}", shell=True)

if __name__ == "__main__":
    current_wallpaper = get_current_wallpaper()
    while True:
        next_wallpaper = get_current_wallpaper() 
        if next_wallpaper != current_wallpaper:
            current_wallpaper = next_wallpaper
            set_wallpaper(current_wallpaper)
        time.sleep(1)
