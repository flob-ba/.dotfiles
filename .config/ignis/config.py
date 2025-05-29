from ignis.app import IgnisApp
from ignis.utils import Utils
from modules import StatusBarLeft, StatusBarRight, NotificationPopupList, ControlCenter

app = IgnisApp.get_default()
app.apply_css(Utils.get_current_dir() + "/style.scss")

ControlCenter(0)
StatusBarLeft(0)
StatusBarRight(0)
NotificationPopupList(0)

