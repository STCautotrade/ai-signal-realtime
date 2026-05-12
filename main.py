import requests
import time
from datetime import datetime

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.scrollview import MDScrollView
from kivy.clock import Clock
from kivy.core.window import Window


DATA_URL = "http://157.10.252.46:5000/signal"


# ======================
# MAIN SCREEN
# ======================
class MainScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.history = []

        Window.clearcolor = (0.12, 0.12, 0.14, 1)

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
            radius=20,
            padding=20,
            size_hint_y=None,
            height=100
        )

        self.clock = MDLabel(
            text="00:00:00",
            halign="center",
            font_style="H3"
        )

        self.clock_card.add_widget(self.clock)
        root.add_widget(self.clock_card)

        # ======================
        # MARKET
        # ======================
        self.market = MDLabel(
            text="MARKET: -",
            halign="center",
            size_hint_y=None,
            height=30
        )
        root.add_widget(self.market)

        # ======================
        # ENTRY CARD (CORE SIGNAL)
        # ======================
        self.entry_card = MDCard(
            radius=25,
            padding=25,
            size_hint_y=None,
            height=180,
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
        # HISTORY (SAFE VERSION)
        # ======================
        self.history_box = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            spacing=5
        )

        self.history_scroll = MDScrollView()
        self.history_scroll.add_widget(self.history_box)

        root.add_widget(self.history_scroll)

        self.add_widget(root)

        # ======================
        # CLOCK + SIGNAL LOOP
        # ======================
        Clock.schedule_interval(self.update_clock, 1.5)
        Clock.schedule_interval(self.load_signal, 2.5)

    # ======================
    # CLOCK
    # ======================
    def update_clock(self, dt):
        self.clock.text = datetime.now().strftime("%H:%M:%S")

    # ======================
    # LOAD SIGNAL (SAFE API)
    # ======================
    def load_signal(self, dt):

        try:
            r = requests.get(DATA_URL + "?t=" + str(time.time()), timeout=3)
            data = r.json()

            signal = data.get("signal", "WAITING")
            market = data.get("market", "-")
            entry_time = data.get("entry_time", "-")

            self.market.text = f"📊 MARKET: {market}"

            # ======================
            # BUY
            # ======================
            if signal.upper() == "BUY":

                self.entry_card.md_bg_color = (0, 0.6, 0.2, 1)

                self.entry_label.text = "🟢 ENTRY BUY"
                self.entry_time.text = f"DI JAM {entry_time}"

                self.history.insert(0, f"BUY - {entry_time}")

            # ======================
            # SELL
            # ======================
            elif signal.upper() == "SELL":

                self.entry_card.md_bg_color = (0.6, 0, 0, 1)

                self.entry_label.text = "🔴 ENTRY SELL"
                self.entry_time.text = f"DI JAM {entry_time}"

                self.history.insert(0, f"SELL - {entry_time}")

            # ======================
            # WAIT
            # ======================
            else:

                self.entry_card.md_bg_color = (0.2, 0.2, 0.2, 1)

                self.entry_label.text = "MENUNGGU SIGNAL ....."

                self.entry_time.text = "-"

            # ======================
            # UPDATE HISTORY UI SAFE
            # ======================
            self.history_box.clear_widgets()

            for h in self.history[:10]:
                self.history_box.add_widget(
                    MDLabel(
                        text="• " + h,
                        size_hint_y=None,
                        height=25
                    )
                )

        except Exception as e:
            print("ERROR API:", e)
            self.entry_label.text = "OFFLINE"
            self.entry_card.md_bg_color = (0.1, 0.1, 0.1, 1)


# ======================
# APP
# ======================
class AISignalApp(MDApp):

    def build(self):
        return MainScreen()


if __name__ == "__main__":
    AISignalApp().run()
