import requests
import time
from datetime import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label


# =========================
# VPS API
# =========================
DATA_URL = "http://157.10.252.46:5000/signal"


# =========================
# WINDOW
# =========================
Window.clearcolor = (0.08, 0.08, 0.09, 1)


# =========================
# CARD
# =========================
class Card(BoxLayout):

    def __init__(self, bg=(0.15, 0.15, 0.17, 1), **kwargs):
        super().__init__(**kwargs)

        self.padding = 15
        self.spacing = 10
        self.size_hint_y = None

        with self.canvas.before:
            Color(*bg)
            self.rect = RoundedRectangle(radius=[20])

        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


# =========================
# MAIN UI
# =========================
class SignalUI(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(
            orientation="vertical",
            spacing=12,
            padding=12,
            **kwargs
        )

        self.history_data = []

        # =========================
        # TITLE
        # =========================
        title = Label(
            text="AI SIGNAL PRO",
            font_size=32,
            bold=True,
            size_hint_y=None,
            height=50,
            color=(0.2, 0.8, 1, 1)
        )
        self.add_widget(title)

        # =========================
        # CLOCK CARD
        # =========================
        self.clock_card = Card(height=90)

        self.clock_label = Label(
            text="00:00:00",
            font_size=34,
            bold=True,
            color=(0.0, 1.0, 0.6, 1)
        )

        self.clock_card.add_widget(self.clock_label)
        self.add_widget(self.clock_card)

        # =========================
        # MARKET CARD
        # =========================
        self.market_card = Card(height=70)

        self.market_label = Label(
            text="MARKET : -",
            font_size=22,
            bold=True,
            color=(1, 1, 1, 1)
        )

        self.market_card.add_widget(self.market_label)
        self.add_widget(self.market_card)

        # =========================
        # BIG SIGNAL CARD
        # =========================
        self.signal_card = Card(
            bg=(0.2, 0.2, 0.2, 1),
            height=180
        )

        self.signal_label = Label(
            text="MENUNGGU SIGNAL",
            font_size=34,
            bold=True,
            color=(1, 1, 1, 1)
        )

        self.signal_card.add_widget(self.signal_label)
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

        self.entry_card.add_widget(self.entry_label)
        self.add_widget(self.entry_card)

        # =========================
        # HISTORY CARD
        # =========================
        self.history_card = Card(height=170)

        self.history_label = Label(
            text="HISTORY\n-",
            font_size=18,
            halign="left",
            valign="top",
            color=(0.9, 0.9, 0.9, 1)
        )

        self.history_label.bind(size=self.history_label.setter('text_size'))

        self.history_card.add_widget(self.history_label)
        self.add_widget(self.history_card)

        # =========================
        # BOTTOM MENU
        # =========================
        bottom = BoxLayout(
            size_hint_y=None,
            height=55,
            spacing=10
        )

        btn_home = Button(
            text="HOME",
            background_color=(0.15, 0.15, 0.17, 1)
        )

        btn_history = Button(
            text="HISTORY",
            background_color=(0.15, 0.15, 0.17, 1)
        )

        btn_profile = Button(
            text="PROFILE",
            background_color=(0.15, 0.15, 0.17, 1)
        )

        bottom.add_widget(btn_home)
        bottom.add_widget(btn_history)
        bottom.add_widget(btn_profile)

        self.add_widget(bottom)

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
    # LOAD SIGNAL
    # =========================
    def load_signal(self, dt):

        try:
            r = requests.get(
                DATA_URL + "?t=" + str(time.time()),
                timeout=3
            )

            data = r.json()

            signal = data.get("signal", "WAITING")
            market = data.get("market", "-")
            entry_time = data.get("entry_time", "-")

            # =========================
            # MARKET
            # =========================
            self.market_label.text = f"MARKET : {market}"

            # =========================
            # BUY
            # =========================
            if signal.upper() == "BUY":

                self.signal_label.text = "ENTRY BUY"
                self.signal_label.color = (1, 1, 1, 1)

                self.signal_card.canvas.before.clear()

                with self.signal_card.canvas.before:
                    Color(0.0, 0.6, 0.2, 1)
                    self.signal_card.rect = RoundedRectangle(radius=[20])

                self.signal_card.bind(
                    pos=self.signal_card.update_rect,
                    size=self.signal_card.update_rect
                )

                self.entry_label.text = f"ENTRY BUY DI JAM {entry_time}"

                self.history_data.insert(
                    0,
                    f"BUY  -  {entry_time}"
                )

            # =========================
            # SELL
            # =========================
            elif signal.upper() == "SELL":

                self.signal_label.text = "ENTRY SELL"
                self.signal_label.color = (1, 1, 1, 1)

                self.signal_card.canvas.before.clear()

                with self.signal_card.canvas.before:
                    Color(0.8, 0.0, 0.0, 1)
                    self.signal_card.rect = RoundedRectangle(radius=[20])

                self.signal_card.bind(
                    pos=self.signal_card.update_rect,
                    size=self.signal_card.update_rect
                )

                self.entry_label.text = f"ENTRY SELL DI JAM {entry_time}"

                self.history_data.insert(
                    0,
                    f"SELL -  {entry_time}"
                )

            # =========================
            # WAITING
            # =========================
            else:

                self.signal_label.text = "MENUNGGU SIGNAL"
                self.signal_label.color = (1, 1, 1, 1)

                self.signal_card.canvas.before.clear()

                with self.signal_card.canvas.before:
                    Color(0.2, 0.2, 0.2, 1)
                    self.signal_card.rect = RoundedRectangle(radius=[20])

                self.signal_card.bind(
                    pos=self.signal_card.update_rect,
                    size=self.signal_card.update_rect
                )

                self.entry_label.text = "ENTRY : -"

            # =========================
            # HISTORY
            # =========================
            self.history_data = self.history_data[:5]

            history_text = "HISTORY SIGNAL\n\n"

            for item in self.history_data:
                history_text += f"{item}\n"

            self.history_label.text = history_text

        except Exception as e:

            self.signal_label.text = "OFFLINE"
            self.entry_label.text = "SERVER ERROR"

            print("ERROR :", e)


# =========================
# APP
# =========================
class AISignalApp(App):

    def build(self):
        return SignalUI()


# =========================
# RUN
# =========================
if __name__ == "__main__":
    AISignalApp().run()
