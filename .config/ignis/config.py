from ignis.app import IgnisApp
from ignis.utils import Utils
from modules import StatusBar, NotificationPopupList 
from wallpaper import get_current_wallpaper, set_wallpaper

app = IgnisApp.get_default()
app.apply_css(Utils.get_current_dir() + "/style.scss")

for n in range(Utils.get_n_monitors()):
    StatusBar(n)

NotificationPopupList(0)

set_wallpaper(get_current_wallpaper())
