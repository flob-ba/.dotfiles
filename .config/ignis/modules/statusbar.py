from ignis.widgets import Widget
from ignis.services.audio import AudioService
from ignis.services.bluetooth import BluetoothService
from ignis.services.hyprland import HyprlandService
from ignis.services.mpris import MprisService, MprisPlayer
from ignis.services.network import NetworkService
from ignis.services.system_tray import SystemTrayService, SystemTrayItem
from ignis.services.upower import UPowerService
from ignis.utils import Utils

from datetime import datetime

audio = AudioService.get_default()
bluetooth = BluetoothService.get_default()
hypr = HyprlandService.get_default()
mpris = MprisService.get_default()
network = NetworkService.get_default()
systray = SystemTrayService.get_default()
upower = UPowerService.get_default()

class Workspace(Widget.Label):
    def __init__(self, workspace_id: int):
        super().__init__()
        self.label = f"{workspace_id}"
        self.workspace_id = workspace_id
        self.css_classes = hypr.bind_many(
            ["workspaces", "active_workspace"],
            lambda w,a: self.css_class(w,a)
        )

    def css_class(self, workspaces, active):
        if self.workspace_id == active.id:
            return ["statusbar-workspace", "active"]
        else:
            for w in workspaces:
                if w.id == self.workspace_id:
                    return ["statusbar-workspace", "occupied"]
            return ["statusbar-workspace"]

class WorkspaceModule(Widget.Box):
    def __init__(self):
        super().__init__()
        self.child = [Workspace(i) for i in range(1,11)]

class ClockModule(Widget.Label):
    def __init__(self):
        super().__init__()
        Utils.Poll(1000, lambda _: self.set_label(datetime.now().strftime("%H:%M")))

class SystemTrayItem(Widget.Button):
    def __init__(self, item: SystemTrayItem):
        super().__init__()
        self.item = item
        self.css_classes = ["statusbar-status-icon", "button"]
        self.child = Widget.Icon(image=item.bind("icon"), pixel_size=20)
        self.on_click = lambda self: self.item.activate()

class SystemTrayModule(Widget.Box):
    def __init__(self):
        super().__init__()
        self.child = systray.bind("items", lambda items : [SystemTrayItem(item) if item.id != "blueman" and item.id != "chrome_status_icon_1" else None for item in items])

class Audio(Widget.Box):
    def __init__(self):
        super().__init__()
        self.child = [
            Widget.Icon(
                css_classes = ["statusbar-status-icon"],
                icon_name = audio.speaker.bind("icon_name")),
            Widget.Icon(
                css_classes = ["statusbar-status-icon"],
                icon_name = audio.microphone.bind("icon_name")
            ),
        ]

class Network(Widget.Icon):
    def __init__(self):
        super().__init__()
        self.css_classes = ["statusbar-status-icon"]
        Utils.Poll(1000, lambda _: self.update_icon())

    def update_icon(self):
        if network.ethernet.is_connected:
            self.icon_name = network.ethernet.icon_name
        else:
            self.icon_name = network.wifi.icon_name

class Bluetooth(Widget.Icon):
    def __init__(self):
        super().__init__()
        self.css_classes = ["statusbar-status-icon"]
        self.icon_name = "bluetooth-active-symbolic"

class Battery(Widget.Icon):
    def __init__(self):
        super().__init__()
        self.css_classes = ["statusbar-status-icon"]
        self.icon_name = upower.batteries[0].bind("icon_name")
        self.pixel_size = 18

class StatusModule(Widget.Box):
    def __init__(self):
        super().__init__()
        self.child = bluetooth.bind("powered", lambda powered: [
            Audio(),
            Bluetooth() if powered else None,
            Network(),
            Battery(), 
        ])

class MediaBar(Widget.Box):
    def __init__(self, player: MprisPlayer):
        super().__init__()
        self.child = [
            Widget.Icon(image = ".dotfiles/assets/yt-music.png", pixel_size = 20, css_classes = ["statusbar-media-icon"]),
            Widget.Label(label = player.bind("title"))
        ]

class MediaModule(Widget.Box):
    def __init__(self):
        super().__init__()
        self.child = mpris.bind(
            "players",
            lambda players:
            [MediaBar(players[0])] if len(players) > 0 else [Widget.Icon(icon_name = "multimedia-player-symbolic", pixel_size = 20), Widget.Label(label = "no catjams")]
        )

class StatusBarStart(Widget.Box):
    def __init__(self):
        super().__init__()
        self.child = [
            WorkspaceModule(),
        ]
        for module in self.child:
            module.add_css_class("statusbar-module")
            module.add_css_class("left")

class StatusBarCenter(Widget.Box):
    def __init__(self):
        super().__init__()
        self.child = [
            MediaModule(), 
        ]
        for module in self.child:
            module.add_css_class("statusbar-module")
            module.add_css_class("center")

class StatusBarEnd(Widget.Box):
    def __init__(self):
        super().__init__()
        self.child = [
                SystemTrayModule(),
                StatusModule(),
                ClockModule(),
        ]
        for module in self.child:
            module.add_css_class("statusbar-module")
            module.add_css_class("right")

class StatusBar(Widget.Window):
    def __init__(self, monitor_id: int):
        super().__init__(f"statusbar_{monitor_id}")
        self.anchor = ["left", "top", "right"]
        self.exclusivity = "exclusive"
        self.monitor = monitor_id
        self.layer = "top"
        self.child = Widget.CenterBox(
            css_classes = ["statusbar"],
            start_widget = StatusBarStart(), 
            center_widget = StatusBarCenter(), 
            end_widget = StatusBarEnd(), 
        )

