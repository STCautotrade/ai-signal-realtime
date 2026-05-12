import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.widget import Widget
from datetime import datetime, timedelta

# ======================
# GITHUB SIGNAL
# ======================
DATA_URL = "https://raw.githubusercontent.com/STCautotrade/ai-signal-realtime/main/signal.json"


class SignalApp(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=10, **kwargs)

        # ======================
        # BACKGROUND
        # ======================
        Window.clearcolor = (0.08, 0.08, 0.10, 1)

        # ======================
        # LOGO / HEADER (TIMPUL ABU)
        # ======================
        self.logo = Label(
            text="AI SIGNAL PRO",
            font_size=34,
            bold=True,
            color=(0.7, 0.7, 0.7, 1)
        )
        self.add_widget(self.logo)

        self.subtitle = Label(
            text="REALTIME TRADING SIGNAL",
            font_size=14,
            color=(0.5, 0.5, 0.5, 1)
        )
        self.add_widget(self.subtitle)

        # ======================
        # CLOCK
        # ======================
        self.clock = Label(text="", font_size=20)
        self.add_widget(self.clock)

        # ======================
        # MARKET
        # ======================
        self.market = Label(text="MARKET: -", font_size=18)
        self.add_widget(self.market)

        # ======================
        # SIGNAL
        # ======================
        self.signal = Label(text="WAITING SIGNAL", font_size=48, bold=True)
        self.add_widget(self.signal)

        # ======================
        # ENTRY
        # ======================
        self.entry = Label(text="ENTRY: -", font_size=18)
        self.add_widget(self.entry)

        # ======================
        # STATUS
        # ======================
        self.status = Label(text="CONNECTING...", font_size=14)
        self.add_widget(self.status)

        Clock.schedule_interval(self.update_clock, 1)
        Clock.schedule_interval(self.load_signal, 1)

    # ======================
    def update_clock(self, dt):
        self.clock.text = "🕒 " + datetime.now().strftime("%H:%M:%S")

    # ======================
    def load_signal(self, dt):
        try:
            headers = {
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
                "User-Agent": "Mozilla/5.0"
            }

            r = requests.get(DATA_URL, headers=headers, timeout=8)

            print("STATUS:", r.status_code)
            print("RAW:", r.text)

            data = r.json()

            signal = data.get("signal", "WAITING")
            market = data.get("market", "-")
            entry_time = data.get("entry_time", "00:00")

            self.market.text = f"📊 {market}"

            # ======================
            # ENTRY +1 MIN
            # ======================
            try:
                t = datetime.strptime(entry_time, "%H:%M")
                t = t + timedelta(minutes=1)
                final_entry = t.strftime("%H.%M")
            except:
                final_entry = entry_time

            # ======================
            # BUY
            # ======================
            if signal.upper() == "BUY":
                Window.clearcolor = (0, 0.5, 0, 1)
                self.signal.text = "🟢 BUY NOW"
                self.entry.text = f"ENTRY BUY: {final_entry}"
                self.status.text = "LIVE CONNECTED"

            # ======================
            # SELL
            # ======================
            elif signal.upper() == "SELL":
                Window.clearcolor = (0.6, 0, 0, 1)
                self.signal.text = "🔴 SELL NOW"
                self.entry.text = f"ENTRY SELL: {final_entry}"
                self.status.text = "LIVE CONNECTED"

            # ======================
            # WAITING
            # ======================
            else:
                Window.clearcolor = (0.08, 0.08, 0.10, 1)
                self.signal.text = "WAITING SIGNAL"
                self.entry.text = "-"
                self.status.text = "NO SIGNAL"

        except Exception as e:
            print("ERROR:", e)
            self.signal.text = "ERROR CONNECT"
            self.status.text = "OFFLINE"


class MainApp(App):
    def build(self):
        return SignalApp()


MainApp().run()
