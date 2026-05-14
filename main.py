import requests
from datetime import datetime, timedelta
import webbrowser
import os
import re

from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics import Color, RoundedRectangle, Line


DATA_URL = "http://157.10.252.46:5000/signal"
BASE_DIR = os.path.dirname(__file__)


# =========================
# CARD
# =========================
class Card(BoxLayout):

    def __init__(self, bg=(0.1,0.1,0.15,1), border=(0.2,0.7,1,1), h=90, **kwargs):
        super().__init__(**kwargs)

        self.orientation = "vertical"
        self.padding = dp(5)
        self.spacing = dp(3)

        self.size_hint_y = None
        self.height = dp(h)

        with self.canvas.before:
            self.bg = Color(*bg)
            self.rect = RoundedRectangle(radius=[14])

        with self.canvas.after:
            self.border = Color(*border)
            self.line = Line(rounded_rectangle=(0,0,0,0,14), width=1)

        self.bind(pos=self.update, size=self.update)

    def update(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.line.rounded_rectangle = (*self.pos, *self.size, 14)

    def set_bg(self, c):
        self.bg.rgba = c


# =========================
# HOME SCREEN
# =========================
class Home(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)

        root = BoxLayout(orientation="vertical")

        # HEADER IMAGE
        root.add_widget(
            Image(
                source=os.path.join(BASE_DIR, "file_00000000989c71fa995c0bb4f763659a.png"),
                size_hint_y=None,
                height=dp(140),
                allow_stretch=True,
                keep_ratio=False
            )
        )

        # TOP
        top = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(3))

        self.market = Card(h=40)
        self.clock = Card(h=40)

        self.market_label = Label(text="CRYPTO ID 85%", font_size=dp(12))
        self.clock_label = Label(text="00:00:00 WIB", font_size=dp(12))

        self.market.add_widget(self.market_label)
        self.clock.add_widget(self.clock_label)

        top.add_widget(self.market)
        top.add_widget(self.clock)

        root.add_widget(top)

        # SIGNAL
        self.signal = Card(h=120)

        self.signal_title = Label(text="SIGNAL KONFIGURASI TRADE", font_size=dp(16), bold=True)
        self.signal_main = Label(text="WAITING....", font_size=dp(14))
        self.signal_status = Label(text="DETECTED", font_size=dp(12))

        self.signal.add_widget(self.signal_title)
        self.signal.add_widget(self.signal_main)
        self.signal.add_widget(self.signal_status)

        root.add_widget(self.signal)

        # EXPIRY
        self.expire_label = Label(text="MENUNGGU SIGNAL", size_hint_y=None, height=dp(30))
        root.add_widget(self.expire_label)

        # HISTORY TITLE
        root.add_widget(Label(text="HISTORY", size_hint_y=None, height=dp(20)))

        # ===== HISTORY 7 KOLOM HEADER =====
        header = BoxLayout(size_hint_y=None, height=dp(25), spacing=dp(2))
        for t in ["SIGNAL","ENTRY","STATUS","K1","K2","K3","K4"]:
            header.add_widget(Label(text=t, font_size=dp(10)))
        root.add_widget(header)

        # ===== HISTORY TABLE =====
        self.history_scroll = ScrollView()

        self.history_box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(2)
        )

        self.history_box.bind(minimum_height=self.history_box.setter("height"))

        self.history_scroll.add_widget(self.history_box)
        root.add_widget(self.history_scroll)

        self.add_widget(root)

        # VAR
        self.history = []
        self.expiry_time = None
        self.last_signal = ""
        self.state = "WAIT"

        Clock.schedule_interval(self.load, 2)
        Clock.schedule_interval(self.clock_update, 1)
        Clock.schedule_interval(self.update_expiry, 1)

    def clock_update(self, dt):
        self.clock_label.text = datetime.now().strftime("%H:%M:%S WIB")

    def set_signal(self, mode, signal="", entry=""):

        if mode == "ACTIVE":
            self.signal.set_bg((0, 0.8, 0.3, 1) if signal == "BUY" else (1, 0.1, 0.2, 1))
            self.signal_main.text = f"ENTRY {signal} {entry}"
            self.signal_status.text = "ACTIVE"

        elif mode == "EXPIRED":
            self.signal.set_bg((0.2, 0.2, 0.2, 1))
            self.signal_main.text = "SIGNAL EXPIRED"
            self.signal_status.text = "DETECTED"

        else:
            self.signal.set_bg((0.1, 0.1, 0.15, 1))
            self.signal_main.text = "WAITING...."
            self.signal_status.text = "DETECTED"

    def update_expiry(self, dt):

        if not self.expiry_time:
            self.expire_label.text = "MENUNGGU SIGNAL"
            return

        remaining = int((self.expiry_time - datetime.now()).total_seconds())

        if remaining <= 0:
            self.expiry_time = None
            self.state = "WAIT"
            self.set_signal("EXPIRED")
            self.expire_label.text = "EXPIRED : 0 DETIK"
            return

        self.expire_label.text = f"EXPIRED : {remaining} DETIK"

    def load(self, dt):

        try:
            data = requests.get(DATA_URL, timeout=5).json()

            signal = data.get("signal", "WAITING").upper()
            entry = data.get("entry_time")

            if signal in ["BUY", "SELL"] and entry:

                key = f"{signal}_{entry}"

                if key != self.last_signal:

                    self.state = "ACTIVE"
                    self.set_signal("ACTIVE", signal, entry)

                    try:
                        h, m = map(int, entry.split(":"))
                        base = datetime.now().replace(hour=h, minute=m, second=0)
                        self.expiry_time = base + timedelta(minutes=1)
                    except:
                        self.expiry_time = datetime.now() + timedelta(seconds=60)

                    self.last_signal = key

            else:
                self.state = "WAIT"
                self.set_signal("WAIT")
                self.expiry_time = None

            # ===== HISTORY 7 KOLOM ROW =====
            row = BoxLayout(size_hint_y=None, height=dp(20), spacing=dp(2))

            row.add_widget(Label(text=signal, font_size=dp(10)))
            row.add_widget(Label(text=str(entry)))
            row.add_widget(Label(text="ACTIVE"))

            for _ in range(4):
                row.add_widget(Label(text="-"))

            self.history_box.add_widget(row)

        except:
            self.set_signal("WAIT")
            self.expire_label.text = "SERVER ERROR"


# =========================
# MARTINGALE SCREEN
# =========================
class Martingale(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)

        self.row_state = {}

        root = BoxLayout(orientation="vertical")

        self.header = Card(h=60)
        self.header_label = Label(text="SIGNAL VIP STC", font_size=dp(18), bold=True)
        self.header.add_widget(self.header_label)
        root.add_widget(self.header)

        self.input = TextInput(hint_text="Paste SIGNAL", size_hint_y=None, height=dp(100))
        self.enter_btn = Button(text="ENTER", size_hint_y=None, height=dp(50))

        root.add_widget(self.input)
        root.add_widget(self.enter_btn)

        self.scroll = ScrollView()

        self.list_box = BoxLayout(
            orientation="vertical",
            size_hint_y=None
        )
        self.list_box.bind(minimum_height=self.list_box.setter("height"))

        self.scroll.add_widget(self.list_box)
        root.add_widget(self.scroll)

        self.add_widget(root)


# =========================
# APP
# =========================
class AppMain(App):

    def build(self):

        sm = ScreenManager()
        sm.add_widget(Home(name="home"))
        sm.add_widget(Martingale(name="mart"))

        root = BoxLayout(orientation="vertical")
        root.add_widget(sm)

        nav = BoxLayout(size_hint_y=None, height=dp(50))

        nav.add_widget(Button(text="HOME", on_press=lambda x: sm.switch_to(sm.get_screen("home"))))
        nav.add_widget(Button(text="MART", on_press=lambda x: sm.switch_to(sm.get_screen("mart"))))
        nav.add_widget(Button(text="TRADE", on_press=lambda x: webbrowser.open("https://stcbroker.id")))

        root.add_widget(nav)

        return root


if __name__ == "__main__":
    AppMain().run().
