from ignis.app import IgnisApp
from ignis.utils import Utils
from modules import StatusBar, NotificationPopupList 

app = IgnisApp.get_default()
app.apply_css(Utils.get_current_dir() + "/style.scss")

StatusBar(0)
NotificationPopupList(0)

