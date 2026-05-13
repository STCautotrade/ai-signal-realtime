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
from kivy.graphics import Color, RoundedRectangle, Line


DATA_URL = "http://157.10.252.46:5000/signal"
BASE_DIR = os.path.dirname(__file__)


# ================= NEON CARD =================
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


# ================= HISTORY ROW =================
class HistoryRow(Card):
    def __init__(self, text, t="empty", **kwargs):

        bg = (0.08,0.08,0.12,1)

        if t == "BUY":
            border = (0,1,0.4,0.4)
        elif t == "SELL":
            border = (1,0.2,0.2,0.4)
        else:
            border = (0.2,0.5,1,0.2)

        super().__init__(bg=bg, border=border, h=28, **kwargs)

        self.label = Label(
            text=text,
            font_size=dp(10),
            bold=True,
            color=(1,1,1,1)
        )
        self.add_widget(self.label)


# ================= DASHBOARD =================
class Dashboard(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", spacing=dp(6), padding=dp(6), **kwargs)

        # ================= LOGO =================
        logo_box = BoxLayout(size_hint_y=None, height=dp(140))

        self.logo = Image(
            source=os.path.join(BASE_DIR, "file_00000000989c71fa995c0bb4f763659a.png"),
            allow_stretch=True,
            keep_ratio=True,
            size_hint=(1, None),
            height=dp(120)
        )

        center = BoxLayout()
        center.add_widget(Label(size_hint_x=1))
        center.add_widget(self.logo)
        center.add_widget(Label(size_hint_x=1))

        logo_box.add_widget(center)
        self.add_widget(logo_box)

        # ================= MARKET + CLOCK (2 BOX NEON) =================
        row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(45), spacing=dp(6))

        self.market_box = Card(h=45)
        self.market = Label(text="MARKET : CRYPTO IDX 85%", font_size=dp(13), bold=True)
        self.market_box.add_widget(self.market)

        self.clock_box = Card(h=45)
        self.clock = Label(text="00:00:00 WIB", font_size=dp(13), bold=True)
        self.clock_box.add_widget(self.clock)

        row.add_widget(self.market_box)
        row.add_widget(self.clock_box)

        self.add_widget(row)

        # ================= SIGNAL =================
        self.signal_card = Card(h=120)

        self.signal_label = Label(
            text="MENUNGGU SIGNAL",
            font_size=dp(28),
            bold=True
        )

        self.entry_text = Label(text="ENTRY : -", font_size=dp(14), bold=True)
        self.status_text = Label(text="SYSTEM STANDBY", font_size=dp(12), bold=True)

        self.signal_card.add_widget(self.signal_label)
        self.signal_card.add_widget(self.entry_text)
        self.signal_card.add_widget(self.status_text)

        self.add_widget(self.signal_card)

        # ================= HISTORY =================
        self.add_widget(Label(text="HISTORY", size_hint_y=None, height=dp(30), bold=True))

        self.history_box = BoxLayout(orientation="vertical", spacing=dp(2))
        self.rows = []

        for i in range(10):
            r = HistoryRow("-", "empty")
            self.rows.append(r)
            self.history_box.add_widget(r)

        self.add_widget(self.history_box)

        self.history = []

        Clock.schedule_interval(self.load_signal, 2)
        Clock.schedule_interval(self.update_clock, 1)

    # ================= CLOCK =================
    def update_clock(self, dt):
        self.clock.text = datetime.now().strftime("%H:%M:%S WIB")

    # ================= LOAD SIGNAL =================
    def load_signal(self, dt):
        try:
            r = requests.get(DATA_URL, timeout=5)
            data = r.json()

            signal = data.get("signal", "WAITING").upper()
            entry_time = data.get("entry_time", "-")

            if signal == "BUY":
                self.signal_card.set_bg((0,0.8,0.3,1))
                self.signal_label.text = "ENTRY BUY"
                self.entry_text.text = f"ENTRY BUY DI JAM {entry_time}"
                self.status_text.text = "AI SIGNAL ACTIVE"
                self.add_history(f"BUY | {entry_time} | BERAKHIR", "BUY")

            elif signal == "SELL":
                self.signal_card.set_bg((1,0.1,0.2,1))
                self.signal_label.text = "ENTRY SELL"
                self.entry_text.text = f"ENTRY SELL DI JAM {entry_time}"
                self.status_text.text = "AI SIGNAL ACTIVE"
                self.add_history(f"SELL | {entry_time} | BERAKHIR", "SELL")

            else:
                self.signal_card.set_bg((0.1,0.1,0.15,1))
                self.signal_label.text = "MENUNGGU SIGNAL"
                self.entry_text.text = "ENTRY : -"
                self.status_text.text = "SYSTEM STANDBY"

            self.update_history_ui()

        except:
            self.signal_label.text = "OFFLINE"
            self.status_text.text = "SERVER ERROR"

    # ================= HISTORY =================
    def add_history(self, text, t):
        if not self.history or self.history[0]["text"] != text:
            self.history.insert(0, {"text": text, "type": t})

        self.history = self.history[:10]

    def update_history_ui(self):
        for i in range(10):
            if i < len(self.history):
                h = self.history[i]
                self.rows[i].label.text = h["text"]

                # TRANSPARAN HISTORY
                if h["type"] == "BUY":
                    self.rows[i].set_bg((0,1,0.4,0.12))
                else:
                    self.rows[i].set_bg((1,0.2,0.2,0.12))
            else:
                self.rows[i].label.text = "-"
                self.rows[i].set_bg((0.08,0.08,0.12,1))


# ================= APP =================
class AISignalApp(App):

    def open_trade(self, instance):
        webbrowser.open("https://stcbroker.id")

    def build(self):
        root = BoxLayout(orientation="vertical")

        scroll = ScrollView()
        scroll.add_widget(Dashboard())

        root.add_widget(scroll)

        nav = BoxLayout(size_hint_y=None, height=dp(55))

        nav.add_widget(Label(text="HOME"))
        nav.add_widget(Label(text="HISTORY"))

        btn = Button(text="TRADE", background_color=(0.08,0.08,0.1,1))
        btn.bind(on_press=self.open_trade)

        nav.add_widget(btn)

        root.add_widget(nav)

        return root


if __name__ == "__main__":
    AISignalApp().run()
