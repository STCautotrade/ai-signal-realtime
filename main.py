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
# CARD BASE
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
# HISTORY CARD
# =========================
class SignalHistoryCard(Card):
    def __init__(self, market, signal, entry):
        super().__init__(h=60)

        if signal == "BUY":
            self.set_bg((0, 1, 0, 0.25))
        else:
            self.set_bg((1, 0, 0, 0.25))

        self.add_widget(
            Label(
                text=f"{market} : SIGNAL {signal} JAM {entry} BERAKHIR",
                font_size=dp(12),
                bold=True
            )
        )


# =========================
# HOME SCREEN (UNCHANGED)
# =========================
class Home(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)

        root = BoxLayout(orientation="vertical", padding=0, spacing=0)

        root.add_widget(
            Image(
                source=os.path.join(BASE_DIR, "file_00000000989c71fa995c0bb4f763659a.png"),
                size_hint_y=None,
                height=dp(140),
                allow_stretch=True,
                keep_ratio=False
            )
        )

        top = BoxLayout(size_hint_y=None, height=dp(40))

        self.market = Card(h=40)
        self.clock = Card(h=40)

        self.market_label = Label(text="CRYPTO ID 85%", font_size=dp(12))
        self.clock_label = Label(text="00:00:00 WIB", font_size=dp(12))

        self.market.add_widget(self.market_label)
        self.clock.add_widget(self.clock_label)

        top.add_widget(self.market)
        top.add_widget(self.clock)

        root.add_widget(top)

        self.signal = Card(h=120)

        self.signal_title = Label(text="SIGNAL KONFIGURASI TRADE", font_size=dp(16), bold=True)
        self.signal_main = Label(text="WAITING....", font_size=dp(14))
        self.signal_status = Label(text="DETECTED", font_size=dp(12))

        self.signal.add_widget(self.signal_title)
        self.signal.add_widget(self.signal_main)
        self.signal.add_widget(self.signal_status)

        root.add_widget(self.signal)

        self.expire_label = Label(text="MENUNGGU SIGNAL", size_hint_y=None, height=dp(30))
        root.add_widget(self.expire_label)

        root.add_widget(Label(text="HISTORY", size_hint_y=None, height=dp(20)))

        self.history_scroll = ScrollView()

        self.history_box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(5)
        )

        self.history_box.bind(minimum_height=self.history_box.setter("height"))

        self.history_scroll.add_widget(self.history_box)
        root.add_widget(self.history_scroll)

        self.add_widget(root)

        self.expiry_time = None
        self.last_signal = ""

        Clock.schedule_interval(self.load, 2)
        Clock.schedule_interval(self.update_expiry, 1)

    def set_signal(self, mode, signal="", entry=""):
        if mode == "ACTIVE":
            self.signal.set_bg((0, 0.8, 0.3, 1) if signal == "BUY" else (1, 0.1, 0.2, 1))
            self.signal_main.text = f"ENTRY {signal} JAM {entry}"
        elif mode == "EXPIRED":
            self.signal.set_bg((0.2, 0.2, 0.2, 1))
            self.signal_main.text = "SIGNAL EXPIRED"
        else:
            self.signal.set_bg((0.1, 0.1, 0.15, 1))
            self.signal_main.text = "WAITING...."

    def update_expiry(self, dt):
        if not self.expiry_time:
            return

        if (self.expiry_time - datetime.now()).total_seconds() <= 0:
            self.expiry_time = None
            self.set_signal("EXPIRED")

    def load(self, dt):
        try:
            data = requests.get(DATA_URL, timeout=5).json()

            signal = data.get("signal", "WAITING").upper()
            entry = data.get("entry_time")

            if signal in ["BUY", "SELL"] and entry:
                key = f"{signal}_{entry}"

                if key != self.last_signal:
                    self.set_signal("ACTIVE", signal, entry)

                    self.expiry_time = datetime.now() + timedelta(minutes=1)
                    self.last_signal = key

                    self.history_box.add_widget(
                        SignalHistoryCard("CRYPTO IDX", signal, entry),
                        index=0
                    )
            else:
                self.set_signal("WAIT")

        except:
            self.set_signal("WAIT")


# =========================
# MARTINGALE (UPDATED ROW)
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

        self.input_box = BoxLayout(orientation="vertical")

        self.input = TextInput(size_hint_y=None, height=dp(120), font_size=dp(18))
        self.enter_btn = Button(text="ENTER", size_hint_y=None, height=dp(60))
        self.enter_btn.bind(on_press=self.parse)

        self.input_box.add_widget(self.input)
        self.input_box.add_widget(self.enter_btn)

        root.add_widget(self.input_box)

        self.list_container = BoxLayout(orientation="vertical")
        self.scroll = ScrollView()

        self.list_box = BoxLayout(
            orientation="vertical",
            size_hint_y=None
        )
        self.list_box.bind(minimum_height=self.list_box.setter("height"))

        self.scroll.add_widget(self.list_box)

        self.clear_btn = Button(text="HAPUS ALL", size_hint_y=None, height=dp(60))
        self.clear_btn.bind(on_press=self.reset_all)

        self.list_container.add_widget(self.scroll)
        self.list_container.add_widget(self.clear_btn)

        root.add_widget(self.list_container)

        self.list_container.opacity = 0
        self.list_container.disabled = True

        self.add_widget(root)

    def cycle_state(self, btn, key):

        order = ["ON", "WIN", "LOSS", "K1", "K2", "K3", "K4", "K5"]
        current = self.row_state[key]

        idx = order.index(current)
        idx = (idx + 1) % len(order)

        new_state = order[idx]
        self.row_state[key] = new_state

        btn.text = new_state

        if new_state == "WIN":
            btn.background_color = (0, 1, 0, 1)
        elif new_state == "LOSS":
            btn.background_color = (1, 0, 0, 1)
        else:
            btn.background_color = (0.3, 0.3, 0.3, 1)

        btn.color = (1, 1, 1, 1)

    def reset_all(self, instance):
        self.list_box.clear_widgets()
        self.row_state = {}

        self.list_container.opacity = 0
        self.list_container.disabled = True

        self.input_box.opacity = 1
        self.input_box.disabled = False

    def parse(self, instance):

        txt = self.input.text.upper()
        self.input.text = ""

        self.list_box.clear_widgets()

        data = re.findall(r'(\d{1,2}:\d{2})\s*([BS])', txt)

        for i, (jam, arah) in enumerate(data):

            row_id = f"{jam}_{i}"
            self.row_state[row_id] = "ON"

            row = Card(h=50)
            line = BoxLayout()

            # JAM
            line.add_widget(Label(text=jam, font_size=dp(20)))

            # B / S
            line.add_widget(Label(text=arah, font_size=dp(20)))

            # BOX WARNA
            box = Card(h=30, bg=(0,1,0,0.4) if arah == "B" else (1,0,0,0.4))
            line.add_widget(box)

            # BUTTON
            btn = Button(
                text="ON",
                background_color=(0.3,0.3,0.3,1),
                color=(1,1,1,1)
            )

            btn.bind(on_press=lambda b, k=row_id: self.cycle_state(b, k))

            line.add_widget(btn)

            row.add_widget(line)
            self.list_box.add_widget(row)

        self.input_box.opacity = 0
        self.input_box.disabled = True

        self.list_container.opacity = 1
        self.list_container.disabled = False


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
    AppMain().run()
