import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.window import Window
from datetime import datetime, timedelta
import random

DATA_URL = "https://raw.githubusercontent.com/STCautotrade/ai-signal-realtime/main/signal.json"


class SignalUI(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=25, spacing=15, **kwargs)

        Window.clearcolor = (0.05, 0.05, 0.05, 1)

        # TITLE
        self.title = Label(
            text="🚨 SIGNAL CRYPTO IDX 🚨",
            font_size=30,
            bold=True
        )
        self.add_widget(self.title)

        # MARKET
        self.market = Label(text="Market: -", font_size=22)
        self.add_widget(self.market)

        # CLOCK
        self.clock = Label(text="", font_size=24)
        self.add_widget(self.clock)

        # SIGNAL
        self.signal = Label(text="WAITING SIGNAL", font_size=55, bold=True)
        self.add_widget(self.signal)

        # ENTRY INFO
        self.entry = Label(text="ENTRY: -", font_size=24)
        self.add_widget(self.entry)

        # MESSAGE
        self.message = Label(text="", font_size=16)
        self.add_widget(self.message)

        # CHART SIMULASI
        self.chart = Label(text="", font_size=18)
        self.add_widget(self.chart)

        Clock.schedule_interval(self.update_clock, 1)
        Clock.schedule_interval(self.load_signal, 2)
        Clock.schedule_interval(self.fake_chart, 1)

    # =====================
    # CLOCK
    # =====================
    def update_clock(self, dt):
        self.clock.text = "🕒 " + datetime.now().strftime("%H:%M:%S")

    # =====================
    # LOAD SIGNAL
    # =====================
    def load_signal(self, dt):

        try:
            r = requests.get(DATA_URL, timeout=5)
            data = r.json()

            market = data.get("market", "-")
            signal = data.get("signal", "-")
            entry_time = data.get("entry_time", "00:00")
            message = data.get("message", "")

            self.market.text = f"📊 {market}"
            self.message.text = message

            # ==========================
            # HITUNG ENTRY + 1 MENIT
            # ==========================
            try:
                entry_dt = datetime.strptime(entry_time, "%H:%M")
                entry_dt = entry_dt + timedelta(minutes=1)
                entry_final = entry_dt.strftime("%H.%M")
            except:
                entry_final = entry_time

            # ==========================
            # BUY
            # ==========================
            if signal.upper() == "BUY":

                Window.clearcolor = (0, 0.4, 0, 1)

                self.signal.text = "🟢 BUY NOW"
                self.entry.text = f"ENTRY BUY DI JAM {entry_final}"

            # ==========================
            # SELL
            # ==========================
            elif signal.upper() == "SELL":

                Window.clearcolor = (0.5, 0, 0, 1)

                self.signal.text = "🔴 SELL NOW"
                self.entry.text = f"ENTRY SELL DI JAM {entry_final}"

            else:
                Window.clearcolor = (0.05, 0.05, 0.05, 1)
                self.signal.text = "WAITING SIGNAL"
                self.entry.text = "-"

        except Exception as e:
            self.signal.text = "NO CONNECTION"
            self.entry.text = str(e)

    # =====================
    # FAKE CHART
    # =====================
    def fake_chart(self, dt):

        bars = ["▁","▂","▃","▄","▅","▆","▇","█"]
        self.chart.text = "📊 " + "".join(random.choice(bars) for _ in range(25))


class MainApp(App):
    def build(self):
        return SignalUI()


MainApp().run()
