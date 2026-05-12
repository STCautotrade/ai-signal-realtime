import requests
import time
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.window import Window
from datetime import datetime, timedelta

# ======================
# VPS API SIGNAL (REALTIME)
# ======================
DATA_URL = "http://157.10.252.46:5000/signal"


class SignalUI(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=10, **kwargs)

        # DARK MODE
        Window.clearcolor = (0.06, 0.06, 0.08, 1)

        # TITLE
        self.title = Label(
            text="🚨 AI SIGNAL CRYPTO IDX",
            font_size=28,
            bold=True,
            color=(1, 1, 1, 1)
        )
        self.add_widget(self.title)

        # CLOCK
        self.clock = Label(
            text="",
            font_size=20,
            color=(0.8, 0.8, 0.8, 1)
        )
        self.add_widget(self.clock)

        # MARKET
        self.market = Label(
            text="📊 MARKET: -",
            font_size=18,
            color=(0.9, 0.9, 0.9, 1)
        )
        self.add_widget(self.market)

        # SIGNAL
        self.signal = Label(
            text="WAITING SIGNAL",
            font_size=60,
            bold=True
        )
        self.add_widget(self.signal)

        # ENTRY
        self.entry = Label(
            text="ENTRY: -",
            font_size=22,
            color=(0.9, 0.9, 0.9, 1)
        )
        self.add_widget(self.entry)

        # STATUS
        self.status = Label(
            text="STATUS: CONNECTING...",
            font_size=16,
            color=(0.7, 0.7, 0.7, 1)
        )
        self.add_widget(self.status)

        Clock.schedule_interval(self.update_clock, 1)
        Clock.schedule_interval(self.load_signal, 1)

    # ======================
    # CLOCK REALTIME
    # ======================
    def update_clock(self, dt):
        self.clock.text = "🕒 " + datetime.now().strftime("%H:%M:%S")

    # ======================
    # LOAD SIGNAL FROM VPS
    # ======================
    def load_signal(self, dt):

        try:
            r = requests.get(
                DATA_URL + "?t=" + str(time.time()),
                timeout=5
            )
            data = r.json()

            signal = data.get("signal", "WAITING")
            market = data.get("market", "-")
            entry_time = data.get("entry_time", "00:00")

            self.market.text = f"📊 MARKET: {market}"

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
                self.signal.color = (0, 1, 0.5, 1)

                self.entry.text = f"ENTRY BUY DI JAM {final_entry}"
                self.status.text = "CONNECTED"

            # ======================
            # SELL MODE
            # ======================
            elif signal.upper() == "SELL":

                Window.clearcolor = (0.6, 0.0, 0.0, 1)

                self.signal.text = "🔴 SELL NOW"
                self.signal.color = (1, 0.2, 0.3, 1)

                self.entry.text = f"ENTRY SELL DI JAM {final_entry}"
                self.status.text = "CONNECTED"

            # ======================
            # WAITING
            # ======================
            else:

                Window.clearcolor = (0.06, 0.06, 0.08, 1)

                self.signal.text = "WAITING SIGNAL"
                self.signal.color = (1, 1, 1, 1)

                self.entry.text = "-"
                self.status.text = "NO SIGNAL"

        except Exception as e:

            print("ERROR:", e)

            Window.clearcolor = (0.1, 0.1, 0.12, 1)

            self.signal.text = "OFFLINE"
            self.entry.text = "-"
            self.status.text = "NO CONNECTION"


class MainApp(App):

    def build(self):
        return SignalUI()


if __name__ == "__main__":
    MainApp().run()
