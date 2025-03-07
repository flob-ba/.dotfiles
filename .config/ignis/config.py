from ignis.app import IgnisApp
from ignis.utils import Utils
from modules import Bar, Logout

app = IgnisApp.get_default()
app.apply_css(Utils.get_current_dir() + "/style.scss")

for monitor in range(Utils.get_n_monitors()):
    Bar(monitor)
    Logout(monitor)
