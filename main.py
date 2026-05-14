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
# HISTORY ROW
# =========================
class HistoryRow(Card):
    def __init__(self, text):
        super().__init__(h=30, bg=(0.08,0.08,0.12,1))
        self.add_widget(Label(text=text, font_size=dp(11)))


# =========================
# HOME
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
                height=dp(130),
                allow_stretch=True,
                keep_ratio=False
            )
        )

        # MARKET + CLOCK
        top = BoxLayout(size_hint_y=None, height=dp(40))

        self.market = Card(h=40)
        self.clock = Card(h=40)

        self.market_label = Label(text="CRYPTO ID 85%")
        self.clock_label = Label(text="00:00:00")

        self.market.add_widget(self.market_label)
        self.clock.add_widget(self.clock_label)

        top.add_widget(self.market)
        top.add_widget(self.clock)
        root.add_widget(top)

        # SIGNAL
        self.signal = Card(h=120)
        self.signal_title = Label(text="SIGNAL KONFIGURASI TRADE")
        self.signal_main = Label(text="WAITING...")
        self.signal_status = Label(text="DETECTED")

        self.signal.add_widget(self.signal_title)
        self.signal.add_widget(self.signal_main)
        self.signal.add_widget(self.signal_status)

        root.add_widget(self.signal)

        # EXPIRE
        self.expire_label = Label(text="MENUNGGU SIGNAL", size_hint_y=None, height=dp(25))
        root.add_widget(self.expire_label)

        # HISTORY TITLE
        root.add_widget(Label(text="HISTORY", size_hint_y=None, height=dp(20)))

        # HEADER 7 KOLOM
        header = BoxLayout(size_hint_y=None, height=dp(25))
        for t in ["SIGNAL","ENTRY","STATUS","K1","K2","K3","K4"]:
            header.add_widget(Label(text=t, font_size=dp(10)))
        root.add_widget(header)

        # SCROLL HISTORY
        self.scroll = ScrollView()
        self.box = BoxLayout(orientation="vertical", size_hint_y=None)
        self.box.bind(minimum_height=self.box.setter("height"))
        self.scroll.add_widget(self.box)
        root.add_widget(self.scroll)

        self.add_widget(root)

        self.expiry_time = None
        self.last_signal = ""

        Clock.schedule_interval(self.load, 2)
        Clock.schedule_interval(self.clock_update, 1)
        Clock.schedule_interval(self.update_expiry, 1)

    def clock_update(self, dt):
        self.clock_label.text = datetime.now().strftime("%H:%M:%S")

    def set_signal(self, mode, signal="", entry=""):

        if mode == "ACTIVE":
            self.signal.set_bg((0,0.8,0.3,1) if signal=="BUY" else (1,0.1,0.2,1))
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
            self.expire_label.text = "MENUNGGU SIGNAL"
            return

        remaining = int((self.expiry_time - datetime.now()).total_seconds())

        if remaining <= 0:
            self.expiry_time = None
            self.set_signal("EXPIRED")
            self.expire_label.text = "EXPIRED : 0"
            return

        self.expire_label.text = f"EXPIRED : {remaining}"

    def load(self, dt):

        try:
            data = requests.get(DATA_URL, timeout=5).json()

            signal = data.get("signal","WAIT").upper()
            entry = data.get("entry_time")

            if signal in ["BUY","SELL"] and entry:

                key = f"{signal}_{entry}"

                if key != self.last_signal:
                    self.set_signal("ACTIVE", signal, entry)

                    try:
                        h,m = map(int, entry.split(":"))
                        base = datetime.now().replace(hour=h, minute=m, second=0)
                        self.expiry_time = base + timedelta(minutes=1)
                    except:
                        self.expiry_time = datetime.now() + timedelta(seconds=60)

                    self.last_signal = key

            # HISTORY ONLY EXPIRED
            if signal == "EXPIRED":
                row = BoxLayout(size_hint_y=None, height=dp(25))

                row.add_widget(Label(text=signal))
                row.add_widget(Label(text=str(entry)))
                row.add_widget(Label(text="EXPIRED"))

                for _ in range(4):
                    row.add_widget(Label(text="-"))

                self.box.add_widget(row)

        except:
            self.set_signal("WAIT")


# =========================
# MART
# =========================
class Mart(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)

        self.state = {}
        self.input_mode = True

        root = BoxLayout(orientation="vertical")

        self.header = Label(text="SIGNAL VIP STC | -", size_hint_y=None, height=dp(40))
        root.add_widget(self.header)

        # INPUT
        self.input_box = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(160))

        self.input = TextInput(hint_text="Paste signal")
        self.btn = Button(text="ENTER")
        self.btn.bind(on_press=self.build_table)

        self.input_box.add_widget(self.input)
        self.input_box.add_widget(self.btn)

        root.add_widget(self.input_box)

        # TABLE
        self.scroll = ScrollView()
        self.box = BoxLayout(orientation="vertical", size_hint_y=None)
        self.box.bind(minimum_height=self.box.setter("height"))
        self.scroll.add_widget(self.box)

        self.clear = Button(text="HAPUS ALL", size_hint_y=None, height=dp(50))
        self.clear.bind(on_press=self.reset_all)

        root.add_widget(self.scroll)
        root.add_widget(self.clear)

        self.add_widget(root)

    def build_table(self, instance):

        txt = self.input.text.upper()
        self.header.text = "SIGNAL VIP STC | " + datetime.now().strftime("%d %b %Y")

        self.input_box.opacity = 0
        self.input_box.disabled = True

        data = re.findall(r'(\d{1,2}:\d{2})\s*([BS])', txt)

        for i,(jam,dir) in enumerate(data):

            rid = f"{jam}_{i}"
            self.state[rid] = "ON"

            row = BoxLayout(size_hint_y=None, height=dp(40))
            row.add_widget(Label(text=jam))
            row.add_widget(Label(text=dir))

            btn = Button(text="ON")

            def cycle(b, rid=rid):

                s = self.state[rid]

                if s=="ON":
                    self.state[rid]="K1"; b.text="K1"
                elif s=="K1":
                    self.state[rid]="K2"; b.text="K2"
                elif s=="K2":
                    self.state[rid]="K3"; b.text="K3"
                elif s=="K3":
                    self.state[rid]="K4"; b.text="K4"
                elif s=="K4":
                    self.state[rid]="K5"; b.text="K5"
                elif s=="K5":
                    self.state[rid]="WIN"; b.text="WIN"
                elif s=="WIN":
                    self.state[rid]="LOSS"; b.text="LOSS"
                else:
                    self.state[rid]="ON"; b.text="ON"

            btn.bind(on_press=cycle)
            row.add_widget(btn)

            self.box.add_widget(row)

    def reset_all(self, instance):

        self.box.clear_widgets()
        self.input.text = ""

        self.input_box.opacity = 1
        self.input_box.disabled = False


# =========================
# APP
# =========================
class AppMain(App):

    def build(self):

        sm = ScreenManager()

        sm.add_widget(Home(name="home"))
        sm.add_widget(Mart(name="mart"))

        root = BoxLayout(orientation="vertical")

        root.add_widget(sm)

        nav = BoxLayout(size_hint_y=None, height=dp(50))

        nav.add_widget(Button(text="HOME", on_press=lambda x: sm.current="home"))
        nav.add_widget(Button(text="MART", on_press=lambda x: sm.current="mart"))
        nav.add_widget(Button(text="TRADE", on_press=lambda x: webbrowser.open("https://stcbroker.id")))

        root.add_widget(nav)

        return root


if __name__ == "__main__":
    AppMain().run()
