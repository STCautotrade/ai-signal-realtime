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
# RGB ANIMATION COLORS
# ======================
RGB_COLORS = [
    (0, 0.8, 0.2, 1),
    (0.2, 0.6, 1, 1),
    (1, 0.2, 0.2, 1),
    (1, 1, 0.2, 1)
]


class MainScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.history = []
        self.rgb_index = 0
        self.page = "HOME"

        Window.clearcolor = (0.12, 0.12, 0.14, 1)

        root = MDBoxLayout(orientation="vertical", padding=15, spacing=10)

        # ======================
        # TITLE
        # ======================
        self.title = MDLabel(
            text="🚀 AI SIGNAL PRO",
            halign="center",
            font_style="H4",
            bold=True
        )
        root.add_widget(self.title)

        # ======================
        # CLOCK CARD
        # ======================
        self.clock_card = MDCard(radius=20, padding=20, size_hint_y=None, height=90)

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
        self.market = MDLabel(text="MARKET: -", halign="center")
        root.add_widget(self.market)

        # ======================
        # ENTRY CARD (CORE PRO PANEL)
        # ======================
        self.entry_card = MDCard(
            radius=25,
            padding=25,
            size_hint_y=None,
            height=180
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
        # HISTORY SCROLL
        # ======================
        self.history_label = MDLabel(
            text="HISTORY:\n-",
            halign="left",
            size_hint_y=None
        )

        scroll = MDScrollView()
        scroll.add_widget(self.history_label)

        root.add_widget(scroll)

        # ======================
        # NAVIGATION
        # ======================
        nav = MDBoxLayout(size_hint_y=None, height=60, spacing=10)

        nav.add_widget(MDLabel(text="HOME", halign="center"))
        nav.add_widget(MDLabel(text="HISTORY", halign="center"))
        nav.add_widget(MDLabel(text="PROFILE", halign="center"))

        root.add_widget(nav)

        self.add_widget(root)

        Clock.schedule_interval(self.update_clock, 1)
        Clock.schedule_interval(self.load_signal, 1)
        Clock.schedule_interval(self.rgb_animation, 0.2)

    # ======================
    # CLOCK
    # ======================
    def update_clock(self, dt):
        self.clock.text = datetime.now().strftime("%H:%M:%S")

    # ======================
    # RGB BORDER EFFECT
    # ======================
    def rgb_animation(self, dt):
        color = RGB_COLORS[self.rgb_index]
        self.entry_card.md_bg_color = color
        self.rgb_index = (self.rgb_index + 1) % len(RGB_COLORS)

    # ======================
    # LOAD SIGNAL
    # ======================
    def load_signal(self, dt):

        try:
            r = requests.get(DATA_URL + "?t=" + str(time.time()), timeout=5)
            data = r.json()

            signal = data.get("signal", "WAITING")
            market = data.get("market", "-")
            entry_time = data.get("entry_time", "-")

            self.market.text = f"MARKET: {market}"

            # ======================
            # BUY
            # ======================
            if signal.upper() == "BUY":

                self.entry_label.text = "🟢 ENTRY BUY"
                self.entry_time.text = f"DI JAM {entry_time}"

                self.history.insert(0, f"BUY - {entry_time}")

                self.entry_card.md_bg_color = (0, 0.6, 0.2, 1)

            # ======================
            # SELL
            # ======================
            elif signal.upper() == "SELL":

                self.entry_label.text = "🔴 ENTRY SELL"
                self.entry_time.text = f"DI JAM {entry_time}"

                self.history.insert(0, f"SELL - {entry_time}")

                self.entry_card.md_bg_color = (0.6, 0, 0, 1)

            # ======================
            # WAIT
            # ======================
            else:

                self.entry_label.text = "MENUNGGU SIGNAL ....."
                self.entry_time.text = "-"

            # ======================
            # UPDATE HISTORY
            # ======================
            self.history_label.text = "HISTORY:\n" + "\n".join(self.history[:10])

        except Exception as e:
            print("ERROR:", e)
            self.entry_label.text = "OFFLINE"


class AISignalApp(MDApp):

    def build(self):
        return MainScreen()


if __name__ == "__main__":
    AISignalApp().run()
