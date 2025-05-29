from ignis.widgets import Widget
from ignis.utils import Utils
from ignis.services.notifications import NotificationService, Notification

notifyService = NotificationService.get_default()

class NotificationPopup(Widget.CenterBox):
    def __init__(self, notification: Notification, notificationPopups):
        super().__init__()
        self.notificationPopups = notificationPopups
        self.css_classes = ["notification-popup"]
        if notification.icon is not None:
            self.start_widget = Widget.Icon(icon_name = notification.icon, pixel_size = 50)
        self.center_widget = Widget.Box(
            vertical = True,
            child = [
                Widget.Label(
                    label = notification.summary[:50] + "..." if len(notification.summary) > 50 else notification.summary,
                    css_classes = ["notification-popup-content", "summary"]
                ) if len(notification.summary) > 0 else None,
                Widget.Label(
                    label = notification.body,
                    css_classes = ["notification-popup-content", "body"],
                ) if len(notification.body) > 0 else None,
            ],
        )
        notification.connect("dismissed", lambda _: self.on_dismissed())

    def on_dismissed(self):
        self.unparent()
        if len(notifyService.popups) == 0:
            self.notificationPopups.visible = False

class NotificationPopupList(Widget.Window):
    def __init__(self, monitor_id: int):
        super().__init__(f"notification_popup_{monitor_id}")
        self.anchor = ["top", "right"]
        self.exclusivitiy = "ignore"
        self.visible = False
        self.monitor = monitor_id
        self.child = Widget.Box(
            css_classes = ["notification-popup-list"],
            vertical = True,
        )
        notifyService.connect("new_popup", lambda _, notification: self.on_new_popup(notification))

    def on_new_popup(self, notification: Notification):
        self.visible = True
        self.child.prepend(NotificationPopup(notification, self))

