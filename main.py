import requests
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


class SignalApp(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=25, spacing=10, **kwargs)

        # ======================
        # TECHNOLOGY BACKGROUND (DARK BLUE CYBER)
        # ======================
        Window.clearcolor = (0.03, 0.05, 0.10, 1)

        # ======================
        # HEADER LOGO
        # ======================
        self.logo = Label(
            text="AI SIGNAL PRO",
            font_size=36,
            bold=True,
            color=(0.3, 0.8, 1, 1)  # neon blue
        )
        self.add_widget(self.logo)

        self.subtitle = Label(
            text="REALTIME TRADING SYSTEM",
            font_size=14,
            color=(0.5, 0.7, 0.9, 1)
        )
        self.add_widget(self.subtitle)

        # ======================
        # CLOCK
        # ======================
        self.clock = Label(text="", font_size=20, color=(0.7, 0.7, 0.7, 1))
        self.add_widget(self.clock)

        # ======================
        # MARKET
        # ======================
        self.market = Label(text="MARKET: -", font_size=18, color=(0.8, 0.8, 0.8, 1))
        self.add_widget(self.market)

        # ======================
        # SIGNAL
        # ======================
        self.signal = Label(text="WAITING SIGNAL", font_size=50, bold=True)
        self.add_widget(self.signal)

        # ======================
        # ENTRY
        # ======================
        self.entry = Label(text="ENTRY: -", font_size=18, color=(0.8, 0.8, 0.8, 1))
        self.add_widget(self.entry)

        # ======================
        # STATUS
        # ======================
        self.status = Label(text="CONNECTING...", font_size=14, color=(0.5, 0.5, 0.5, 1))
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
            data = r.json()

            signal = data.get("signal", "WAITING")
            market = data.get("market", "-")
            entry_time = data.get("entry_time", "00:00")

            self.market.text = f"📊 {market}"

            # ENTRY +1 MIN
            try:
                t = datetime.strptime(entry_time, "%H:%M")
                t = t + timedelta(minutes=1)
                final_entry = t.strftime("%H.%M")
            except:
                final_entry = entry_time

            # ======================
            # BUY STYLE (NEON GREEN)
            # ======================
            if signal.upper() == "BUY":
                Window.clearcolor = (0.02, 0.15, 0.10, 1)
                self.signal.text = "🟢 BUY NOW"
                self.signal.color = (0, 1, 0.6, 1)
                self.entry.text = f"ENTRY BUY: {final_entry}"
                self.status.text = "LIVE CONNECTED"

            # ======================
            # SELL STYLE (NEON RED)
            # ======================
            elif signal.upper() == "SELL":
                Window.clearcolor = (0.15, 0.02, 0.05, 1)
                self.signal.text = "🔴 SELL NOW"
                self.signal.color = (1, 0.2, 0.3, 1)
                self.entry.text = f"ENTRY SELL: {final_entry}"
                self.status.text = "LIVE CONNECTED"

            # ======================
            # WAITING
            # ======================
            else:
                Window.clearcolor = (0.03, 0.05, 0.10, 1)
                self.signal.text = "WAITING SIGNAL"
                self.signal.color = (0.7, 0.7, 0.7, 1)
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
