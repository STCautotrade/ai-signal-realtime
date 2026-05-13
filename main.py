import requests
from datetime import datetime
import webbrowser

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.graphics import Color, RoundedRectangle, Line


DATA_URL = "http://157.10.252.46:5000/signal"

Window.clearcolor = (0.02, 0.02, 0.05, 1)


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

        bg = (0.08,0.08,0.12,1)

        if t == "BUY":
            border = (0,1,0.4,0.5)
        elif t == "SELL":
            border = (1,0.2,0.2,0.5)
        else:
            border = (0.2,0.5,1,0.3)

        super().__init__(bg=bg, border=border, h=30, **kwargs)

        self.label = Label(
            text=text,
            font_size=dp(10),
            bold=True,
            color=(1,1,1,1)
        )

        self.add_widget(self.label)


# =========================
# DASHBOARD
# =========================
class Dashboard(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", spacing=dp(4), padding=dp(6), **kwargs)

        # ================= LOGO (PNG REPLACEMENT TITLE) =================
        logo_box = BoxLayout(
            size_hint_y=None,
            height=dp(110),
            padding=dp(10)
        )

        self.logo = Image(
            source="logo.png",
            allow_stretch=True,
            keep_ratio=True
        )

        logo_box.add_widget(self.logo)
        self.add_widget(logo_box)

        # ================= MARKET + CLOCK =================
        market_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(40),
            spacing=dp(10)
        )

        self.market = Label(
            text="MARKET : CRYPTO IDX 85%",
            font_size=dp(16),
            bold=True
        )

        self.clock = Label(
            text="00:00:00 WIB",
            font_size=dp(16),
            bold=True
        )

        market_row.add_widget(self.market)
        market_row.add_widget(self.clock)

        self.add_widget(market_row)

        # ================= SIGNAL CARD =================
        self.signal_card = Card(h=120)

        self.signal_label = Label(
            text="MENUNGGU SIGNAL",
            font_size=dp(30),
            bold=True,
            color=(1,1,1,1)
        )

        self.entry_text = Label(
            text="ENTRY : -",
            font_size=dp(16),
            bold=True
        )

        self.status_text = Label(
            text="SYSTEM STANDBY",
            font_size=dp(14),
            bold=True
        )

        self.signal_card.add_widget(self.signal_label)
        self.signal_card.add_widget(self.entry_text)
        self.signal_card.add_widget(self.status_text)

        self.add_widget(self.signal_card)

        # ================= HISTORY =================
        self.history_title = Label(
            text="HISTORY",
            font_size=dp(22),
            bold=True,
            size_hint_y=None,
            height=dp(40)
        )
        self.add_widget(self.history_title)

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

    # ================= EXPIRED =================
    def expired(self, t):
        try:
            return datetime.now().strftime("%H:%M") > t
        except:
            return False

    # ================= LOAD SIGNAL =================
    def load_signal(self, dt):
        try:
            r = requests.get(DATA_URL, timeout=5)
            data = r.json()

            signal = data.get("signal", "WAITING").upper()
            entry_time = data.get("entry_time", "-")

            # ================= BUY =================
            if signal == "BUY":

                self.signal_card.set_bg((0,0.8,0.3,1))
                self.signal_label.text = "ENTRY BUY"

                if self.expired(entry_time):
                    self.entry_text.text = "ENTRY CLOSED / EXPIRED"
                    self.status_text.text = "MENUNGGU SIGNAL"
                else:
                    self.entry_text.text = f"ENTRY BUY DI JAM {entry_time}"
                    self.status_text.text = "AI SIGNAL ACTIVE"

                self.add_history(f"BUY | {entry_time} | BERAKHIR", "BUY")

            # ================= SELL =================
            elif signal == "SELL":

                self.signal_card.set_bg((1,0.1,0.2,1))
                self.signal_label.text = "ENTRY SELL"

                if self.expired(entry_time):
                    self.entry_text.text = "ENTRY CLOSED / EXPIRED"
                    self.status_text.text = "MENUNGGU SIGNAL"
                else:
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

                # HISTORY TRANSPARAN (TIDAK IKUT SIGNAL UTAMA)
                if h["type"] == "BUY":
                    self.rows[i].set_bg((0, 1, 0.4, 0.15))
                else:
                    self.rows[i].set_bg((1, 0.2, 0.2, 0.15))
            else:
                self.rows[i].label.text = "-"
                self.rows[i].set_bg((0.08,0.08,0.12,1))


# =========================
# APP
# =========================
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

        btn_trade = Button(
            text="TRADE",
            font_size=dp(14),
            background_color=(0.08,0.08,0.1,1)
        )
        btn_trade.bind(on_press=self.open_trade)

        nav.add_widget(btn_trade)

        root.add_widget(nav)

        return root


if __name__ == "__main__":
    AISignalApp().run()
