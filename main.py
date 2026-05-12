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

DATA_URL = "http://157.10.252.46:5000/signal"


# ======================
# CARD TEMPLATE
# ======================
class Card(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(padding=12, **kwargs)
        self.size_hint_y = None

        with self.canvas.before:
            Color(0.15, 0.15, 0.18, 1)
            self.bg = RoundedRectangle(radius=[18])

        self.bind(pos=self.update_bg, size=self.update_bg)

    def set_color(self, r, g, b, a=1):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(r, g, b, a)
            self.bg = RoundedRectangle(radius=[18])

    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size


# ======================
# MAIN APP
# ======================
class SignalUI(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=10, spacing=10, **kwargs)

        # 🔥 FIX: BACKGROUND SELALU ABU-ABU
        Window.clearcolor = (0.12, 0.12, 0.14, 1)

        self.page = "HOME"

        # ======================
        # TITLE
        # ======================
        self.title = Label(
            text="🚀 AI SIGNAL PRO",
            font_size=38,
            bold=True,
            size_hint_y=None,
            height=55,
            color=(0.3, 0.8, 1, 1)
        )
        self.add_widget(self.title)

        # ======================
        # CLOCK CARD
        # ======================
        self.clock_card = Card()
        self.clock_card.height = 80

        self.clock = Label(text="00:00:00", font_size=40, bold=True, color=(0, 1, 0.6, 1))
        self.clock_card.add_widget(self.clock)
        self.add_widget(self.clock_card)

        # ======================
        # MARKET
        # ======================
        self.market = Label(text="📊 MARKET: -", font_size=16, size_hint_y=None, height=30)
        self.add_widget(self.market)

        # ======================
        # SIGNAL
        # ======================
        self.signal = Label(text="MENUNGGU SIGNAL .....", font_size=35, bold=True, size_hint_y=None, height=90)
        self.add_widget(self.signal)

        # ======================
        # ENTRY CARD (🔥 INI YANG DIWARNAI)
        # ======================
        self.entry_card = Card()
        self.entry_card.height = 90

        self.entry = Label(text="-", font_size=24, bold=True)
        self.entry_card.add_widget(self.entry)
        self.add_widget(self.entry_card)

        # ======================
        # HISTORY
        # ======================
        self.history = Label(text="HISTORY:\n-", font_size=14)
        self.add_widget(self.history)

        # ======================
        # NAV
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

        self.history_list = []

        Clock.schedule_interval(self.update_clock, 1)
        Clock.schedule_interval(self.load_signal, 1)

    # ======================
    # CLOCK
    # ======================
    def update_clock(self, dt):
        self.clock.text = datetime.now().strftime("%H:%M:%S")

    # ======================
    # PAGE (optional)
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
            # BUY
            # ======================
            if signal.upper() == "BUY":

                self.signal.text = "ENTRY BUY"
                self.signal.color = (0, 1, 0.5, 1)

                self.entry.text = f"BUY @ {entry_time}"

                # 🔥 ENTRY CARD HIJAU
                self.entry_card.set_color(0.0, 0.6, 0.2, 1)

                self.history_list.insert(0, f"BUY - {entry_time}")

            # ======================
            # SELL
            # ======================
            elif signal.upper() == "SELL":

                self.signal.text = "ENTRY SELL"
                self.signal.color = (1, 0.2, 0.2, 1)

                self.entry.text = f"SELL @ {entry_time}"

                # 🔥 ENTRY CARD MERAH
                self.entry_card.set_color(0.6, 0.0, 0.0, 1)

                self.history_list.insert(0, f"SELL - {entry_time}")

            # ======================
            # WAIT
            # ======================
            else:

                self.signal.text = "MENUNGGU SIGNAL ....."

                self.entry.text = "-"

                # 🔥 ENTRY CARD NETRAL
                self.entry_card.set_color(0.15, 0.15, 0.18, 1)

            self.history.text = "HISTORY:\n" + "\n".join(self.history_list[:6])

        except Exception as e:
            print("ERROR:", e)
            self.signal.text = "OFFLINE"


class MainApp(App):

    def build(self):
        return SignalUI()


if __name__ == "__main__":
    MainApp().run()
