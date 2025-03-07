import datetime
from ignis.services.audio import AudioService
from ignis.services.hyprland import HyprlandService
from ignis.services.network import NetworkService
from ignis.services.upower import UPowerService
from ignis.services.upower import UPowerDevice
from ignis.app import IgnisApp
from ignis.utils import Utils
from ignis.widgets import Widget

audio = AudioService.get_default()
hypr = HyprlandService.get_default()
network = NetworkService.get_default()
upower = UPowerService.get_default()

app = IgnisApp.get_default()

class WorkspaceButton(Widget.Box):
    def __init__(self, index: int):
        super().__init__(
            child = [
                Widget.Label(
                    css_classes = ["workspace-label"],
                    label = str(index),
                ),
            ],
        )
        self.id = index
        hypr.connect("notify::workspaces", lambda x,y: self.update_css())

    def update_css(self):
        if hypr.active_workspace["id"] == self.id:
            self.css_classes = ["workspace", "active"]
            self.child[0].css_classes = ["workspace-label"]
        else:
            occupied = False
            for workspace in hypr.get_workspaces():
                if workspace["id"] == self.id:
                    self.css_classes = ["workspace", "occupied"]
                    self.child[0].css_classes = ["workspace-label"]
                    occupied = True
            if not occupied:
                self.css_classes = ["workspace", "empty"] 
                self.child[0].css_classes = ["workspace-label"]

class Workspaces(Widget.Box):
    def __init__(self):
        super().__init__(
            css_classes = ["workspaces"],
            child = [WorkspaceButton(i) for i in range(1,11)]
        )

class Audio(Widget.Box):
    def __init__(self):
        super().__init__(
            css_classes = ["audio"],
            child = [
                Widget.Icon(
                    css_classes = ["audio-icon"],
                    icon_name = audio.microphone.bind("icon_name"),
                ),
                Widget.Icon(
                    css_classes = ["audio-icon"],
                    icon_name = audio.speaker.bind("icon_name"),
                ),
                Widget.Label(
                    label = audio.speaker.bind_many(["volume", "is_muted"], lambda volume, is_muted: "0%" if volume is None else ("" if is_muted else f"{int(volume)}%")),
                ),
            ],
        )

class Clock(Widget.Label):
    def __init__(self):
        super().__init__()
        Utils.Poll(1000 / 30, lambda _: self.update_label())

    def update_label(self):
        self.set_label(datetime.datetime.now().strftime("%H:%M:%S:%f")[:-4])

class Network(Widget.Icon):
    def __init__(self):
        super().__init__(
            css_classes = ["network-icon"],
        )
        self.update_icon()
        Utils.Poll(100, lambda _: self.update_icon())

    def update_icon(self):
        if network.ethernet.get_is_connected():
            self.icon_name = network.ethernet.get_icon_name()
        else:
            self.icon_name = network.wifi.get_icon_name()

class Battery(Widget.Box):
    def __init__(self, device: UPowerDevice):
        super().__init__(
            css_classes = ["battery"],
            child = [
                Widget.Icon(
                    icon_name = device.bind("icon_name"),
                ),
                Widget.Label(
                    label = device.bind("percent", lambda x: f"{int(x)}%"),
                ),
            ],
        )

class Power(Widget.Button):
    def __init__(self, monitor):
        super().__init__(
            css_classes = ["power"],
            child = Widget.Icon(
                icon_name = "system-shutdown-symbolic",
            ),
            on_click = lambda _: app.open_window(f"logout-{monitor}")
        )

class Bar(Widget.Window):
    def __init__(self, monitor: int):
        super().__init__(
            anchor = ["left","top","right"],
            exclusivity = "exclusive",
            monitor = monitor,
            namespace = f"bar-{monitor}",
            layer = "top",
            kb_mode = "none",
            child = Widget.CenterBox(
                css_classes = ["statusbar"],
                start_widget = Workspaces(),
                center_widget = Clock(),
                end_widget = Widget.Box(
                    child = [
                        Audio(),
                        Network(),
                        Battery(upower.batteries[0]),
                        #Power(monitor),
                    ],
                ),
            ),
        )
