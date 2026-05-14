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


# =========================
# API (FIXED)
# =========================
DATA_URL = "http://157.10.252.46:5000/app_state"
BASE_DIR = os.path.dirname(__file__)


# =========================
# CARD UI
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

        self.history = []
        self.expiry_time = None
        self.last_signal = ""

        root = BoxLayout(orientation="vertical")

        # HEADER IMAGE
        root.add_widget(
            Image(
                source=os.path.join(BASE_DIR, "banner.png"),
                size_hint_y=None,
                height=dp(140),
                allow_stretch=True,
                keep_ratio=False
            )
        )

        # TOP BAR
        top = BoxLayout(size_hint_y=None, height=dp(40))

        self.market = Card(h=40)
        self.clock = Card(h=40)

        self.market_label = Label(text="CRYPTO IDX", font_size=dp(12))
        self.clock_label = Label(text="00:00:00", font_size=dp(12))

        self.market.add_widget(self.market_label)
        self.clock.add_widget(self.clock_label)

        top.add_widget(self.market)
        top.add_widget(self.clock)

        root.add_widget(top)

        # SIGNAL
        self.signal = Card(h=120)
        self.signal_title = Label(text="SIGNAL STC", font_size=dp(16), bold=True)
        self.signal_main = Label(text="WAITING", font_size=dp(14))
        self.signal_status = Label(text="DETECTED", font_size=dp(12))

        self.signal.add_widget(self.signal_title)
        self.signal.add_widget(self.signal_main)
        self.signal.add_widget(self.signal_status)

        root.add_widget(self.signal)

        self.expire_label = Label(text="MENUNGGU SIGNAL", size_hint_y=None, height=dp(30))
        root.add_widget(self.expire_label)

        # HISTORY
        root.add_widget(Label(text="HISTORY", size_hint_y=None, height=dp(20)))

        self.history_scroll = ScrollView()
        self.history_box = BoxLayout(orientation="vertical", size_hint_y=None)
        self.history_box.bind(minimum_height=self.history_box.setter("height"))

        self.history_scroll.add_widget(self.history_box)
        root.add_widget(self.history_scroll)

        self.add_widget(root)

        Clock.schedule_interval(self.load, 2)
        Clock.schedule_interval(self.update_expiry, 1)
        Clock.schedule_interval(self.clock_update, 1)

    def clock_update(self, dt):
        self.clock_label.text = datetime.now().strftime("%H:%M:%S")

    def set_signal(self, mode, signal="", entry=""):

        if mode == "ACTIVE":
            self.signal.set_bg((0,0.8,0.3,1) if signal=="BUY" else (1,0.2,0.2,1))
            self.signal_main.text = f"{signal} {entry}"
            self.signal_status.text = "ACTIVE"

        elif mode == "EXPIRED":
            self.signal.set_bg((0.2,0.2,0.2,1))
            self.signal_main.text = "EXPIRED"
            self.signal_status.text = "DETECTED"

        else:
            self.signal.set_bg((0.1,0.1,0.15,1))
            self.signal_main.text = "WAITING"
            self.signal_status.text = "DETECTED"

    def update_expiry(self, dt):

        if not self.expiry_time:
            return

        remaining = int((self.expiry_time - datetime.now()).total_seconds())

        if remaining <= 0:
            self.expiry_time = None
            self.set_signal("EXPIRED")
            return

        self.expire_label.text = f"EXPIRED {remaining}s"

    def load(self, dt):

        try:
            data = requests.get(DATA_URL, timeout=5).json()
        except:
            data = {}

        signal = (data.get("signal") or "WAITING").upper()
        entry = data.get("entry_time") or "-"

        if signal in ["BUY", "SELL"]:

            key = f"{signal}_{entry}"

            if key != self.last_signal:
                self.set_signal("ACTIVE", signal, entry)
                self.expiry_time = datetime.now() + timedelta(minutes=1)
                self.last_signal = key

        hist = f"{signal} | {entry}"

        if not self.history or self.history[0] != hist:
            self.history.insert(0, hist)
            self.history_box.add_widget(Label(text=hist, size_hint_y=None, height=dp(25)))


# =========================
# MARTINGALE
# =========================
class Martingale(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)

        self.row_state = {}

        root = BoxLayout(orientation="vertical")

        self.header = Label(text="SIGNAL VIP STC", size_hint_y=None, height=dp(50))
        root.add_widget(self.header)

        self.input = TextInput(size_hint_y=None, height=dp(120))
        root.add_widget(self.input)

        btn = Button(text="ENTER", size_hint_y=None, height=dp(60))
        btn.bind(on_press=self.parse)
        root.add_widget(btn)

        self.scroll = ScrollView()
        self.list_box = BoxLayout(orientation="vertical", size_hint_y=None)
        self.list_box.bind(minimum_height=self.list_box.setter("height"))
        self.scroll.add_widget(self.list_box)

        root.add_widget(self.scroll)

        clear = Button(text="HAPUS ALL", size_hint_y=None, height=dp(60))
        clear.bind(on_press=self.reset)
        root.add_widget(clear)

        self.add_widget(root)

    def reset(self, *args):
        self.list_box.clear_widgets()
        self.row_state = {}

    def parse(self, instance):

        txt = self.input.text.upper()
        data = re.findall(r'(\d{1,2}:\d{2})\s*([BS])', txt)

        for i, (jam, arah) in enumerate(data):

            row_id = f"{jam}_{i}"
            self.row_state[row_id] = "ON"

            row = BoxLayout(size_hint_y=None, height=dp(50))

            label = Label(text=f"{jam} {arah}")
            btn = Button(text="ON")

            def cycle(b, rid=row_id):

                order = ["ON","K1","K2","K3","K4","K5","WIN","LOSS"]

                state = self.row_state[rid]
                idx = order.index(state) if state in order else 0
                idx = (idx + 1) % len(order)

                self.row_state[rid] = order[idx]
                b.text = order[idx]

            btn.bind(on_press=cycle)

            row.add_widget(label)
            row.add_widget(btn)
            self.list_box.add_widget(row)


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

        nav.add_widget(Button(text="HOME", on_press=lambda x: setattr(sm, "current", "home")))
        nav.add_widget(Button(text="MART", on_press=lambda x: setattr(sm, "current", "mart")))
        nav.add_widget(Button(text="TRADE", on_press=lambda x: webbrowser.open("https://stcbroker.id")))

        root.add_widget(nav)

        return root


if __name__ == "__main__":
    AppMain().run()
