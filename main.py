import requests
import time
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.window import Window
from datetime import datetime, timedelta

# ======================
# GITHUB SIGNAL
# ======================
DATA_URL = "https://raw.githubusercontent.com/STCautotrade/ai-signal-realtime/main/signal.json"


class SignalUI(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=10, **kwargs)

        # DARK MODE DEFAULT
        Window.clearcolor = (0.06, 0.06, 0.08, 1)

        # TITLE
        self.title = Label(
            text="🚨 AI SIGNAL CRYPTO IDX",
            font_size=28,
            bold=True
        )
        self.add_widget(self.title)

        # CLOCK
        self.clock = Label(text="", font_size=20)
        self.add_widget(self.clock)

        # MARKET
        self.market = Label(text="MARKET: -", font_size=18)
        self.add_widget(self.market)

        # BIG SIGNAL
        self.signal = Label(
            text="WAITING SIGNAL",
            font_size=60,
            bold=True
        )
        self.add_widget(self.signal)

        # ENTRY
        self.entry = Label(text="ENTRY: -", font_size=22)
        self.add_widget(self.entry)

        # STATUS
        self.status = Label(text="STATUS: CONNECTING...", font_size=16)
        self.add_widget(self.status)

        Clock.schedule_interval(self.update_clock, 1)
        Clock.schedule_interval(self.load_signal, 2)

    # ======================
    # CLOCK
    # ======================
    def update_clock(self, dt):
        self.clock.text = "🕒 " + datetime.now().strftime("%H:%M:%S")

    # ======================
    # LOAD SIGNAL
    # ======================
    def load_signal(self, dt):

        try:
            headers = {"Cache-Control": "no-cache"}

            # 🔥 ANTI CACHE FIX
            r = requests.get(DATA_URL + "?t=" + str(time.time()), headers=headers, timeout=5)
            data = r.json()

            signal = data.get("signal", "WAITING")
            market = data.get("market", "-")
            entry_time = data.get("entry_time", "00:00")

            self.market.text = f"📊 {market}"

            # ======================
            # ENTRY +1 MINUTE
            # ======================
            try:
                t = datetime.strptime(entry_time, "%H:%M")
                t = t + timedelta(minutes=1)
                final_entry = t.strftime("%H.%M")
            except:
                final_entry = entry_time

            # ======================
            # BUY MODE
            # ======================
            if signal.upper() == "BUY":

                Window.clearcolor = (0.0, 0.6, 0.0, 1)

                self.signal.text = "🟢 BUY NOW"
                self.entry.text = f"ENTRY BUY DI JAM {final_entry}"
                self.status.text = "CONNECTED"

            # ======================
            # SELL MODE
            # ======================
            elif signal.upper() == "SELL":

                Window.clearcolor = (0.6, 0.0, 0.0, 1)

                self.signal.text = "🔴 SELL NOW"
                self.entry.text = f"ENTRY SELL DI JAM {final_entry}"
                self.status.text = "CONNECTED"

            # ======================
            # WAITING
            # ======================
            else:

                Window.clearcolor = (0.06, 0.06, 0.08, 1)

                self.signal.text = "WAITING SIGNAL"
                self.entry.text = "-"
                self.status.text = "NO SIGNAL"

        except:

            Window.clearcolor = (0.1, 0.1, 0.12, 1)

            self.signal.text = "OFFLINE"
            self.entry.text = "-"
            self.status.text = "NO CONNECTION"


class MainApp(App):

    def build(self):
        return SignalUI()


MainApp().run()
