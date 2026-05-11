import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from datetime import datetime

# =========================
# LINK SIGNAL JSON
# =========================

DATA_URL = "https://raw.githubusercontent.com/STCautotrade/ai-signal-realtime/main/signal.json"

class SignalUI(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(
            orientation='vertical',
            padding=20,
            spacing=20,
            **kwargs
        )

        # TITLE
        self.title = Label(
            text="AI SIGNAL REALTIME",
            font_size=32,
            bold=True
        )
        self.add_widget(self.title)

        # MARKET
        self.market = Label(
            text="MARKET",
            font_size=24
        )
        self.add_widget(self.market)

        # JAM
        self.clock_label = Label(
            text="00:00:00",
            font_size=28
        )
        self.add_widget(self.clock_label)

        # INFO
        self.info = Label(
            text="Loading...",
            font_size=18
        )
        self.add_widget(self.info)

        # SIGNAL
        self.signal = Label(
            text="WAITING...",
            font_size=42,
            bold=True
        )
        self.add_widget(self.signal)

        # UPDATE
        Clock.schedule_interval(self.update_clock, 1)
        Clock.schedule_interval(self.load_signal, 5)

    # =========================
    # JAM REALTIME
    # =========================
    def update_clock(self, dt):
        now = datetime.now().strftime("%H:%M:%S")
        self.clock_label.text = f"🕒 {now}"

    # =========================
    # LOAD SIGNAL
    # =========================
    def load_signal(self, dt):

        try:
            response = requests.get(DATA_URL)
            data = response.json()

            market = data["market"]
            signal = data["signal"]
            entry = data["entry_time"]
            message = data["message"]

            # MARKET
            self.market.text = f"📊 {market}"

            # INFO
            self.info.text = message

            # SIGNAL
            if signal == "BUY":
                self.signal.text = "🟢 BUY NOW"

            elif signal == "SELL":
                self.signal.text = "🔴 SELL NOW"

            else:
                self.signal.text = "WAITING..."

        except:
            self.signal.text = "ERROR"

class MainApp(App):

    def build(self):
        return SignalUI()

MainApp().run()
