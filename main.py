import requests
import time
from datetime import datetime

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivy.clock import Clock
from kivy.core.window import Window


DATA_URL = "http://157.10.252.46:5000/signal"


class MainScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.history = []

        Window.clearcolor = (0.10, 0.10, 0.12, 1)

        root = MDBoxLayout(orientation="vertical", padding=15, spacing=12)

        # ======================
        # TITLE
        # ======================
        self.title = MDLabel(
            text="🚀 AI SIGNAL PRO",
            halign="center",
            font_style="H4",
            bold=True,
            size_hint_y=None,
            height=40
        )
        root.add_widget(self.title)

        # ======================
        # CLOCK CARD
        # ======================
        self.clock_card = MDCard(
            radius=15,
            padding=15,
            size_hint_y=None,
            height=80
        )

        self.clock = MDLabel(
            text="00:00:00",
            halign="center",
            font_style="H3"
        )

        self.clock_card.add_widget(self.clock)
        root.add_widget(self.clock_card)

        # ======================
        # MARKET CARD
        # ======================
        self.market_card = MDCard(
            radius=15,
            padding=15,
            size_hint_y=None,
            height=70
        )

        self.market = MDLabel(
            text="MARKET: -",
            halign="center"
        )

        self.market_card.add_widget(self.market)
        root.add_widget(self.market_card)

        # ======================
        # ENTRY CARD (BIG CORE)
        # ======================
        self.entry_card = MDCard(
            radius=25,
            padding=25,
            size_hint_y=None,
            height=200,
            md_bg_color=(0.2, 0.2, 0.2, 1)
        )

        self.entry_label = MDLabel(
            text="MENUNGGU SIGNAL .....",
            halign="center",
            font_style="H4",
            bold=True
        )

        self.entry_time = MDLabel(
            text="-",
            halign="center"
        )

        box = MDBoxLayout(orientation="vertical")
        box.add_widget(self.entry_label)
        box.add_widget(self.entry_time)

        self.entry_card.add_widget(box)
        root.add_widget(self.entry_card)

        # ======================
        # STATUS CARD
        # ======================
        self.status_card = MDCard(
            radius=15,
            padding=15,
            size_hint_y=None,
            height=70
        )

        self.status = MDLabel(
            text="STATUS: CONNECTING...",
            halign="center"
        )

        self.status_card.add_widget(self.status)
        root.add_widget(self.status_card)

        # ======================
        # HISTORY CARD
        # ======================
        self.history_card = MDCard(
            radius=15,
            padding=15
        )

        self.history_label = MDLabel(
            text="HISTORY:\n-",
            halign="left"
        )

        self.history_card.add_widget(self.history_label)
        root.add_widget(self.history_card)

        self.add_widget(root)

        Clock.schedule_interval(self.update_clock, 1)
        Clock.schedule_interval(self.load_signal, 2)

    # ======================
    # CLOCK
    # ======================
    def update_clock(self, dt):
        self.clock.text = datetime.now().strftime("%H:%M:%S")

    # ======================
    # LOAD SIGNAL
    # ======================
    def load_signal(self, dt):

        try:
            r = requests.get(DATA_URL + "?t=" + str(time.time()), timeout=4)
            data = r.json()

            signal = data.get("signal", "WAITING")
            market = data.get("market", "-")
            entry_time = data.get("entry_time", "-")

            self.market.text = f"📊 MARKET: {market}"

            # ======================
            # BUY
            # ======================
            if signal.upper() == "BUY":

                self.entry_card.md_bg_color = (0, 0.7, 0.2, 1)

                self.entry_label.text = "🟢 ENTRY BUY"
                self.entry_time.text = f"DI JAM {entry_time}"

                self.status.text = "ACTIVE BUY SIGNAL"

                self.history.insert(0, f"BUY - {entry_time}")

            # ======================
            # SELL
            # ======================
            elif signal.upper() == "SELL":

                self.entry_card.md_bg_color = (0.7, 0, 0, 1)

                self.entry_label.text = "🔴 ENTRY SELL"
                self.entry_time.text = f"DI JAM {entry_time}"

                self.status.text = "ACTIVE SELL SIGNAL"

                self.history.insert(0, f"SELL - {entry_time}")

            # ======================
            # WAIT
            # ======================
            else:

                self.entry_card.md_bg_color = (0.2, 0.2, 0.2, 1)

                self.entry_label.text = "MENUNGGU SIGNAL ....."

                self.entry_time.text = "-"

                self.status.text = "NO SIGNAL"

            # ======================
            # UPDATE HISTORY
            # ======================
            self.history_label.text = "HISTORY:\n" + "\n".join(self.history[:8])

        except Exception as e:
            print("ERROR:", e)
            self.status.text = "OFFLINE / NO CONNECTION"


class AISignalApp(MDApp):

    def build(self):
        return MainScreen()


if __name__ == "__main__":
    AISignalApp().run()
