import requests
import time
from datetime import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView


# =========================
# VPS API
# =========================
DATA_URL = "http://157.10.252.46:5000/signal"

Window.clearcolor = (0.05, 0.05, 0.07, 1)


# =========================
# CARD
# =========================
class Card(BoxLayout):

    def __init__(
        self,
        bg=(0.15, 0.15, 0.18, 1),
        border=(0.25, 0.25, 0.3, 1),
        radius=18,
        **kwargs
    ):

        super().__init__(**kwargs)

        self.orientation = "vertical"
        self.padding = 15
        self.spacing = 10
        self.size_hint_y = None

        with self.canvas.before:

            self.bg_color = Color(*bg)

            self.rect = RoundedRectangle(
                radius=[radius]
            )

        with self.canvas.after:

            self.line_color = Color(*border)

            self.line = Line(
                rounded_rectangle=(0, 0, 0, 0, radius),
                width=1.5
            )

        self.bind(pos=self.update_canvas)
        self.bind(size=self.update_canvas)

    def update_canvas(self, *args):

        self.rect.pos = self.pos
        self.rect.size = self.size

        self.line.rounded_rectangle = (
            self.x,
            self.y,
            self.width,
            self.height,
            18
        )

    def set_bg(self, color):

        self.bg_color.rgba = color


# =========================
# HISTORY ROW
# =========================
class HistoryRow(Card):

    def __init__(self, text="-", color_type="empty", **kwargs):

        bg = (0.18, 0.18, 0.2, 1)

        if color_type == "buy":
            bg = (0.0, 0.55, 0.2, 1)

        elif color_type == "sell":
            bg = (0.65, 0.0, 0.0, 1)

        super().__init__(
            bg=bg,
            border=(0.3, 0.3, 0.35, 1),
            height=45,
            padding=10,
            **kwargs
        )

        self.label = Label(
            text=text,
            font_size=15,
            bold=True,
            color=(1, 1, 1, 1),
            halign="left",
            valign="middle"
        )

        self.label.bind(
            size=self.label.setter("text_size")
        )

        self.add_widget(self.label)


# =========================
# MAIN CONTENT
# =========================
class Content(BoxLayout):

    def __init__(self, **kwargs):

        super().__init__(
            orientation="vertical",
            spacing=12,
            padding=10,
            size_hint_y=None,
            **kwargs
        )

        self.bind(
            minimum_height=self.setter("height")
        )

        self.history_data = []

        # =========================
        # TOP BAR
        # =========================
        self.topbar = Card(
            bg=(0.08, 0.12, 0.18, 1),
            border=(0.1, 0.5, 1, 1),
            height=90
        )

        self.title = Label(
            text="AI SIGNAL PRO",
            font_size=38,
            bold=True,
            color=(0.1, 0.7, 1, 1)
        )

        self.topbar.add_widget(self.title)

        self.add_widget(self.topbar)

        # =========================
        # MARKET + CLOCK
        # =========================
        row = BoxLayout(
            orientation="horizontal",
            spacing=10,
            size_hint_y=None,
            height=80
        )

        # MARKET CARD
        self.market_card = Card(
            bg=(0.05, 0.12, 0.10, 1),
            border=(0.0, 1, 0.6, 1),
            height=80
        )

        self.market_label = Label(
            text="MARKET : CRYPTO IDX",
            font_size=20,
            bold=True,
            color=(0.1, 1, 0.7, 1)
        )

        self.market_card.add_widget(
            self.market_label
        )

        # CLOCK CARD
        self.clock_card = Card(
            bg=(0.05, 0.10, 0.15, 1),
            border=(0.1, 0.7, 1, 1),
            height=80
        )

        self.clock_label = Label(
            text="00:00:00 WIB",
            font_size=24,
            bold=True,
            color=(0, 1, 0.6, 1)
        )

        self.clock_card.add_widget(
            self.clock_label
        )

        row.add_widget(self.market_card)
        row.add_widget(self.clock_card)

        self.add_widget(row)

        # =========================
        # BIG SIGNAL CARD
        # =========================
        self.signal_card = Card(
            bg=(0.2, 0.2, 0.2, 1),
            border=(0.4, 0.4, 0.4, 1),
            height=240
        )

        self.signal_label = Label(
            text="SEDANG KONFIGURASI",
            font_size=42,
            bold=True,
            color=(1, 1, 1, 1)
        )

        self.signal_info = Label(
            text="MENUNGGU SIGNAL",
            font_size=18,
            color=(1, 1, 1, 1)
        )

        self.signal_card.add_widget(
            self.signal_label
        )

        self.signal_card.add_widget(
            self.signal_info
        )

        self.add_widget(self.signal_card)

        # =========================
        # ENTRY CARD
        # =========================
        self.entry_card = Card(
            bg=(0.12, 0.12, 0.15, 1),
            border=(0.2, 0.6, 1, 1),
            height=90
        )

        self.entry_label = Label(
            text="ENTRY : -",
            font_size=24,
            bold=True,
            color=(1, 1, 1, 1)
        )

        self.entry_card.add_widget(
            self.entry_label
        )

        self.add_widget(self.entry_card)

        # =========================
        # SYSTEM ACTIVE CARD
        # =========================
        self.system_card = Card(
            bg=(0.08, 0.10, 0.13, 1),
            border=(0.1, 0.6, 1, 1),
            height=70
        )

        self.system_label = Label(
            text="SYSTEM ACTIVE",
            font_size=20,
            bold=True,
            color=(0.1, 0.8, 1, 1)
        )

        self.system_card.add_widget(
            self.system_label
        )

        self.add_widget(self.system_card)

        # =========================
        # HISTORY TITLE
        # =========================
        self.history_title = Label(
            text="HISTORY SIGNAL",
            font_size=22,
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=40
        )

        self.add_widget(self.history_title)

        # =========================
        # HISTORY ROWS
        # =========================
        self.history_rows = []

        for i in range(10):

            row = HistoryRow(
                text="-",
                color_type="empty"
            )

            self.history_rows.append(row)

            self.add_widget(row)

        # =========================
        # LOOP
        # =========================
        Clock.schedule_interval(
            self.update_clock,
            1
        )

        Clock.schedule_interval(
            self.load_signal,
            2
        )

    # =========================
    # CLOCK
    # =========================
    def update_clock(self, dt):

        now = datetime.now()

        self.clock_label.text = now.strftime(
            "%H:%M:%S WIB"
        )

    # =========================
    # SIGNAL EXPIRED CHECK
    # =========================
    def check_expired(self, entry_time):

        try:

            now = datetime.now().strftime("%H:%M")

            current = datetime.strptime(
                now,
                "%H:%M"
            )

            signal_time = datetime.strptime(
                entry_time,
                "%H:%M"
            )

            return current > signal_time

        except:

            return False

    # =========================
    # LOAD SIGNAL
    # =========================
    def load_signal(self, dt):

        try:

            r = requests.get(
                DATA_URL + "?t=" + str(time.time()),
                timeout=5
            )

            data = r.json()

            signal = data.get(
                "signal",
                "WAITING"
            )

            market = data.get(
                "market",
                "CRYPTO IDX"
            )

            entry_time = data.get(
                "entry_time",
                "-"
            )

            self.market_label.text = (
                f"MARKET : {market}"
            )

            expired = self.check_expired(
                entry_time
            )

            # =========================
            # BUY
            # =========================
            if signal.upper() == "BUY":

                self.signal_card.set_bg(
                    (0.0, 0.75, 0.2, 1)
                )

                self.signal_label.text = (
                    "BUY NOW"
                )

                self.signal_info.text = (
                    "AI SIGNAL ACTIVE"
                )

                if expired:

                    self.entry_label.text = (
                        "ENTRY CLOSED\nWAIT NEXT SIGNAL"
                    )

                else:

                    self.entry_label.text = (
                        f"ENTRY BUY DI JAM {entry_time}"
                    )

                new_data = (
                    f"{market} | {entry_time} | BUY"
                )

                if len(self.history_data) == 0 or \
                   self.history_data[0]["text"] != new_data:

                    self.history_data.insert(
                        0,
                        {
                            "text": new_data,
                            "type": "buy"
                        }
                    )

            # =========================
            # SELL
            # =========================
            elif signal.upper() == "SELL":

                self.signal_card.set_bg(
                    (0.75, 0.0, 0.0, 1)
                )

                self.signal_label.text = (
                    "SELL NOW"
                )

                self.signal_info.text = (
                    "AI SIGNAL ACTIVE"
                )

                if expired:

                    self.entry_label.text = (
                        "ENTRY CLOSED\nWAIT NEXT SIGNAL"
                    )

                else:

                    self.entry_label.text = (
                        f"ENTRY SELL DI JAM {entry_time}"
                    )

                new_data = (
                    f"{market} | {entry_time} | SELL"
                )

                if len(self.history_data) == 0 or \
                   self.history_data[0]["text"] != new_data:

                    self.history_data.insert(
                        0,
                        {
                            "text": new_data,
                            "type": "sell"
                        }
                    )

            # =========================
            # WAITING
            # =========================
            else:

                self.signal_card.set_bg(
                    (0.2, 0.2, 0.2, 1)
                )

                self.signal_label.text = (
                    "SEDANG KONFIGURASI"
                )

                self.signal_info.text = (
                    "MENUNGGU SIGNAL"
                )

                self.entry_label.text = (
                    "ENTRY : -"
                )

            # =========================
            # UPDATE HISTORY
            # =========================
            self.history_data = self.history_data[:10]

            for i in range(10):

                if i < len(self.history_data):

                    item = self.history_data[i]

                    self.history_rows[i].label.text = (
                        item["text"]
                    )

                    if item["type"] == "buy":

                        self.history_rows[i].set_bg(
                            (0.0, 0.55, 0.2, 1)
                        )

                    else:

                        self.history_rows[i].set_bg(
                            (0.65, 0.0, 0.0, 1)
                        )

                else:

                    self.history_rows[i].label.text = "-"

                    self.history_rows[i].set_bg(
                        (0.18, 0.18, 0.2, 1)
                    )

        except Exception as e:

            self.signal_label.text = "OFFLINE"

            self.signal_info.text = (
                "SERVER ERROR"
            )

            print("ERROR :", e)


# =========================
# MAIN APP
# =========================
class AISignalApp(App):

    def build(self):

        root = BoxLayout(
            orientation="vertical"
        )

        # SCROLL CONTENT
        scroll = ScrollView()

        content = Content()

        scroll.add_widget(content)

        # FIXED NAVBAR
        navbar = BoxLayout(
            orientation="horizontal",
            spacing=8,
            size_hint_y=None,
            height=60,
            padding=5
        )

        btn_home = Button(
            text="HOME",
            font_size=18,
            background_color=(0.08, 0.08, 0.1, 1)
        )

        btn_history = Button(
            text="HISTORY",
            font_size=18,
            background_color=(0.08, 0.08, 0.1, 1)
        )

        btn_profile = Button(
            text="PROFILE",
            font_size=18,
            background_color=(0.08, 0.08, 0.1, 1)
        )

        navbar.add_widget(btn_home)
        navbar.add_widget(btn_history)
        navbar.add_widget(btn_profile)

        root.add_widget(scroll)
        root.add_widget(navbar)

        return root


# =========================
# RUN
# =========================
if __name__ == "__main__":

    AISignalApp().run()
