import requests
from datetime import datetime
import webbrowser
import os

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics import Color, RoundedRectangle, Line


DATA_URL = "http://157.10.252.46:5000/signal"
Window.clearcolor = (0.02, 0.02, 0.05, 1)

BASE_DIR = os.path.dirname(__file__)


# =========================
# NEON CARD
# =========================
class Card(BoxLayout):
    def __init__(self, bg=(0.1,0.1,0.15,1), border=(0.2,0.7,1,1), h=100, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(6)
        self.spacing = dp(3)
        self.size_hint_y = None
        self.height = dp(h)

        with self.canvas.before:
            self.bg = Color(*bg)
            self.rect = RoundedRectangle(radius=[16])

        with self.canvas.after:
            self.border = Color(*border)
            self.line = Line(rounded_rectangle=(0,0,0,0,16), width=1.2)

        self.bind(pos=self.update, size=self.update)

    def update(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.line.rounded_rectangle = (*self.pos, *self.size, 16)

    def set_bg(self, c):
        self.bg.rgba = c


# =========================
# HISTORY ROW
# =========================
class HistoryRow(Card):
    def __init__(self, text, t="empty", **kwargs):
        border = (0.2,0.5,1,0.3)

        super().__init__(bg=(0.08,0.08,0.12,1), border=border, h=32, **kwargs)

        self.label = Label(
            text=text,
            font_size=dp(10),
            bold=True,
            color=(1,1,1,1)
        )
        self.add_widget(self.label)


# =========================
# MARTINGALE CALC
# =========================
class Martingale(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))

        self.input = Label(text="BASE : 14000", font_size=dp(18), bold=True)

        self.result = Label(text="", font_size=dp(14))

        self.calc = Button(text="CALCULATE", size_hint_y=None, height=dp(50))
        self.calc.bind(on_press=self.run_calc)

        root.add_widget(self.input)
        root.add_widget(self.calc)
        root.add_widget(self.result)

        self.add_widget(root)

    def run_calc(self, instance):
        base = 14000
        mults = [2, 2.5, 3, 4]

        out = ""
        for m in mults:
            out += f"\nMULT {m}\n"
            val = base
            for i in range(1, 11):
                val *= m
                out += f"K{i} = {int(val)}\n"

        self.result.text = out


# =========================
# DASHBOARD (HOME)
# =========================
class Dashboard(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.history = []

        root = BoxLayout(orientation="vertical", spacing=dp(6), padding=dp(6))

        # ================= LOGO =================
        logo = Image(
            source=os.path.join(BASE_DIR, "file_00000000989c71fa995c0bb4f763659a.png"),
            size_hint_y=None,
            height=dp(140)
        )
        root.add_widget(logo)

        # ================= MARKET + CLOCK (2 CARD 1 ROW) =================
        row = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(6))

        self.market = Card(h=60)
        self.clock = Card(h=60)

        self.market_label = Label(text="CRYPTO IDX 85%", font_size=dp(14))
        self.clock_label = Label(text="00:00:00 WIB", font_size=dp(14))

        self.market.add_widget(self.market_label)
        self.clock.add_widget(self.clock_label)

        row.add_widget(self.market)
        row.add_widget(self.clock)

        root.add_widget(row)

        # ================= SIGNAL =================
        self.signal_card = Card(h=120)

        self.signal_label = Label(text="MENUNGGU SIGNAL", font_size=dp(26), bold=True)
        self.entry_text = Label(text="ENTRY : -", font_size=dp(14))
        self.status_text = Label(text="SYSTEM", font_size=dp(14))

        self.signal_card.add_widget(self.signal_label)
        self.signal_card.add_widget(self.entry_text)
        self.signal_card.add_widget(self.status_text)

        root.add_widget(self.signal_card)

        # ================= HISTORY =================
        root.add_widget(Label(text="HISTORY", size_hint_y=None, height=dp(30)))

        self.box = BoxLayout(orientation="vertical", spacing=dp(2))

        self.rows = []
        for i in range(10):
            r = HistoryRow("-")
            self.rows.append(r)
            self.box.add_widget(r)

        root.add_widget(self.box)

        self.add_widget(root)

        Clock.schedule_interval(self.load, 2)
        Clock.schedule_interval(self.clock_update, 1)

    def clock_update(self, dt):
        self.clock_label.text = datetime.now().strftime("%H:%M:%S WIB")

    def expired(self, t):
        try:
            return datetime.now().strftime("%H:%M") > t
        except:
            return False

    def load(self, dt):
        try:
            data = requests.get(DATA_URL, timeout=5).json()

            signal = data.get("signal", "WAITING").upper()
            entry = data.get("entry_time", "-")

            if signal == "BUY":
                self.signal_card.set_bg((0,0.8,0.3,1))
                self.signal_label.text = "ENTRY BUY"
                self.entry_text.text = f"BUY {entry}"

            elif signal == "SELL":
                self.signal_card.set_bg((1,0.1,0.2,1))
                self.signal_label.text = "ENTRY SELL"
                self.entry_text.text = f"SELL {entry}"

            else:
                self.signal_card.set_bg((0.1,0.1,0.15,1))
                self.signal_label.text = "WAITING"
                self.entry_text.text = "-"

            self.history.insert(0, f"{signal} | {entry}")
            self.history = self.history[:10]

            for i in range(10):
                self.rows[i].label.text = self.history[i] if i < len(self.history) else "-"

        except:
            self.signal_label.text = "OFFLINE"


# =========================
# HISTORY SCREEN
# =========================
class History(Screen):
    def __init__(self, dashboard, **kwargs):
        super().__init__(**kwargs)

        self.dash = dashboard
        self.box = BoxLayout(orientation="vertical")

        self.box.add_widget(Label(text="HISTORY VIEW"))

        self.add_widget(self.box)


# =========================
# APP
# =========================
class AISignalApp(App):

    def build(self):

        self.sm = ScreenManager()

        self.home = Dashboard(name="home")
        self.history = History(self.home, name="history")
        self.martingale = Martingale(name="martingale")

        self.sm.add_widget(self.home)
        self.sm.add_widget(self.history)
        self.sm.add_widget(self.martingale)

        root = BoxLayout(orientation="vertical")

        root.add_widget(self.sm)

        nav = BoxLayout(size_hint_y=None, height=dp(55))

        btn_home = Button(text="HOME")
        btn_history = Button(text="HISTORY")
        btn_trade = Button(text="TRADE")
        btn_m = Button(text="MARTINGALE")

        btn_home.bind(on_press=lambda x: self.sm.switch_to(self.home))
        btn_history.bind(on_press=lambda x: self.sm.switch_to(self.history))
        btn_trade.bind(on_press=lambda x: webbrowser.open("https://stcbroker.id"))
        btn_m.bind(on_press=lambda x: self.sm.switch_to(self.martingale))

        nav.add_widget(btn_home)
        nav.add_widget(btn_history)
        nav.add_widget(btn_trade)
        nav.add_widget(btn_m)

        root.add_widget(nav)

        return root


if __name__ == "__main__":
    AISignalApp().run()
