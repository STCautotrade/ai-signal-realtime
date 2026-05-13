import requests
from datetime import datetime
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
        super().__init__(h=26, bg=(0.08,0.08,0.12,1))
        self.label = Label(text=text, font_size=dp(9))
        self.add_widget(self.label)


# =========================
# HOME
# =========================
class Home(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)

        root = BoxLayout(orientation="vertical", spacing=dp(5), padding=dp(6))

        # LOGO
        root.add_widget(Image(
            source=os.path.join(BASE_DIR, "file_00000000989c71fa995c0bb4f763659a.png"),
            size_hint_y=None,
            height=dp(140)
        ))

        # MARKET + CLOCK
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

        # SIGNAL
        self.signal = Card(h=120)

        self.signal_label = Label(text="MENUNGGU SIGNAL", font_size=dp(18))
        self.entry = Label(text="ENTRY : -", font_size=dp(12))
        self.status = Label(text="SYSTEM STANDBY", font_size=dp(10))

        self.signal.add_widget(self.signal_label)
        self.signal.add_widget(self.entry)
        self.signal.add_widget(self.status)

        root.add_widget(self.signal)

        # HISTORY TITLE
        root.add_widget(Label(text="HISTORY", size_hint_y=None, height=dp(20)))

        # ================= HISTORY SCROLL (INI FIX UTAMA) =================
        self.history_scroll = ScrollView(
            size_hint=(1, None),
            height=dp(220),   # BATAS BIAR TIDAK NUTUP MENU BAWAH
        )

        self.history_box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(2)
        )

        self.history_box.bind(minimum_height=self.history_box.setter("height"))

        self.history_scroll.add_widget(self.history_box)
        root.add_widget(self.history_scroll)

        self.add_widget(root)

        self.history = []

        Clock.schedule_interval(self.load, 2)
        Clock.schedule_interval(self.clock_update, 1)

    def clock_update(self, dt):
        self.clock_label.text = datetime.now().strftime("%H:%M:%S WIB")

    def load(self, dt):
        try:
            data = requests.get(DATA_URL, timeout=5).json()

            signal = data.get("signal", "WAITING").upper()
            entry = data.get("entry_time", "-")

            if signal == "BUY":
                self.signal.set_bg((0,0.7,0.3,1))
                self.signal_label.text = "BUY"
                self.entry.text = f"BUY {entry}"

            elif signal == "SELL":
                self.signal.set_bg((0.8,0.1,0.2,1))
                self.signal_label.text = "SELL"
                self.entry.text = f"SELL {entry}"

            else:
                self.signal.set_bg((0.1,0.1,0.15,1))
                self.signal_label.text = "WAITING"
                self.entry.text = "-"

            # ================= ADD HISTORY UNLIMITED =================
            text = f"{signal} | {entry}"

            if not self.history or self.history[0] != text:
                self.history.insert(0, text)

                row = HistoryRow(text)
                self.history_box.add_widget(row, index=0)

        except:
            self.signal_label.text = "OFFLINE"


# =========================
# MARTINGALE
# =========================
class Martingale(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)

        root = BoxLayout(orientation="vertical", padding=dp(8))

        self.base = 14000

        root.add_widget(Label(text="MARTINGALE", font_size=dp(14)))

        self.result = Label(font_size=dp(10))

        btn = Button(text="HITUNG", size_hint_y=None, height=dp(40))
        btn.bind(on_press=self.calc)

        root.add_widget(btn)
        root.add_widget(self.result)

        self.add_widget(root)

    def calc(self, instance):
        mults = [2, 2.5, 3, 4]

        out = ""
        for m in mults:
            val = self.base
            out += f"\nX{m}\n"
            for i in range(1, 11):
                val *= m
                out += f"K{i}: {int(val)}\n"

        self.result.text = out


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
