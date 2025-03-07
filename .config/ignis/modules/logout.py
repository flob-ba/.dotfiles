from ignis.widgets import Widget
from ignis.utils import Utils
from ignis.app import IgnisApp

app = IgnisApp.get_default()

class LogoutButton(Widget.Button):
    def __init__(self):
        super().__init__(
            child = 
                Widget.Icon(
                    css_classes = ["logout-button"],
                    icon_name = "system-log-out-symbolic",
                    pixel_size = 100,
                ),
            on_click = lambda x: Utils.exec_sh_async("hyprctl dispatch exit 0")
        )

class LockButton(Widget.Button):
    def __init__(self, monitor):
        self.monitor = monitor
        super().__init__(
            child = 
                Widget.Icon(
                    css_classes = ["logout-button"],
                    icon_name = "system-lock-screen-symbolic",
                    pixel_size = 100,
                ),
            on_click = lambda x: self.on_click(x)
        )

    def on_click(self, x):
        app.close_window(f"logout-{self.monitor}")
        Utils.exec_sh("hyprlock")

class RebootButton(Widget.Button):
    def __init__(self):
        super().__init__(
            child = 
                Widget.Icon(
                    css_classes = ["logout-button"],
                    icon_name = "system-reboot-symbolic",
                    pixel_size = 100,
                ),
            on_click = lambda x: Utils.exec_sh_async("reboot")
        )

class PoweroffButton(Widget.Button):
    def __init__(self):
        super().__init__(
            child = 
                Widget.Icon(
                    css_classes = ["logout-button"],
                    icon_name = "system-shutdown-symbolic",
                    pixel_size = 100,
                ),
            on_click = lambda x: Utils.exec_sh_async("poweroff")
        )

class Logout(Widget.Window):
    def __init__(self, monitor: int):
        monitor_width = Utils.get_monitor(monitor).get_geometry().width;
        monitor_height = Utils.get_monitor(monitor).get_geometry().height;

        super().__init__(
            exclusivity = "ignore",
            monitor = monitor,
            namespace = f"logout-{monitor}",
            layer = "overlay",
            kb_mode = "exclusive",
            popup = True,
            visible = False,
            child = 
                Widget.CenterBox(
                    css_classes = ["logout-back"],
                    style = f"min-width: {monitor_width}px; min-height: {monitor_height}px;",
                    center_widget = Widget.CenterBox(
                        vertical = True,
                        center_widget = Widget.Box(
                            css_classes = ["logout-window"],
                            child = [
                                PoweroffButton(),
                                RebootButton(),
                                LogoutButton(),
                                LockButton(monitor),
                            ],
                        ),
                    ),
                ),
            ),
        
