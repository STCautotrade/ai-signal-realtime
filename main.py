import requests
import time
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from datetime import datetime

# ======================
# VPS API
# ======================
DATA_URL = "http://157.10.252.46:5000/signal"


# ======================
# CARD COMPONENT
# ======================
class Card(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(padding=12, **kwargs)
        self.size_hint_y = None

        with self.canvas.before:
            Color(0.12, 0.12, 0.18, 1)
            self.bg = RoundedRectangle(radius=[18])

        self.bind(pos=self.update_bg, size=self.update_bg)

    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size


# ======================
# MAIN UI
# ======================
class SignalUI(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=10, spacing=8, **kwargs)

        Window.clearcolor = (0.05, 0.05, 0.08, 1)

        self.page = "HOME"
        self.history_list = []

        # ======================
        # TITLE
        # ======================
        self.title = Label(
            text="🚀 AI SIGNAL PRO",
            font_size=44,
            bold=True,
            size_hint_y=None,
            height=60,
            color=(0.2, 0.8, 1, 1)
        )
        self.add_widget(self.title)

        # ======================
        # ANIMATED BANNER
        # ======================
        self.banner_texts = [
            "⚡ REALTIME TRADING SYSTEM ⚡",
            "📡 CONNECTED TO VPS ENGINE",
            "🔥 AI ANALYSIS ACTIVE MODE"
        ]
        self.banner_index = 0

        self.banner = Label(
            text=self.banner_texts[0],
            font_size=16,
            size_hint_y=None,
            height=25,
            color=(0.7, 0.7, 1, 1)
        )
        self.add_widget(self.banner)

        Clock.schedule_interval(self.animate_banner, 2)

        # ======================
        # CLOCK CARD
        # ======================
        self.clock_card = Card()
        self.clock_card.height = 90

        self.clock = Label(
            text="00:00:00",
            font_size=48,
            bold=True,
            color=(0, 1, 0.6, 1)
        )
        self.clock_card.add_widget(self.clock)
        self.add_widget(self.clock_card)

        # ======================
        # MARKET
        # ======================
        self.market = Label(
            text="📊 MARKET: -",
            font_size=18,
            size_hint_y=None,
            height=30
        )
        self.add_widget(self.market)

        # ======================
        # SIGNAL STATE
        # ======================
        self.signal = Label(
            text="MENUNGGU SIGNAL .....",
            font_size=40,
            bold=True,
            size_hint_y=None,
            height=100
        )
        self.add_widget(self.signal)

        # ======================
        # ENTRY
        # ======================
        self.entry = Label(
            text="-",
            font_size=22,
            size_hint_y=None,
            height=40
        )
        self.add_widget(self.entry)

        # ======================
        # CONTENT AREA (DYNAMIC PAGE)
        # ======================
        self.content = Label(
            text="SYSTEM READY",
            font_size=14
        )
        self.add_widget(self.content)

        # ======================
        # HISTORY BOX
        # ======================
        self.history_box = Label(
            text="HISTORY:\n-",
            font_size=14
        )
        self.add_widget(self.history_box)

        # ======================
        # NAV BUTTONS (REAL CLICK)
        # ======================
        nav = BoxLayout(size_hint_y=None, height=45, spacing=5)

        btn_home = Button(text="HOME")
        btn_history = Button(text="HISTORY")
        btn_profile = Button(text="PROFILE")

        btn_home.bind(on_press=lambda x: self.set_page("HOME"))
        btn_history.bind(on_press=lambda x: self.set_page("HISTORY"))
        btn_profile.bind(on_press=lambda x: self.set_page("PROFILE"))

        nav.add_widget(btn_home)
        nav.add_widget(btn_history)
        nav.add_widget(btn_profile)

        self.add_widget(nav)

        # ======================
        # CLOCK + SIGNAL LOOP
        # ======================
        Clock.schedule_interval(self.update_clock, 1)
        Clock.schedule_interval(self.load_signal, 1)

    # ======================
    # BANNER ANIMATION
    # ======================
    def animate_banner(self, dt):
        self.banner_index = (self.banner_index + 1) % len(self.banner_texts)
        self.banner.text = self.banner_texts[self.banner_index]

    # ======================
    # CLOCK
    # ======================
    def update_clock(self, dt):
        self.clock.text = datetime.now().strftime("%H:%M:%S")

    # ======================
    # CHANGE PAGE
    # ======================
    def set_page(self, page):
        self.page = page

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

            self.market.text = f"📊 MARKET: {market}"

            # ======================
            # HOME PAGE
            # ======================
            if self.page == "HOME":

                if signal.upper() == "BUY":

                    Window.clearcolor = (0.0, 0.4, 0.0, 1)

                    self.signal.text = "ENTRY BUY"
                    self.signal.color = (0, 1, 0.5, 1)

                    self.entry.text = f"ENTRY BUY JAM {entry_time}"

                    self.history_list.insert(0, f"BUY - {entry_time}")

                elif signal.upper() == "SELL":

                    Window.clearcolor = (0.5, 0.0, 0.0, 1)

                    self.signal.text = "ENTRY SELL"
                    self.signal.color = (1, 0.2, 0.2, 1)

                    self.entry.text = f"ENTRY SELL JAM {entry_time}"

                    self.history_list.insert(0, f"SELL - {entry_time}")

                else:

                    Window.clearcolor = (0.05, 0.05, 0.08, 1)

                    self.signal.text = "MENUNGGU SIGNAL ....."
                    self.signal.color = (1, 1, 1, 1)

                    self.entry.text = "-"

                # update history preview
                self.history_box.text = "HISTORY:\n" + "\n".join(self.history_list[:5])

            # ======================
            # HISTORY PAGE
            # ======================
            elif self.page == "HISTORY":

                Window.clearcolor = (0.07, 0.07, 0.10, 1)

                self.signal.text = "HISTORY MODE"
                self.entry.text = "-"

                self.content.text = "FULL HISTORY SIGNAL"

                self.history_box.text = "ALL HISTORY:\n" + "\n".join(self.history_list)

            # ======================
            # PROFILE PAGE
            # ======================
            elif self.page == "PROFILE":

                Window.clearcolor = (0.08, 0.08, 0.12, 1)

                self.signal.text = "PROFILE"
                self.entry.text = "-"

                self.content.text = (
                    "AI SIGNAL PRO\n"
                    "VPS CONNECTED\n"
                    "REALTIME SYSTEM ACTIVE"
                )

                self.history_box.text = ""

        except Exception as e:
            print("ERROR:", e)
            self.signal.text = "OFFLINE"


# ======================
# APP RUN
# ======================
class MainApp(App):

    def build(self):
        return SignalUI()


if __name__ == "__main__":
    MainApp().run()
