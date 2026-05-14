import requests
from datetime import datetime, timedelta
import webbrowser
import os

from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
import re
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
# HISTORY
# =========================
class HistoryRow(Card):

    def __init__(self, text):
        super().__init__(h=30, bg=(0.08,0.08,0.12,1))

        self.label = Label(text=text, font_size=dp(9))
        self.add_widget(self.label)


# =========================
# HOME
# =========================
class Home(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)

        root = BoxLayout(
            orientation="vertical",
            spacing=dp(5),
            padding=dp(6)
        )

        root.add_widget(
            Image(
                source=os.path.join(BASE_DIR, "file_00000000989c71fa995c0bb4f763659a.png"),
                size_hint_y=None,
                height=dp(140)
            )
        )

        row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(5))

        self.market = Card(h=50)
        self.clock = Card(h=50)

        self.market_label = Label(text="CRYPTO IDX 85%", font_size=dp(11))
        self.clock_label = Label(text="00:00:00 WIB", font_size=dp(11))

        self.market.add_widget(self.market_label)
        self.clock.add_widget(self.clock_label)

        row.add_widget(self.market)
        row.add_widget(self.clock)

        root.add_widget(row)

# ================= SIGNAL (FIXED ONLY PART) =================
self.signal = Card(h=120)

self.signal_title = Label(
    text="SIGNAL KONFIGURASI TRADE",
    font_size=dp(18),
    bold=True
)

self.entry = Label(
    text="SIGNAL EXPIRED",
    font_size=dp(14)
)

self.status = Label(
    text="DETECTED",
    font_size=dp(11)
)

self.signal.add_widget(self.signal_title)
self.signal.add_widget(self.entry)
self.signal.add_widget(self.status)

root.add_widget(self.signal)


# ================= EXPIRE =================
self.expire_card = Card(h=70, bg=(0.08,0.08,0.12,1))

self.expire_label = Label(
    text="WAITING SIGNAL...",
    font_size=dp(22),
    bold=True
)

self.expire_card.add_widget(self.expire_label)
root.add_widget(self.expire_card)


# ================= HISTORY =================
root.add_widget(
    Label(text="HISTORY", size_hint_y=None, height=dp(20))
)

self.history_scroll = ScrollView(size_hint=(1, None), height=dp(220))

self.history_box = BoxLayout(
    orientation="vertical",
    spacing=dp(2),
    size_hint_y=None
)

self.history_box.bind(minimum_height=self.history_box.setter("height"))

self.history_scroll.add_widget(self.history_box)
root.add_widget(self.history_scroll)

self.add_widget(root)


# ================= VAR =================
self.history = []
self.expiry_time = None
self.last_signal = ""


Clock.schedule_interval(self.load, 2)
Clock.schedule_interval(self.clock_update, 1)
Clock.schedule_interval(self.update_expiry, 1)


# ================= CLOCK =================
def clock_update(self, dt):
    self.clock_label.text = datetime.now().strftime("%H:%M:%S WIB")


# ================= EXPIRY =================
def update_expiry(self, dt):

    if not self.expiry_time:
        self.expire_label.text = "MENUNGGU SIGNAL BERIKUTNYA"
        return

    remaining = int((self.expiry_time - datetime.now()).total_seconds())

    if remaining < 0:
        remaining = 0

    self.expire_label.text = f"EXPIRED : {remaining} DETIK"

    if remaining == 0:
        self.expiry_time = None


# ================= LOAD SIGNAL (FIXED FLOW) =================
def load(self, dt):

    try:
        data = requests.get(DATA_URL, timeout=5).json()

        signal = data.get("signal", "WAITING").upper()
        entry = data.get("entry_time")

        signal_key = None

        # ================= BUY =================
        if signal == "BUY" and entry:

            self.signal.set_bg((0, 0.8, 0.3, 1))
            self.entry.text = f"ENTRY BUY DI JAM {entry}"
            self.status.text = "ACTIVE"

            signal_key = f"BUY_{entry}"

        # ================= SELL =================
        elif signal == "SELL" and entry:

            self.signal.set_bg((1, 0.1, 0.2, 1))
            self.entry.text = f"ENTRY SELL DI JAM {entry}"
            self.status.text = "ACTIVE"

            signal_key = f"SELL_{entry}"

        # ================= WAITING / INVALID =================
        else:

            self.signal.set_bg((0.1, 0.1, 0.15, 1))
            self.entry.text = "SIGNAL EXPIRED"
            self.status.text = "DETECTED"

            self.expiry_time = None
            self.last_signal = ""
            signal_key = None

        # ================= EXPIRY SET (ONLY VALID SIGNAL) =================
        if signal_key and signal_key != self.last_signal:

            try:
                h, m = map(int, entry.split(":"))

                base_time = datetime.now().replace(
                    hour=h,
                    minute=m,
                    second=0
                )

                self.expiry_time = base_time + timedelta(minutes=1)

            except:
                self.expiry_time = datetime.now() + timedelta(seconds=60)

            self.last_signal = signal_key

        # ================= HISTORY (STABLE) =================
        hist = f"{signal} | JAM {entry if entry else '-'}"

        if not self.history or self.history[0] != hist:

            self.history.insert(0, hist)

            self.history_box.add_widget(
                HistoryRow(hist),
                index=0
            )

    except:

        self.entry.text = "OFFLINE"
        self.status.text = "SERVER ERROR"


# =========================
# MARTINGALE (UNCHANGED)
# =========================
class Martingale(Screen):

    def __init__(self, **kw):

        super().__init__(**kw)

        self.row_state = {}

        root = BoxLayout(
            orientation="vertical",
            padding=dp(6),
            spacing=dp(6)
        )

        # ================= HEADER =================
        self.header = Card(h=60)

        self.header_label = Label(
            text="SIGNAL VIP STC | -",
            font_size=dp(14),
            bold=True
        )

        self.header.add_widget(self.header_label)
        root.add_widget(self.header)

        # ================= INPUT =================
        self.input = TextInput(
            hint_text="Paste SIGNAL VIP di sini...",
            multiline=True,
            size_hint_y=None,
            height=dp(120)
        )

        root.add_widget(self.input)

        # ================= ENTER BUTTON =================
        btn = Button(
            text="ENTER",
            size_hint_y=None,
            height=dp(45)
        )

        btn.bind(on_press=self.parse)
        root.add_widget(btn)

        # ================= SCROLL =================
        scroll = ScrollView()

        self.listbox = BoxLayout(
            orientation="vertical",
            spacing=dp(2),
            padding=dp(2),
            size_hint_y=None
        )

        self.listbox.bind(minimum_height=self.listbox.setter("height"))

        scroll.add_widget(self.listbox)
        root.add_widget(scroll)

        # ================= CLEAR BUTTON =================
        self.clear_btn = Button(
            text="HAPUS DATA",
            size_hint_y=None,
            height=dp(45),
            background_normal=""
        )

        self.clear_btn.bind(on_press=self.clear_data)
        root.add_widget(self.clear_btn)

        self.add_widget(root)

    # ================= CLEAR ALL DATA =================
    def clear_data(self, instance):

        self.listbox.clear_widgets()
        self.row_state = {}
        self.input.text = ""

        self.header_label.text = "SIGNAL VIP STC | -"
        self.input.focus = True

    # ================= PARSE SIGNAL =================
    def parse(self, instance):

        self.listbox.clear_widgets()

        now = datetime.now()
        self.header_label.text = f"SIGNAL VIP STC | {now.strftime('%a, %d %b %Y')}"

        txt = self.input.text.upper()
        self.input.text = ""

        data = re.findall(r'(\d{1,2}:\d{2})\s*([BS])', txt)

        for i, (jam, arah) in enumerate(data):

            row_id = f"{jam}-{i}"
            self.row_state[row_id] = "ON"

            row = Card(h=28)

            line = BoxLayout(
                spacing=dp(2),
                padding=dp(2)
            )

            # ================= JAM =================
            line.add_widget(
                Label(
                    text=jam,
                    size_hint_x=.3,
                    font_size=dp(9)
                )
            )

            # ================= ARAH =================
            line.add_widget(
                Label(
                    text=arah,
                    size_hint_x=.15,
                    font_size=dp(9)
                )
            )

            # ================= COLOR BOX =================
            kotak = Button(
                text="",
                size_hint_x=.1,
                background_normal=""
            )

            kotak.background_color = (0, 1, 0, 1) if arah == "B" else (1, 0, 0, 1)

            line.add_widget(kotak)

            # ================= TOGGLE ON -> WIN -> LOSS =================
            btn = Button(
                text="ON",
                size_hint_x=.25,
                font_size=dp(9),
                background_normal=""
            )

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
                    b.background_color = (0.2, 0.2, 0.2, 1)

            btn.bind(on_press=cycle)

            line.add_widget(btn)

            # ================= DELETE ROW =================
            delete = Button(
                text="X",
                size_hint_x=.1,
                font_size=dp(9)
            )

            def remove_row(widget_row=row):
                self.listbox.remove_widget(widget_row)

            delete.bind(on_press=remove_row)

            line.add_widget(delete)

            row.add_widget(line)
            self.listbox.add_widget(row)


# =========================
# APP
# =========================
class AppMain(App):

    def build(self):

        sm = ScreenManager()

        home = Home(name="home")
        mart = Martingale(name="mart")

        sm.add_widget(home)
        sm.add_widget(mart)

        root = BoxLayout(orientation="vertical")

        root.add_widget(sm)

        nav = BoxLayout(size_hint_y=None, height=dp(50))

        nav.add_widget(Button(text="HOME", on_press=lambda x: sm.switch_to(home)))
        nav.add_widget(Button(text="MART", on_press=lambda x: sm.switch_to(mart)))
        nav.add_widget(Button(text="TRADE", on_press=lambda x: webbrowser.open("https://stcbroker.id")))

        root.add_widget(nav)

        return root


if __name__ == "__main__":
    AppMain().run()
