import requests
import time
import webbrowser
from datetime import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.uix.scrollview import ScrollView


DATA_URL = "http://157.10.252.46:5000/signal"

Window.clearcolor = (0.05, 0.05, 0.07, 1)


# =========================
# CARD UI
# =========================
class Card(BoxLayout):
    def __init__(self, bg=(0.1,0.1,0.1,1), border=(0.3,0.3,0.3,1), radius=18, **kwargs):
        super().__init__(**kwargs)

        self.orientation = "vertical"
        self.padding = dp(10)
        self.spacing = dp(5)
        self.size_hint_y = None

        with self.canvas.before:
            self.bg = Color(*bg)
            self.rect = RoundedRectangle(radius=[radius])

        with self.canvas.after:
            self.border = Color(*border)
            self.line = Line(rounded_rectangle=(0,0,0,0,radius), width=1.2)

        self.bind(pos=self.update, size=self.update)

    def update(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.line.rounded_rectangle = (*self.pos, *self.size, 18)

    def set_bg(self, c):
        self.bg.rgba = c


# =========================
# HISTORY ROW
# =========================
class HistoryRow(Card):
    def __init__(self, text, t="empty", **kwargs):

        bg = (0.2,0.2,0.2,1)
        if t == "buy":
            bg = (0.0,0.7,0.2,1)
        elif t == "sell":
            bg = (0.8,0.1,0.1,1)

        super().__init__(bg=bg, height=dp(55), **kwargs)

        self.label = Label(
            text=text,
            font_size=dp(16),
            bold=True
        )

        self.add_widget(self.label)


# =========================
# HOME SCREEN
# =========================
class HomeScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(orientation="vertical", spacing=dp(5), padding=dp(6))

        # ================= TITLE =================
        self.title = Label(
            text="AI SIGNAL MODE",
            font_size=dp(42),
            bold=True,
            color=(0.2,0.8,1,1),
            size_hint_y=None,
            height=dp(70)
        )
        root.add_widget(self.title)

        # ================= MARKET + CLOCK =================
        top = BoxLayout(size_hint_y=None, height=dp(60))

        self.market = Label(text="MARKET : -", font_size=dp(18))
        self.clock = Label(text="00:00:00", font_size=dp(20), bold=True)

        top.add_widget(self.market)
        top.add_widget(self.clock)
        root.add_widget(top)

        # ================= SIGNAL =================
        self.signal = Label(
            text="WAITING",
            font_size=dp(34),
            bold=True,
            size_hint_y=None,
            height=dp(70)
        )

        self.info = Label(
            text="-",
            font_size=dp(16),
            size_hint_y=None,
            height=dp(40)
        )

        root.add_widget(self.signal)
        root.add_widget(self.info)

        # ================= ENTRY =================
        self.entry = Label(
            text="ENTRY : -",
            font_size=dp(20),
            size_hint_y=None,
            height=dp(50)
        )

        root.add_widget(self.entry)

        # ================= HISTORY =================
        self.history_box = BoxLayout(orientation="vertical")

        self.rows = []
        for i in range(8):
            r = HistoryRow("-")
            self.rows.append(r)
            self.history_box.add_widget(r)

        root.add_widget(self.history_box)

        self.add_widget(root)

        self.history = []

        Clock.schedule_interval(self.update_clock, 1)
        Clock.schedule_interval(self.load_signal, 2)

    # CLOCK
    def update_clock(self, dt):
        self.clock.text = datetime.now().strftime("%H:%M:%S WIB")

    # EXPIRED CHECK
    def expired(self, t):
        try:
            return datetime.now().strftime("%H:%M") > t
        except:
            return False

    # LOAD SIGNAL (SAFE)
    def load_signal(self, dt):
        try:
            r = requests.get(DATA_URL, timeout=5)

            if r.status_code != 200:
                return

            data = r.json()

            signal = data.get("signal", "WAITING")
            market = data.get("market", "-")
            entry_time = data.get("entry_time", "-")

            self.market.text = f"MARKET : {market}"

            if signal == "BUY":
                self.signal.text = "BUY NOW"
                self.signal.color = (0,1,0,1)

                self.entry.text = (
                    "ENTRY CLOSED" if self.expired(entry_time)
                    else f"BUY {entry_time}"
                )

                self.add_history(f"{market} | {entry_time} | BUY", "buy")

            elif signal == "SELL":
                self.signal.text = "SELL NOW"
                self.signal.color = (1,0,0,1)

                self.entry.text = (
                    "ENTRY CLOSED" if self.expired(entry_time)
                    else f"SELL {entry_time}"
                )

                self.add_history(f"{market} | {entry_time} | SELL", "sell")

            else:
                self.signal.text = "WAITING"
                self.signal.color = (1,1,1,1)
                self.entry.text = "-"

            self.update_history_ui()

        except:
            self.signal.text = "OFFLINE"
            self.info.text = "SERVER ERROR"

    # HISTORY ADD
    def add_history(self, text, t):
        if not self.history or self.history[0]["text"] != text:
            self.history.insert(0, {"text": text, "type": t})
        self.history = self.history[:8]

    # UPDATE HISTORY UI
    def update_history_ui(self):
        for i in range(8):
            if i < len(self.history):
                h = self.history[i]
                self.rows[i].label.text = h["text"]
                self.rows[i].set_bg((0,0.7,0.2,1) if h["type"]=="buy" else (0.8,0.1,0.1,1))
            else:
                self.rows[i].label.text = "-"
                self.rows[i].set_bg((0.2,0.2,0.2,1))


# =========================
# APP
# =========================
class AISignalApp(App):

    def build(self):

        self.sm = ScreenManager()

        self.home = HomeScreen(name="home")
        self.sm.add_widget(self.home)

        root = BoxLayout(orientation="vertical")

        root.add_widget(self.sm)

        # ================= NAVBAR =================
        nav = BoxLayout(size_hint_y=None, height=dp(60))

        btn_home = Button(text="HOME")

        btn_profile = Button(text="PROFILE")

        # PROFILE OPEN BROWSER (STABLE)
        btn_profile.bind(
            on_press=lambda x: webbrowser.open("https://stcbroker.id")
        )

        nav.add_widget(btn_home)
        nav.add_widget(Button(text="HISTORY"))
        nav.add_widget(btn_profile)

        root.add_widget(nav)

        return root


if __name__ == "__main__":
    AISignalApp().run()
