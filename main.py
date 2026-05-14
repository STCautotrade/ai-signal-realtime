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
        super().__init__(h=35, bg=(0.08,0.08,0.12,1))
        self.add_widget(Label(text=text, font_size=dp(12)))


# =========================
# HOME SCREEN
# =========================
class Home(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)

        root = BoxLayout(orientation="vertical", padding=0, spacing=0)

        # JUDUL PNG FULL ATAS
        root.add_widget(
            Image(
                source=os.path.join(BASE_DIR, "file_00000000989c71fa995c0bb4f763659a.png"),
                size_hint_y=None,
                height=dp(140),
                allow_stretch=True,
                keep_ratio=False
            )
        )

        # CRYPTO + CLOCK
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

        # SIGNAL BOX
        self.signal = Card(h=120)

        self.signal_title = Label(text="SIGNAL KONFIGURASI TRADE", font_size=dp(16), bold=True)
        self.signal_main = Label(text="WAITING....", font_size=dp(14))
        self.signal_status = Label(text="DETECTED", font_size=dp(12))

        self.signal.add_widget(self.signal_title)
        self.signal.add_widget(self.signal_main)
        self.signal.add_widget(self.signal_status)

        root.add_widget(self.signal)

        # EXPIRE
        self.expire_label = Label(text="MENUNGGU SIGNAL", size_hint_y=None, height=dp(30))
        root.add_widget(self.expire_label)

        # HISTORY FULL SCROLL
        root.add_widget(Label(text="HISTORY", size_hint_y=None, height=dp(20)))

        self.history_scroll = ScrollView()

        self.history_box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(3)
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
            self.signal_main.text = f"ENTRY {signal} DI JAM {entry} ~ ACTIVE"
            self.signal_status.text = "ACTIVE"

        elif mode == "EXPIRED":
            self.signal.set_bg((0.2, 0.2, 0.2, 1))
            self.signal_main.text = "SIGNAL EXPIRED"
            self.signal_status.text = "DETECTED"

        else:
            self.signal.set_bg((0.1, 0.1, 0.15, 1))
            self.signal_main.text = "AKTIVE ~ WAITING...."
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

    # =========================
    # FIXED LOAD LOGIC
    # =========================
    def load(self, dt):

        try:
            data = requests.get(DATA_URL, timeout=5).json()

            signal = data.get("signal", "WAITING").upper()
            entry = data.get("entry_time")

            if signal in ["BUY", "SELL"] and entry:

                key = f"{signal}_{entry}"

                # SIGNAL BARU SELALU BISA ACTIVE
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

            hist = f"{signal} | {entry if entry else '-'}"

            if not self.history or self.history[0] != hist:
                self.history.insert(0, hist)
                self.history_box.add_widget(HistoryRow(hist), index=0)

        except:
            self.set_signal("WAIT")
            self.expire_label.text = "SERVER ERROR"


# =========================
# MARTINGALE (FULL SCREEN FIX)
# =========================
class Martingale(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)

        self.row_state = {}

        root = BoxLayout(orientation="vertical", padding=0, spacing=5)

        self.header = Card(h=60)
        self.header_label = Label(text="SIGNAL VIP STC | -", font_size=dp(18), bold=True)
        self.header.add_widget(self.header_label)
        root.add_widget(self.header)

        # INPUT
        self.input_box = BoxLayout(orientation="vertical", spacing=5)

        self.input = TextInput(
            hint_text="Paste SIGNAL VIP",
            size_hint_y=None,
            height=dp(120),
            font_size=dp(18)
        )

        self.enter_btn = Button(text="ENTER", size_hint_y=None, height=dp(60))
        self.enter_btn.bind(on_press=self.parse)

        self.input_box.add_widget(self.input)
        self.input_box.add_widget(self.enter_btn)

        root.add_widget(self.input_box)

        # LIST MODE
        self.list_container = BoxLayout(orientation="vertical")

        self.scroll = ScrollView()

        self.list_box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=5
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

        now = datetime.now()
        self.header_label.text = f"SIGNAL VIP STC | {now.strftime('%d %b %Y')}"

        data = re.findall(r'(\d{1,2}:\d{2})\s*([BS])', txt)

        for i, (jam, arah) in enumerate(data):

            row_id = f"{jam}-{i}"
            self.row_state[row_id] = "ON"

            row = Card(h=60)
            line = BoxLayout(spacing=10, padding=10)

            line.add_widget(Label(text=jam, font_size=dp(24)))
            line.add_widget(Label(text=arah, font_size=dp(24)))

            btn = Button(text="ON", font_size=dp(18))

            def cycle(b, rid=row_id):

                state = self.row_state[rid]

                if state == "ON":
                    self.row_state[rid] = "WIN"
                    b.text = "WIN"
                    b.background_color = (0, 1, 0, 1)

                elif state == "WIN":
                    self.row_state[rid] = "LOSS"
                    b.text = "LOSS"
                    b.background_color = (1, 0, 0, 1)

                else:
                    self.row_state[rid] = "ON"
                    b.text = "ON"

            btn.bind(on_press=cycle)

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
