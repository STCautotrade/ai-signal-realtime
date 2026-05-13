import requests
import time
import random
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

    def __init__(
        self,
        bg=(0.15, 0.15, 0.18, 1),
        border=(0.25, 0.25, 0.3, 1),
        **kwargs
    ):

        super().__init__(**kwargs)

        self.orientation = "vertical"
        self.padding = 15
        self.spacing = 10
        self.size_hint_y = None

        with self.canvas.before:

            self.bg_color = Color(*bg)

            self.rect = RoundedRectangle(
                radius=[18]
            )

        with self.canvas.after:

            self.line_color = Color(*border)

            self.line = Line(
                rounded_rectangle=(0, 0, 0, 0, 18),
                width=1.3
            )

        self.bind(pos=self.update_canvas)
        self.bind(size=self.update_canvas)

    def update_canvas(self, *args):

        self.rect.pos = self.pos
        self.rect.size = self.size

        self.line.rounded_rectangle = (
            self.x,
            self.y,
            self.width,
            self.height,
            18
        )

    def set_bg(self, color):

        self.bg_color.rgba = color


# =========================
# TECH TEXT ANIMATION
# =========================
class TechAnimation(Card):

    def __init__(self, **kwargs):

        super().__init__(
            bg=(0.08, 0.10, 0.13, 1),
            border=(0.1, 0.6, 1, 1),
            height=80,
            **kwargs
        )

        self.tech_label = Label(
            text="◉ SYSTEM ACTIVE ◉",
            font_size=20,
            bold=True,
            color=(0.1, 0.8, 1, 1)
        )

        self.add_widget(self.tech_label)

        self.frames = [
            "◉ SYSTEM ACTIVE ◉",
            "◉◉ SYSTEM ACTIVE ◉◉",
            "◉◉◉ SYSTEM ACTIVE ◉◉◉",
            "◉◉ SYSTEM ACTIVE ◉◉"
        ]

        self.index = 0

        Clock.schedule_interval(
            self.animate,
            0.3
        )

    def animate(self, dt):

        self.tech_label.text = self.frames[self.index]

        self.index += 1

        if self.index >= len(self.frames):
            self.index = 0


# =========================
# GRAPH TEXT ANIMATION
# =========================
class GraphAnimation(Card):

    def __init__(self, **kwargs):

        super().__init__(
            bg=(0.08, 0.10, 0.13, 1),
            border=(0.1, 1, 0.5, 1),
            height=100,
            **kwargs
        )

        self.graph_label = Label(
            text="▁▂▃▄▅▆▇",
            font_size=28,
            bold=True,
            color=(0, 1, 0.5, 1)
        )

        self.add_widget(self.graph_label)

        self.frames = [
            "▁▂▃▄▅▆▇",
            "▂▃▄▅▆▇█",
            "▄▅▆▇█▆▅",
            "▇█▆▅▄▃▂",
            "█▇▆▅▄▃▂"
        ]

        self.index = 0

        Clock.schedule_interval(
            self.animate,
            0.4
        )

    def animate(self, dt):

        self.graph_label.text = self.frames[self.index]

        self.index += 1

        if self.index >= len(self.frames):
            self.index = 0


# =========================
# MAIN CONTENT
# =========================
class Content(BoxLayout):

    def __init__(self, **kwargs):

        super().__init__(
            orientation="vertical",
            spacing=12,
            padding=10,
            size_hint_y=None,
            **kwargs
        )

        self.bind(
            minimum_height=self.setter("height")
        )

        self.history_data = []

        # =========================
        # TOP BAR
        # =========================
        self.topbar = Card(
            bg=(0.08, 0.12, 0.18, 1),
            border=(0.1, 0.5, 1, 1),
            height=90
        )

        self.title = Label(
            text="AI SIGNAL PRO",
            font_size=38,
            bold=True,
            color=(0.1, 0.7, 1, 1)
        )

        self.topbar.add_widget(self.title)

        self.add_widget(self.topbar)

        # =========================
        # MARKET + CLOCK
        # =========================
        row = BoxLayout(
            orientation="horizontal",
            spacing=10,
            size_hint_y=None,
            height=80
        )

        # MARKET
        self.market_card = Card(height=80)

        self.market_label = Label(
            text="MARKET : -",
            font_size=20,
            bold=True,
            color=(1, 1, 1, 1)
        )

        self.market_card.add_widget(
            self.market_label
        )

        # CLOCK
        self.clock_card = Card(height=80)

        self.clock_label = Label(
            text="00:00:00",
            font_size=24,
            bold=True,
            color=(0, 1, 0.6, 1)
        )

        self.clock_card.add_widget(
            self.clock_label
        )

        row.add_widget(self.market_card)
        row.add_widget(self.clock_card)

        self.add_widget(row)

        # =========================
        # BIG SIGNAL CARD
        # =========================
        self.signal_card = Card(
            bg=(0.2, 0.2, 0.2, 1),
            border=(0.4, 0.4, 0.4, 1),
            height=240
        )

        self.signal_label = Label(
            text="SEDANG KONFIGURASI",
            font_size=42,
            bold=True,
            color=(1, 1, 1, 1)
        )

        self.signal_info = Label(
            text="MENUNGGU SIGNAL",
            font_size=18,
            color=(1, 1, 1, 1)
        )

        self.signal_card.add_widget(
            self.signal_label
        )

        self.signal_card.add_widget(
            self.signal_info
        )

        self.add_widget(self.signal_card)

        # =========================
        # ENTRY CARD
        # =========================
        self.entry_card = Card(height=90)

        self.entry_label = Label(
            text="ENTRY : -",
            font_size=24,
            bold=True,
            color=(1, 1, 1, 1)
        )

        self.entry_card.add_widget(
            self.entry_label
        )

        self.add_widget(self.entry_card)

        # =========================
        # TECHNOLOGY ANIMATION
        # =========================
        self.tech_animation = TechAnimation()

        self.add_widget(self.tech_animation)

        # =========================
        # GRAPH ANIMATION
        # =========================
        self.graph_animation = GraphAnimation()

        self.add_widget(self.graph_animation)

        # =========================
        # HISTORY CARD
        # =========================
        self.history_card = Card(
            height=250,
            border=(0.25, 0.25, 0.35, 1)
        )

        self.history_label = Label(
            text="HISTORY SIGNAL\n-",
            font_size=18,
            halign="left",
            valign="top",
            color=(1, 1, 1, 1)
        )

        self.history_label.bind(
            size=self.history_label.setter(
                "text_size"
            )
        )

        self.history_card.add_widget(
            self.history_label
        )

        self.add_widget(self.history_card)

        # =========================
        # LOOP
        # =========================
        Clock.schedule_interval(
            self.update_clock,
            1
        )

        Clock.schedule_interval(
            self.load_signal,
            2
        )

    # =========================
    # CLOCK
    # =========================
    def update_clock(self, dt):

        self.clock_label.text = datetime.now().strftime(
            "%H:%M:%S"
        )

    # =========================
    # LOAD SIGNAL
    # =========================
    def load_signal(self, dt):

        try:

            r = requests.get(
                DATA_URL + "?t=" + str(time.time()),
                timeout=5
            )

            data = r.json()

            signal = data.get(
                "signal",
                "WAITING"
            )

            market = data.get(
                "market",
                "-"
            )

            entry_time = data.get(
                "entry_time",
                "-"
            )

            self.market_label.text = (
                f"MARKET : {market}"
            )

            # =========================
            # BUY
            # =========================
            if signal.upper() == "BUY":

                self.signal_card.set_bg(
                    (0.0, 0.75, 0.2, 1)
                )

                self.signal_label.text = "BUY NOW"

                self.signal_info.text = (
                    "AI SIGNAL ACTIVE"
                )

                self.entry_label.text = (
                    f"ENTRY BUY DI JAM {entry_time}"
                )

                if len(self.history_data) == 0 or \
                   self.history_data[0] != f"BUY - {entry_time}":

                    self.history_data.insert(
                        0,
                        f"BUY - {entry_time}"
                    )

            # =========================
            # SELL
            # =========================
            elif signal.upper() == "SELL":

                self.signal_card.set_bg(
                    (0.85, 0.0, 0.0, 1)
                )

                self.signal_label.text = "SELL NOW"

                self.signal_info.text = (
                    "AI SIGNAL ACTIVE"
                )

                self.entry_label.text = (
                    f"ENTRY SELL DI JAM {entry_time}"
                )

                if len(self.history_data) == 0 or \
                   self.history_data[0] != f"SELL - {entry_time}":

                    self.history_data.insert(
                        0,
                        f"SELL - {entry_time}"
                    )

            # =========================
            # WAITING
            # =========================
            else:

                self.signal_card.set_bg(
                    (0.2, 0.2, 0.2, 1)
                )

                self.signal_label.text = (
                    "SEDANG KONFIGURASI"
                )

                self.signal_info.text = (
                    "MENUNGGU SIGNAL"
                )

                self.entry_label.text = (
                    "ENTRY : -"
                )

            # =========================
            # HISTORY
            # =========================
            self.history_data = self.history_data[:6]

            history_text = "HISTORY SIGNAL\n\n"

            for item in self.history_data:

                history_text += f"• {item}\n"

            self.history_label.text = history_text

        except Exception as e:

            self.signal_label.text = "OFFLINE"

            self.signal_info.text = (
                "SERVER ERROR"
            )

            print("ERROR :", e)


# =========================
# MAIN APP
# =========================
class AISignalApp(App):

    def build(self):

        root = BoxLayout(
            orientation="vertical"
        )

        # =========================
        # SCROLL CONTENT
        # =========================
        scroll = ScrollView()

        content = Content()

        scroll.add_widget(content)

        # =========================
        # FIXED BOTTOM NAVBAR
        # =========================
        navbar = BoxLayout(
            orientation="horizontal",
            spacing=8,
            size_hint_y=None,
            height=60,
            padding=5
        )

        btn_home = Button(
            text="HOME",
            font_size=18,
            background_color=(0.08, 0.08, 0.1, 1)
        )

        btn_history = Button(
            text="HISTORY",
            font_size=18,
            background_color=(0.08, 0.08, 0.1, 1)
        )

        btn_profile = Button(
            text="PROFILE",
            font_size=18,
            background_color=(0.08, 0.08, 0.1, 1)
        )

        navbar.add_widget(btn_home)
        navbar.add_widget(btn_history)
        navbar.add_widget(btn_profile)

        # =========================
        # ADD ROOT
        # =========================
        root.add_widget(scroll)
        root.add_widget(navbar)

        return root


# =========================
# RUN
# =========================
if __name__ == "__main__":

    AISignalApp().run()
