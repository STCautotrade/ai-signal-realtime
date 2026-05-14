from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from datetime import datetime

from api import fetch_signal


class Home(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)

        # ======================
        # ROOT LAYOUT
        # ======================
        self.root = BoxLayout(orientation="vertical", spacing=5, padding=5)
        self.add_widget(self.root)

        # ======================
        # TITLE
        # ======================
        self.title = Label(
            text="AI SIGNAL HOME",
            font_size=22,
            size_hint_y=None,
            height=40
        )
        self.root.add_widget(self.title)

        # ======================
        # MARKET LABEL
        # ======================
        self.market_label = Label(
            text="MARKET: -",
            font_size=16,
            size_hint_y=None,
            height=30
        )
        self.root.add_widget(self.market_label)

        # ======================
        # SIGNAL DISPLAY
        # ======================
        self.signal_label = Label(
            text="WAITING SIGNAL...",
            font_size=18
        )
        self.root.add_widget(self.signal_label)

        # ======================
        # ENTRY TIME
        # ======================
        self.entry_label = Label(
            text="ENTRY: -",
            font_size=16,
            size_hint_y=None,
            height=30
        )
        self.root.add_widget(self.entry_label)

        # ======================
        # CLOCK
        # ======================
        self.clock_label = Label(
            text="00:00:00",
            font_size=16,
            size_hint_y=None,
            height=30
        )
        self.root.add_widget(self.clock_label)

        # ======================
        # START LOOP
        # ======================
        Clock.schedule_interval(self.update_data, 2)
        Clock.schedule_interval(self.update_clock, 1)

    # ======================
    # CLOCK
    # ======================
    def update_clock(self, dt):
        self.clock_label.text = datetime.now().strftime("%H:%M:%S")

    # ======================
    # FETCH VPS DATA
    # ======================
    def update_data(self, dt):
        data = fetch_signal()

        signal = data.get("signal", "WAITING")
        entry = data.get("entry_time", "-")
        market = data.get("market", "-")

        self.market_label.text = f"MARKET: {market}"
        self.signal_label.text = f"SIGNAL: {signal}"
        self.entry_label.text = f"ENTRY: {entry}"
