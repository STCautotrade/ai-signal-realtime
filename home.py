from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from datetime import datetime, timedelta

from api import fetch_signal


class Home(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)

        self.history = []
        self.expiry_time = None

        root = BoxLayout(orientation="vertical", spacing=6, padding=6)
        self.add_widget(root)

        # =========================
        # TITLE PNG
        # =========================
        root.add_widget(
            Image(
                source="file_00000000989c71fa995c0bb4f763659a.png",
                size_hint_y=None,
                height=120
            )
        )

        # =========================
        # MARKET + JAM
        # =========================
        self.market_label = Label(
            text="MARKET | WIB",
            size_hint_y=None,
            height=30,
            font_size=16
        )
        root.add_widget(self.market_label)

        # =========================
        # SIGNAL CARD NEON
        # =========================
        self.signal_label = Label(
            text="SIGNAL: WAITING",
            font_size=26,
            size_hint_y=None,
            height=70
        )

        self.status_label = Label(
            text="STATUS: -",
            size_hint_y=None,
            height=30
        )

        self.timer_label = Label(
            text="TIMER: WAITING",
            size_hint_y=None,
            height=30
        )

        root.add_widget(self.signal_label)
        root.add_widget(self.status_label)
        root.add_widget(self.timer_label)

        # =========================
        # HISTORY HEADER (7 KOLOM)
        # =========================
        header = BoxLayout(size_hint_y=None, height=30)

        headers = ["SIGNAL", "TIME", "STATUS", "K1", "K2", "K3", "K4"]

        for h in headers:
            header.add_widget(Label(text=h, font_size=12))

        root.add_widget(header)

        # =========================
        # HISTORY SCROLL
        # =========================
        self.scroll = ScrollView()

        self.history_box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=2
        )

        self.history_box.bind(minimum_height=self.history_box.setter("height"))

        self.scroll.add_widget(self.history_box)
        root.add_widget(self.scroll)

        # =========================
        # LOOP
        # =========================
        Clock.schedule_interval(self.update_data, 2)
        Clock.schedule_interval(self.update_timer, 1)

    # =========================
    # UPDATE DATA VPS
    # =========================
    def update_data(self, dt):

        data = fetch_signal()

        signal = data.get("signal", "WAITING")
        entry = data.get("entry_time", "-")

        # =========================
        # NEON COLOR SIGNAL
        # =========================
        if signal == "BUY":
            self.signal_label.text = "🟢 SIGNAL: BUY"
            self.signal_label.color = (0, 1, 0, 1)

        elif signal == "SELL":
            self.signal_label.text = "🔴 SIGNAL: SELL"
            self.signal_label.color = (1, 0, 0, 1)

        else:
            self.signal_label.text = "⚪ SIGNAL: WAITING"
            self.signal_label.color = (1, 1, 1, 1)

        self.status_label.text = "STATUS: ACTIVE"

        # =========================
        # TIMER 1 MENIT
        # =========================
        if signal in ["BUY", "SELL"] and entry != "-":
            try:
                h, m = map(int, entry.split(":"))
                base = datetime.now().replace(hour=h, minute=m, second=0)
                self.expiry_time = base + timedelta(minutes=1)
            except:
                self.expiry_time = datetime.now() + timedelta(seconds=60)

        # =========================
        # HISTORY ROW (7 KOLOM NEON)
        # =========================
        k1, k2, k3, k4 = "-", "-", "-", "-"

        row = BoxLayout(size_hint_y=None, height=28, spacing=2)

        row_data = [
            signal,
            entry,
            "ACTIVE",
            k1, k2, k3, k4
        ]

        for i, d in enumerate(row_data):

            lbl = Label(text=str(d), font_size=11)

            # neon style simple
            if signal == "BUY":
                lbl.color = (0, 1, 0, 1)

            elif signal == "SELL":
                lbl.color = (1, 0, 0, 1)

            else:
                lbl.color = (0.8, 0.8, 0.8, 1)

            row.add_widget(lbl)

        # prevent duplicate spam
        if not self.history or self.history[0] != row_data:
            self.history.insert(0, row_data)
            self.history_box.add_widget(row)

    # =========================
    # TIMER
    # =========================
    def update_timer(self, dt):

        if not self.expiry_time:
            self.timer_label.text = "TIMER: WAITING SIGNAL"
            return

        remaining = int((self.expiry_time - datetime.now()).total_seconds())

        if remaining <= 0:
            self.timer_label.text = "TIMER: EXPIRED"
            self.status_label.text = "STATUS: EXPIRED"
            self.expiry_time = None
        else:
            self.timer_label.text = f"TIMER: {remaining}s"
