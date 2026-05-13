import requests
from datetime import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle, Line


DATA_URL = "http://157.10.252.46:5000/signal"

Window.clearcolor = (0.02, 0.02, 0.05, 1)


# =========================
# NEON CARD
# =========================
class Card(BoxLayout):

    def __init__(self, bg=(0.1,0.1,0.15,1), border=(0.2,0.7,1,1), h=120, **kwargs):
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
            self.line = Line(rounded_rectangle=(0,0,0,0,16), width=1.3)

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
            border = (0,1,0.4,1)
        elif t == "SELL":
            border = (1,0.1,0.2,1)
        else:
            border = (0.2,0.5,1,1)

        super().__init__(bg=bg, border=border, h=35, **kwargs)

        self.label = Label(
            text=text,
            font_size=dp(11),
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

        # ================= TITLE =================
        self.title = Label(
            text="AI SIGNAL PRO",
            font_size=dp(42),
            bold=True,
            color=(0.1,0.8,1,1),
            size_hint_y=None,
            height=dp(60)
        )
        self.add_widget(self.title)

        # ================= MARKET + TIME =================
        top = BoxLayout(size_hint_y=None, height=dp(50))

        self.market = Label(text="MARKET : CRYPTO IDX 85%", font_size=dp(16), bold=True)
        self.clock = Label(text="00:00:00 WIB", font_size=dp(18), bold=True)

        top.add_widget(self.market)
        top.add_widget(self.clock)

        self.add_widget(top)

        # ================= SIGNAL BOX =================
        self.signal_card = Card(h=130)

        self.signal = Label(
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

        self.status = Label(
            text="SYSTEM STANDBY",
            font_size=dp(14),
            bold=True
        )

        self.signal_card.add_widget(self.signal)
        self.signal_card.add_widget(self.entry_text)
        self.signal_card.add_widget(self.status)

        self.add_widget(self.signal_card)

        # ================= ENTRY DETAIL =================
        self.entry_detail = Label(
            text="",
            font_size=dp(18),
            bold=True,
            size_hint_y=None,
            height=dp(40)
        )
        self.add_widget(self.entry_detail)

        # ================= HISTORY TITLE =================
        self.history_title = Label(
            text="HISTORY",
            font_size=dp(22),
            bold=True,
            size_hint_y=None,
            height=dp(40)
        )
        self.add_widget(self.history_title)

        # ================= HISTORY 15 ROW =================
        self.history_box = BoxLayout(orientation="vertical", spacing=dp(2))

        self.rows = []
        for i in range(15):
            r = HistoryRow("-", "empty")
            self.rows.append(r)
            self.history_box.add_widget(r)

        self.add_widget(self.history_box)

        self.history = []

        Clock.schedule_interval(self.update_clock, 1)
        Clock.schedule_interval(self.load_signal, 2)

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
                self.signal.text = "ENTRY BUY"

                if self.expired(entry_time):
                    self.entry_text.text = "ENTRY CLOSED / EXPIRED"
                    self.status.text = "MENUNGGU SIGNAL"
                    self.entry_detail.text = ""
                else:
                    self.entry_text.text = f"ENTRY BUY DI JAM {entry_time}"
                    self.status.text = "AI SIGNAL ACTIVE"
                    self.entry_detail.text = "BUY SIGNAL ACTIVE"

                self.add_history(f"BUY | JAM {entry_time} | BERAKHIR", "BUY")

            # ================= SELL =================
            elif signal == "SELL":

                self.signal_card.set_bg((1,0.1,0.2,1))
                self.signal.text = "ENTRY SELL"

                if self.expired(entry_time):
                    self.entry_text.text = "ENTRY CLOSED / EXPIRED"
                    self.status.text = "MENUNGGU SIGNAL"
                    self.entry_detail.text = ""
                else:
                    self.entry_text.text = f"ENTRY SELL DI JAM {entry_time}"
                    self.status.text = "AI SIGNAL ACTIVE"
                    self.entry_detail.text = "SELL SIGNAL ACTIVE"

                self.add_history(f"SELL | JAM {entry_time} | BERAKHIR", "SELL")

            else:
                self.signal_card.set_bg((0.1,0.1,0.15,1))
                self.signal.text = "MENUNGGU SIGNAL"
                self.entry_text.text = "ENTRY : -"
                self.status.text = "SYSTEM STANDBY"
                self.entry_detail.text = ""

            self.update_history_ui()

        except:
            self.signal.text = "OFFLINE"
            self.status.text = "SERVER ERROR"

    # ================= HISTORY =================
    def add_history(self, text, t):
        if not self.history or self.history[0]["text"] != text:
            self.history.insert(0, {"text": text, "type": t})

        self.history = self.history[:15]

    def update_history_ui(self):
        for i in range(15):
            if i < len(self.history):
                h = self.history[i]
                self.rows[i].label.text = h["text"]

                if h["type"] == "BUY":
                    self.rows[i].set_bg((0,0.8,0.3,1))
                else:
                    self.rows[i].set_bg((1,0.1,0.2,1))
            else:
                self.rows[i].label.text = "-"
                self.rows[i].set_bg((0.08,0.08,0.12,1))


# =========================
# APP
# =========================
class AISignalApp(App):

    def build(self):

        root = BoxLayout(orientation="vertical")

        scroll = ScrollView()
        scroll.add_widget(Dashboard())

        root.add_widget(scroll)

        # ================= NAVBAR =================
        nav = BoxLayout(size_hint_y=None, height=dp(55))

        nav.add_widget(Label(text="HOME"))
        nav.add_widget(Label(text="HISTORY"))
        nav.add_widget(Label(text="TRADE"))

        root.add_widget(nav)

        return root


if __name__ == "__main__":
    AISignalApp().run()
