import asyncio
import time
from ignis.widgets import Widget
from ignis.utils import Utils
from ignis.services.bluetooth import BluetoothService, BluetoothDevice
from ignis.services.fetch import FetchService
from ignis.services.network import NetworkService, WifiAccessPoint, WifiDevice, VpnConnection
from ignis.services.notifications import NotificationService
from ignis.services.upower import UPowerService
from datetime import datetime

bluetooth = BluetoothService.get_default()
fetch = FetchService.get_default()
network = NetworkService.get_default()
notify = NotificationService.get_default()
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

class AudioModule(Widget.CenterBox):
    def __init__(self):
        super().__init__()
        self.css_classes = ["control-center-module", "control-center-audio-module"]
        self.center_widget = Widget.Icon(icon_name="audio-volume-high-symbolic", pixel_size=50)

class QSButton(Widget.Button):
    def __init__(self, control_module: "ControlModule", menu: str):
        super().__init__()
        self.control_module = control_module
        self.menu = menu
        self.css_classes = ["control-center-qs-button"]

    def on_click(self, _):
        self.control_module.open_menu(self.menu)

class QSButtonNotify(QSButton):
    def __init__(self, control_module: "ControlModule"):
        super().__init__(control_module, "notify")
        self.child = Widget.CenterBox(
            start_widget = Widget.Icon(icon_name = "notification-symbolic", pixel_size=20),
            center_widget = notify.bind(
                "notifications",
                lambda notifications:
                Widget.Label(label = self.construct_label(notifications))
            ), 
            end_widget = Widget.Icon(icon_name = "pan-end-symbolic"),
        )
    
    def construct_label(self, notifications):
        if len(notifications) == 0:
            return "No Notifications"
        elif len(notifications) == 1:
            return "1 Notification"
        else:
            return f"{len(notifications)} Notifications"

class QSButtonWifi(QSButton):
    def __init__(self, control_module: "ControlModule"):
        super().__init__(control_module, "wifi")
        self.button_label = Widget.Label(label = "wifi")
        self.child = Widget.CenterBox(
            start_widget = Widget.Icon(icon_name = "network-wireless-signal-excellent-symbolic", pixel_size=20),
            center_widget = network.wifi.devices[0].bind_many(
                ["is_connected", "ap"],
                lambda is_connected, ap:
                Widget.Label(label = self.construct_label(is_connected, ap))
            ),
            end_widget = Widget.Icon(icon_name = "pan-end-symbolic"),
        )

    def construct_label(self, is_connected: bool, ap: WifiAccessPoint):
        if not is_connected:
            return "Disconnected"
        return ap.ssid

class QSButtonBluetooth(QSButton):
    def __init__(self, control_module: "ControlModule"):
        super().__init__(control_module, "bluetooth")
        self.child = Widget.CenterBox(
            start_widget = Widget.Icon(icon_name = "bluetooth-active-symbolic", pixel_size=20),
            center_widget = bluetooth.bind(
                "connected_devices",
                lambda connected_devices:
                Widget.Label(label = self.construct_label(connected_devices))
            ),
            end_widget = Widget.Icon(icon_name = "pan-end-symbolic"),
        )
    
    def construct_label(self, connected_devices):
        if len(connected_devices) == 0:
            return "Disconnected"
        elif len(connected_devices) == 1:
            return connected_devices[0].alias
        else:
            return f"Paired {len(connected_devices)} Devices"

class QSButtonVpn(QSButton):
    def __init__(self, control_module: "ControlModule"):
        super().__init__(control_module, "vpn")
        self.child = Widget.CenterBox(
            start_widget = Widget.Icon(icon_name = "security-high-symbolic", pixel_size=20),
            center_widget =  network.vpn.bind(
                "active_connections",
                lambda active_connections:
                Widget.Label(label = self.construct_label(active_connections))
            ),
            end_widget = Widget.Icon(icon_name = "pan-end-symbolic"),
        )

    def construct_label(self, active_connections):
        if len(active_connections) == 0:
            return "Disconnected"
        elif len(active_connections) == 1:
            return active_connections[0].name
        else:
            return f"{len(active_connections)} Connections"

class QSMenu(Widget.Revealer):
    def __init__(self):
        super().__init__()
        self.transition_type = "slide_right"

    def open(self):
        self.reveal_child = True

class QSMenuNotify(QSMenu):
    def __init__(self):
        super().__init__()
        self.child = Widget.Label(label="NOTIFY")

class WifiItem(Widget.Button):
    def __init__(self, ap: WifiAccessPoint):
        super().__init__()
        self.ap = ap
        
        self.css_classes = ["control-center-menu-item"] 
        self.css_classes = network.wifi.devices[0].bind_many(
            ["is_connected", "ap"],
            lambda is_connected, xap: [
                "control-center-menu-item",
                "connected" if is_connected and xap.bssid == self.ap.bssid else None
            ],
        )
        self.child = Widget.Box(
            child = ap.bind(
                "icon_name",
                lambda icon_name: [
                    Widget.Icon(icon_name = icon_name),
                    Widget.Label(label = f"{ap.ssid} ({str(ap.bandwidth)} MHz)")
                ],
            ),
        )

    def on_click(self, _):
        if network.wifi.devices[0].ap.bssid == self.ap.bssid:
            asyncio.create_task(self.ap.disconnect_from())
        else:
            asyncio.create_task(self.ap.connect_to_graphical())

class QSMenuWifi(QSMenu):
    def __init__(self):
        super().__init__()
        self.child = Widget.Scroll(
            css_classes = ["control-center-menu"],
            child = Widget.Box(
                vertical = True,
                child = network.wifi.devices[0].bind("state", lambda state: [
                    Widget.Label(label = "Wi-Fi", css_classes = ["control-center-menu-title"]),
                    Widget.Label(label = f"State: {state}"),
                    Widget.Box(
                        vertical = True,
                        child = network.wifi.devices[0].bind(
                            "access_points",
                            lambda access_points: [WifiItem(ap) if ap.ssid is not None else None for ap in access_points],
                        ),
                    ),
                ]),
            ),
        )
    def open(self):
        super().open()
        asyncio.create_task(network.wifi.devices[0].scan())

class BluetoothItem(Widget.Button):
    def __init__(self, device: BluetoothDevice):
        super().__init__()
        self.device = device
        
        self.css_classes = ["control-center-menu-item"] 
        self.css_classes = device.bind(
            "connected",
            lambda is_connected: [
                "control-center-menu-item",
                "connected" if is_connected else None
            ],
        )
        self.child = Widget.Box(
            child = device.bind(
                "icon_name",
                lambda icon_name: [
                    Widget.Icon(icon_name = icon_name),
                    Widget.Label(label = f"{device.alias}")
                ],
            ),
        )

    def on_click(self, _):
        if self.device.connected:
            asyncio.create_task(self.device.disconnect_from())
        else:
            asyncio.create_task(self.device.connect_to())

class QSMenuBluetooth(QSMenu):
    def __init__(self):
        super().__init__()
        self.child = Widget.Scroll(
            css_classes = ["control-center-menu"],
            child = Widget.Box(
                vertical = True,
                child = bluetooth.bind("state", lambda state: [
                    Widget.Label(label = "Bluetooth", css_classes = ["control-center-menu-title"]),
                    Widget.Label(label = f"State: {state}"),
                    Widget.Box(
                        vertical = True,
                        child = bluetooth.bind(
                            "devices",
                            lambda devices: [BluetoothItem(device) for device in devices],
                        ),
                    ),
                ]),
            ),
        )

    def open(self):
        super().open()
        bluetooth.setup_mode = True

class VpnItem(Widget.Button):
    def __init__(self, connection: VpnConnection):
        super().__init__()
        self.connection = connection
        
        self.css_classes = ["control-center-menu-item"] 
        self.css_classes = connection.bind(
            "is_connected",
            lambda is_connected: [
                "control-center-menu-item",
                "connected" if is_connected else None
            ],
        )
        self.child = Widget.Box(
            child = [ 
                Widget.Icon(icon_name = "network-vpn-symbolic"),
                Widget.Label(label = f"{connection.name}")
            ],
        )

    def on_click(self, _):
        asyncio.create_task(self.connection.toggle_connection())

class QSMenuVpn(QSMenu):
    def __init__(self):
        super().__init__()
        self.child = Widget.Scroll(
            css_classes = ["control-center-menu"],
            child = Widget.Box(
                vertical = True,
                child = [ 
                    Widget.Label(label = "VPN", css_classes = ["control-center-menu-title"]),
                    Widget.Box(
                        vertical = True,
                        child = network.vpn.bind(
                            "connections",
                            lambda connections: [VpnItem(connection) for connection in connections],
                        ),
                    ),
                ],
            ),
        )

    def open(self):
        super().open()
        bluetooth.setup_mode = True

class ControlModule(Widget.Box):
    def __init__(self):
        super().__init__()

        self.qs_button_notify = QSButtonNotify(self)
        self.qs_button_wifi = QSButtonWifi(self)
        self.qs_button_bluetooth = QSButtonBluetooth(self)
        self.qs_button_vpn = QSButtonVpn(self)

        self.qs_menu_notify = QSMenuNotify()
        self.qs_menu_wifi = QSMenuWifi()
        self.qs_menu_bluetooth = QSMenuBluetooth()
        self.qs_menu_vpn = QSMenuVpn()

        self.current_menu = None
        self.open_menu("wifi")

        self.css_classes = ["control-center-module"]
        self.child = [
            Widget.Box(
                vertical = True,
                child = [self.qs_button_notify, self.qs_button_wifi, self.qs_button_bluetooth, self.qs_button_vpn],
            ),
            self.qs_menu_notify,
            self.qs_menu_wifi,
            self.qs_menu_bluetooth,
            self.qs_menu_vpn,
        ]

    def get_qs_button(self, menu: str):
        if menu == "notify":
            return self.qs_button_notify
        if menu == "wifi":
            return self.qs_button_wifi
        if menu == "bluetooth":
            return self.qs_button_bluetooth
        if menu == "vpn":
            return self.qs_button_vpn

    def get_qs_menu(self, menu: str):
        if menu == "notify":
            return self.qs_menu_notify
        if menu == "wifi":
            return self.qs_menu_wifi
        if menu == "bluetooth":
            return self.qs_menu_bluetooth
        if menu == "vpn":
            return self.qs_menu_vpn

    def open_menu(self, menu: str):
        if self.current_menu == menu:
            return

        if self.current_menu is not None:
            self.get_qs_menu(self.current_menu).reveal_child = False
            self.get_qs_button(self.current_menu).remove_css_class("active") 
            Utils.Timeout(self.get_qs_menu(self.current_menu).transition_duration, lambda: self.get_qs_menu(menu).open())
        else:
            self.get_qs_menu(menu).open()

        self.get_qs_button(menu).add_css_class("active")
        self.current_menu = menu

class ControlCenterContent(Widget.Box):
    def __init__(self):
        super().__init__()
        self.css_classes = ["control-center"]
        self.vertical=True
        self.child = [
            StatusLine(),
            Widget.Box(child = [
                #AudioModule(),
                ControlModule(),
            ])
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

