import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.window import Window
from datetime import datetime, timedelta

# ======================
# GITHUB SIGNAL JSON
# ======================
DATA_URL = "https://raw.githubusercontent.com/STCautotrade/ai-signal-realtime/main/signal.json"


class SignalApp(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=25, spacing=12, **kwargs)

        # DARK THEME DEFAULT
        Window.clearcolor = (0.08, 0.08, 0.10, 1)

        # TITLE
        self.title = Label(
            text="🚨 SIGNAL CRYPTO IDX",
            font_size=30,
            bold=True
        )
        self.add_widget(self.title)

        # CLOCK
        self.clock = Label(text="", font_size=22)
        self.add_widget(self.clock)

        # MARKET
        self.market = Label(text="MARKET: -", font_size=20)
        self.add_widget(self.market)

        # SIGNAL BIG TEXT
        self.signal = Label(text="WAITING SIGNAL", font_size=52, bold=True)
        self.add_widget(self.signal)

        # ENTRY TIME
        self.entry = Label(text="ENTRY: -", font_size=22)
        self.add_widget(self.entry)

        # MESSAGE / STATUS
        self.status = Label(text="STATUS: CONNECTING...", font_size=16)
        self.add_widget(self.status)

        # SCHEDULE LOOP
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
            headers = {"User-Agent": "Mozilla/5.0"}
            r = requests.get(DATA_URL, headers=headers, timeout=8)
            data = r.json()

            signal = data.get("signal", "WAITING")
            market = data.get("market", "-")
            entry_time = data.get("entry_time", "00:00")

            self.market.text = f"📊 {market}"

            # ======================
            # CONVERT ENTRY +1 MIN
            # ======================
            try:
                t = datetime.strptime(entry_time, "%H:%M")
                t = t + timedelta(minutes=1)
                final_entry = t.strftime("%H.%M")
            except:
                final_entry = entry_time

            # ======================
            # BUY SIGNAL
            # ======================
            if signal.upper() == "BUY":
                Window.clearcolor = (0, 0.5, 0, 1)

                self.signal.text = "🟢 BUY NOW"
                self.entry.text = f"ENTRY BUY DI JAM {final_entry}"
                self.status.text = "STATUS: CONNECTED"

            # ======================
            # SELL SIGNAL
            # ======================
            elif signal.upper() == "SELL":
                Window.clearcolor = (0.6, 0, 0, 1)

                self.signal.text = "🔴 SELL NOW"
                self.entry.text = f"ENTRY SELL DI JAM {final_entry}"
                self.status.text = "STATUS: CONNECTED"

            # ======================
            # WAITING
            # ======================
            else:
                Window.clearcolor = (0.08, 0.08, 0.10, 1)

                self.signal.text = "WAITING SIGNAL"
                self.entry.text = "-"
                self.status.text = "STATUS: NO SIGNAL"

        # ======================
        # OFFLINE MODE
        # ======================
        except:
            Window.clearcolor = (0.1, 0.1, 0.12, 1)

            self.signal.text = "OFFLINE"
            self.entry.text = "-"
            self.status.text = "STATUS: NO CONNECTION"


# ======================
# RUN APP
# ======================
class MainApp(App):
    def build(self):
        return SignalApp()


MainApp().run()
