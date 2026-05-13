import requests
import time
from datetime import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView


# =========================
# VPS API
# =========================
DATA_URL = "http://157.10.252.46:5000/signal"

Window.clearcolor = (0.05, 0.05, 0.07, 1)


# =========================
# CARD
# =========================
class Card(BoxLayout):

    def __init__(self, bg=(0.15, 0.15, 0.18, 1), border=(0.25, 0.25, 0.3, 1), radius=18, **kwargs):
        super().__init__(**kwargs)

        self.orientation = "vertical"
        self.padding = 15
        self.spacing = 10

        # ✅ FIX RESPONSIVE HEIGHT (PENTING)
        self.size_hint_y = None

        with self.canvas.before:
            self.bg_color = Color(*bg)
            self.rect = RoundedRectangle(radius=[radius])

        with self.canvas.after:
            self.line_color = Color(*border)
            self.line = Line(rounded_rectangle=(0, 0, 0, 0, radius), width=1.5)

        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

        self.line.rounded_rectangle = (
            self.x, self.y, self.width, self.height, 18
        )

    def set_bg(self, color):
        self.bg_color.rgba = color


# =========================
# HISTORY ROW
# =========================
class HistoryRow(Card):

    def __init__(self, text="-", color_type="empty", **kwargs):

        bg = (0.18, 0.18, 0.2, 1)

        if color_type == "buy":
            bg = (0.0, 0.55, 0.2, 1)
        elif color_type == "sell":
            bg = (0.65, 0.0, 0.0, 1)

        super().__init__(bg=bg, border=(0.3, 0.3, 0.35, 1), height=50, **kwargs)

        self.label = Label(
            text=text,
            font_size=14,
            color=(1, 1, 1, 1),
            halign="left",
            valign="middle"
        )

        self.label.bind(size=self.label.setter("text_size"))
        self.add_widget(self.label)


# =========================
# MAIN CONTENT
# =========================
class Content(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(
            orientation="vertical",
            spacing=8,
            padding=8
        )

        # ✅ FULL HEIGHT CONTROL (PENTING)
        self.size_hint_y = 1

        self.history_data = []

        # =========================
        # TOP BAR (FIX HEIGHT)
        # =========================
        self.topbar = Card(bg=(0.08, 0.12, 0.18, 1), border=(0.1, 0.5, 1, 1), height=80)
        self.topbar.size_hint_y = None

        self.title = Label(text="AI SIGNAL PRO", font_size=30, bold=True, color=(0.1, 0.7, 1, 1))
        self.topbar.add_widget(self.title)

        self.add_widget(self.topbar)

        # =========================
        # MARKET + CLOCK
        # =========================
        row = BoxLayout(orientation="horizontal", size_hint_y=None, height=70, spacing=8)

        self.market_card = Card(bg=(0.05, 0.12, 0.10, 1), border=(0.0, 1, 0.6, 1), height=70)
        self.market_label = Label(text="MARKET : CRYPTO IDX", font_size=16, color=(0.1, 1, 0.7, 1))
        self.market_card.add_widget(self.market_label)

        self.clock_card = Card(bg=(0.05, 0.10, 0.15, 1), border=(0.1, 0.7, 1, 1), height=70)
        self.clock_label = Label(text="00:00:00", font_size=18, color=(0, 1, 0.6, 1))
        self.clock_card.add_widget(self.clock_label)

        row.add_widget(self.market_card)
        row.add_widget(self.clock_card)
        self.add_widget(row)

        # =========================
        # SIGNAL CARD (BESAR)
        # =========================
        self.signal_card = Card(bg=(0.2, 0.2, 0.2, 1), border=(0.4, 0.4, 0.4, 1), height=180)

        self.signal_label = Label(text="LOADING", font_size=32, bold=True)
        self.signal_info = Label(text="WAIT SIGNAL", font_size=16)

        self.signal_card.add_widget(self.signal_label)
        self.signal_card.add_widget(self.signal_info)

        self.add_widget(self.signal_card)

        # =========================
        # ENTRY
        # =========================
        self.entry_card = Card(bg=(0.12, 0.12, 0.15, 1), border=(0.2, 0.6, 1, 1), height=70)

        self.entry_label = Label(text="ENTRY : -", font_size=18)
        self.entry_card.add_widget(self.entry_label)

        self.add_widget(self.entry_card)

        # =========================
        # HISTORY TITLE
        # =========================
        self.history_title = Label(
            text="HISTORY",
            size_hint_y=None,
            height=35,
            font_size=18
        )

        self.add_widget(self.history_title)

        # =========================
        # HISTORY LIST (FILL SPACE)
        # =========================
        self.history_box = BoxLayout(orientation="vertical", size_hint_y=None)
        self.history_box.bind(minimum_height=self.history_box.setter("height"))

        scroll = ScrollView()
        scroll.add_widget(self.history_box)

        # ✅ INI YANG BIKIN FULL LAYAR AMAN
        self.add_widget(scroll)

        self.history_rows = []

        for i in range(10):
            row = HistoryRow()
            self.history_rows.append(row)
            self.history_box.add_widget(row)

        # =========================
        # LOOP
        # =========================
        Clock.schedule_interval(self.update_clock, 1)
        Clock.schedule_interval(self.load_signal, 2)

    # =========================
    # CLOCK
    # =========================
    def update_clock(self, dt):
        self.clock_label.text = datetime.now().strftime("%H:%M:%S")

    # =========================
    # SIGNAL
    # =========================
    def load_signal(self, dt):

        try:
            r = requests.get(DATA_URL + "?t=" + str(time.time()), timeout=5)
            data = r.json()

            signal = data.get("signal", "WAITING")
            market = data.get("market", "CRYPTO IDX")
            entry_time = data.get("entry_time", "-")

            self.market_label.text = f"MARKET : {market}"

            if signal.upper() == "BUY":
                self.signal_card.set_bg((0.0, 0.75, 0.2, 1))
                self.signal_label.text = "BUY NOW"

            elif signal.upper() == "SELL":
                self.signal_card.set_bg((0.75, 0.0, 0.0, 1))
                self.signal_label.text = "SELL NOW"

        except:
            self.signal_label.text = "OFFLINE"


# =========================
# APP ROOT (FULL SCREEN FIX)
# =========================
class AISignalApp(App):

    def build(self):

        root = BoxLayout(orientation="vertical")

        # ✅ CONTENT FULL HEIGHT
        self.content = Content()
        self.content.size_hint_y = 1

        # NAVBAR FIX BOTTOM
        navbar = BoxLayout(size_hint_y=None, height=55)

        btn1 = Button(text="HOME")
        btn2 = Button(text="HISTORY")
        btn3 = Button(text="PROFILE")

        navbar.add_widget(btn1)
        navbar.add_widget(btn2)
        navbar.add_widget(btn3)

        root.add_widget(self.content)
        root.add_widget(navbar)

        return root


# =========================
# RUN
# =========================
if __name__ == "__main__":
    AISignalApp().run()
