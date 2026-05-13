import requests
import time
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

# WEBVIEW
from kivy.garden.webview import WebView


DATA_URL = "http://157.10.252.46:5000/signal"

Window.clearcolor = (0.05, 0.05, 0.07, 1)


# =========================
# CARD UI
# =========================
class Card(BoxLayout):
    def __init__(self, bg=(0.1,0.1,0.1,1), border=(0.3,0.3,0.3,1), radius=20, **kwargs):
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
        self.line.rounded_rectangle = (*self.pos, *self.size, 20)

    def set_bg(self, c):
        self.bg.rgba = c


# =========================
# HISTORY ROW
# =========================
class HistoryRow(Card):
    def __init__(self, text, color_type="empty", **kwargs):

        bg = (0.2,0.2,0.2,1)
        if color_type == "buy":
            bg = (0.0,0.7,0.2,1)
        elif color_type == "sell":
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

        root = BoxLayout(orientation="vertical", spacing=dp(6), padding=dp(6))

        # ================= TITLE =================
        self.title = Label(
            text="AI SIGNAL MODE",
            font_size=dp(40),
            bold=True,
            color=(0.2,0.8,1,1),
            size_hint_y=None,
            height=dp(70)
        )
        root.add_widget(self.title)

        # ================= MARKET + CLOCK =================
        top = BoxLayout(size_hint_y=None, height=dp(70), spacing=dp(6))

        self.market = Label(text="MARKET : CRYPTO IDX", font_size=dp(18))
        self.clock = Label(text="00:00:00", font_size=dp(22), bold=True)

        top.add_widget(self.market)
        top.add_widget(self.clock)
        root.add_widget(top)

        # ================= SIGNAL =================
        self.signal = Label(text="WAITING", font_size=dp(36), bold=True, size_hint_y=None, height=dp(80))
        self.info = Label(text="-", font_size=dp(18), size_hint_y=None, height=dp(40))

        root.add_widget(self.signal)
        root.add_widget(self.info)

        # ================= ENTRY =================
        self.entry = Label(text="ENTRY : -", font_size=dp(20), size_hint_y=None, height=dp(50))
        root.add_widget(self.entry)

        # ================= HISTORY =================
        self.history_box = BoxLayout(orientation="vertical")

        self.rows = []
        for i in range(8):
            r = HistoryRow("-", "empty")
            self.rows.append(r)
            self.history_box.add_widget(r)

        root.add_widget(self.history_box)

        self.add_widget(root)

        Clock.schedule_interval(self.update_clock, 1)
        Clock.schedule_interval(self.load_signal, 2)

        self.history = []

    # CLOCK
    def update_clock(self, dt):
        self.clock.text = datetime.now().strftime("%H:%M:%S WIB")

    # EXPIRED
    def expired(self, t):
        try:
            return datetime.now().strftime("%H:%M") > t
        except:
            return False

    # LOAD SIGNAL
    def load_signal(self, dt):
        try:
            r = requests.get(DATA_URL, timeout=5)
            data = r.json()

            signal = data.get("signal", "WAITING")
            market = data.get("market", "-")
            entry_time = data.get("entry_time", "-")

            self.market.text = f"MARKET : {market}"

            if signal == "BUY":
                self.signal.text = "BUY NOW"
                self.signal.color = (0,1,0,1)

                self.entry.text = "ENTRY CLOSED" if self.expired(entry_time) else f"BUY {entry_time}"

                item = f"{market} | {entry_time} | BUY"
                self.add_history(item, "buy")

            elif signal == "SELL":
                self.signal.text = "SELL NOW"
                self.signal.color = (1,0,0,1)

                self.entry.text = "ENTRY CLOSED" if self.expired(entry_time) else f"SELL {entry_time}"

                item = f"{market} | {entry_time} | SELL"
                self.add_history(item, "sell")

            else:
                self.signal.text = "WAITING"
                self.signal.color = (1,1,1,1)
                self.entry.text = "-"

            self.update_history_ui()

        except:
            self.signal.text = "OFFLINE"

    def add_history(self, text, t):
        if not self.history or self.history[0]["text"] != text:
            self.history.insert(0, {"text": text, "type": t})
        self.history = self.history[:8]

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
# WEB SCREEN
# =========================
class WebScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation="vertical")

        self.web = WebView(
            url="https://stcbtoker.id"
        )

        layout.add_widget(self.web)
        self.add_widget(layout)


# =========================
# APP
# =========================
class AppMain(App):

    def build(self):

        self.sm = ScreenManager()

        self.home = HomeScreen(name="home")
        self.web = WebScreen(name="web")

        self.sm.add_widget(self.home)
        self.sm.add_widget(self.web)

        # NAVBAR FIXED
        root = BoxLayout(orientation="vertical")

        root.add_widget(self.sm)

        nav = BoxLayout(size_hint_y=None, height=dp(60))

        btn1 = Button(text="HOME")
        btn2 = Button(text="HISTORY")
        btn3 = Button(text="PROFILE")

        btn1.bind(on_press=lambda x: self.sm.switch_to(self.home))
        btn3.bind(on_press=lambda x: self.sm.switch_to(self.web))

        nav.add_widget(btn1)
        nav.add_widget(btn2)
        nav.add_widget(btn3)

        root.add_widget(nav)

        return root


if __name__ == "__main__":
    AppMain().run()
