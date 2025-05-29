import asyncio
from ignis.widgets import Widget
from ignis.utils import Utils
from ignis.services.bluetooth import BluetoothService
from ignis.services.fetch import FetchService
from ignis.services.network import NetworkService, WifiAccessPoint
from ignis.services.upower import UPowerService
from datetime import datetime

bluetooth = BluetoothService.get_default()
fetch = FetchService.get_default()
network = NetworkService.get_default()
upower = UPowerService.get_default()

class StatusLine(Widget.CenterBox):
    def __init__(self):
        username = Utils.exec_sh("whoami").stdout
        username = username[:len(username)-1]
        hostname = fetch.hostname
        hostname = hostname[:len(hostname)-1]

        super().__init__()
        self.css_classes = ["control-center-statusline"]
        self.start_widget = Widget.Label(label=username+"@"+hostname)
        self.center_widget = Widget.Label(label="YY-MM-DD --- HH:MM") 
        self.end_widget = Widget.Box(
            child = [
                Widget.Icon(icon_name=upower.batteries[0].bind("icon_name"),pixel_size=20),
                Widget.Label(label=upower.batteries[0].bind("percent",lambda p: str(int(p))+"%")),
            ],
        )

        Utils.Poll(1000, lambda _: self.center_widget.set_label(datetime.now().strftime("%Y-%m-%d - %H:%M")))

class Wifi(Widget.Box):
    def __init__(self):
        super().__init__()
        title = Widget.Label(
            label = "Wi-Fi",
            css_classes = ["control-center-quick-settings-button-title"],
        )
        device = Widget.Label(
            label=network.wifi.bind(
                "is_connected",
                lambda is_connected: network.wifi.devices[0].ap.ssid if is_connected else "Disconnected",
            ),
            css_classes = ["control-center-quick-settings-button-subtitle"],
        )
        button_connection = Widget.Button(
            hexpand = True,
            css_classes = network.wifi.bind(
                "enabled",
                lambda enabled: ["control-center-quick-settings-button", "connected", "left"] if enabled else ["control-center-quick-settings-button", "left"]),
            child = Widget.Box(
                child = [
                    Widget.Icon(
                        icon_name = "network-wireless-signal-excellent-symbolic",
                        pixel_size = 30,
                        style = "margin-right:0.5rem; margin-left:0.5rem;",
                    ),
                    Widget.Box(
                        hexpand = True,
                        vertical = True,
                        child = [title, device],
                    ),
                ],
            ),
            on_click = lambda _: self.on_connection_click(),
        )
        button_details = Widget.Button(
            css_classes = network.wifi.bind(
                "enabled",
                lambda enabled: ["control-center-quick-settings-button", "connected", "right"] if enabled else ["control-center-quick-settings-button", "right"]),
            child = Widget.Icon(
                icon_name = "pan-end-symbolic",
                pixel_size = 30,
            ),
        )

        self.style="margin:0.5rem;"
        self.child = [
            button_connection, button_details,
        ]

    def on_connection_click(self):
        if network.wifi.enabled:
            asyncio.create_task(Utils.exec_sh_async("nmcli radio wifi off"))
        else:
            asyncio.create_task(Utils.exec_sh_async("nmcli radio wifi on"))

class Bluetooth(Widget.Box):
    def __init__(self):
        super().__init__()
        title = Widget.Label(
            label = "Bluetooth",
            css_classes = ["control-center-quick-settings-button-title"],
        )
        device = Widget.Label(
            label = bluetooth.bind("connected_devices", lambda devices: devices[0].alias if len(devices) > 0 else "Disonnected"),
            css_classes = ["control-center-quick-settings-button-subtitle"],
        )
        button_connection = Widget.Button(
            hexpand = True,
            css_classes = bluetooth.bind( 
                "powered",
                lambda powered: ["control-center-quick-settings-button", "connected", "left"] if powered else ["control-center-quick-settings-button", "left"]),
            child = Widget.Box(
                child = [
                    Widget.Icon(
                        icon_name = "bluetooth-active-symbolic",
                        pixel_size = 30,
                        style = "margin-right:0.5rem; margin-left:0.5rem;",
                    ),
                    Widget.Box(
                        vertical = True,
                        hexpand = True,
                        child = [title, device],
                    ),
                ],
            ),
            on_click = lambda _: self.on_connection_click(),
        )
        button_details = Widget.Button(
            css_classes = bluetooth.bind( 
                "powered",
                lambda powered: ["control-center-quick-settings-button", "connected", "right"] if powered else ["control-center-quick-settings-button", "right"]),
            child = Widget.Icon(
                icon_name = "pan-end-symbolic",
                pixel_size = 30,
            ),
        )
    
        self.style="margin:0.5rem;"
        self.child = [
            button_connection, button_details,
        ]

    def on_connection_click(self):
        if bluetooth.powered:
            asyncio.create_task(Utils.exec_sh_async("bluetoothctl power off"))
        else:
            asyncio.create_task(Utils.exec_sh_async("bluetoothctl power on"))

class MenuViewEmpty(Widget.Revealer):
    def __init__(self):
        super().__init__()
        self.child = Widget.Label(label="Background\nNothing to show yet :(")
        self.reveal_child = False
    
    def update_menu(self):
        pass 

class WifiNetworkButton(Widget.Button):
    def __init__(self, access_point: WifiAccessPoint):
        self.access_point = access_point

        super().__init__()
        self.css_classes = network.wifi.devices[0].bind("ap", lambda ap: ["control-center-menu-button", "connected" if ap.bssid == access_point.bssid else None])
        self.child = Widget.Box(child = [
            Widget.Icon(icon_name=access_point.bind("icon_name")),
            Widget.Label(label=access_point.bind("ssid")),
            Widget.Label(label=access_point.bind("bandwidth", lambda bandwidth: f"({bandwidth})")),
        ])
        self.on_click = lambda _: self.toggle_connection()

    def toggle_connection(self):
        if network.wifi.devices[0].ap.bssid == self.access_point.bssid:
            asyncio.create_task(self.access_point.disconnect_from())
        else:
            asyncio.create_task(self.access_point.connect_to_graphical())

class ControlCenterContent(Widget.Box):
    def __init__(self):
        super().__init__()
        self.css_classes = ["control-center"]
        self.vertical=True
        self.child = [
            StatusLine(),
            Widget.Box(
                child = [
                    Widget.Box(
                        vertical = True,
                        child = [
                            Wifi(),
                            Bluetooth(),
                        ],
                    ),
                    Widget.Separator(vertical=True,css_classes=["control-center-separator", "horizontal"]),
                ],
            ),
        ]

class ControlCenter(Widget.RevealerWindow):
    def __init__(self, monitor_id: int):
        revealer = Widget.Revealer(
            child = ControlCenterContent(),
            transition_type = "slide_down",
            transition_duration = 200,
            reveal_child=True,
        )

        super().__init__(namespace=f"control_center_{monitor_id}",revealer=revealer)
        self.anchor = ["top"]
        self.exclusitivity = "ignore"
        self.monitor = monitor_id
        self.visible = False 
        self.layer = "top"
        self.kb_mode = "on_demand"
        self.popup = True
        self.child = Widget.Box(child=[revealer])
