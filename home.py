from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from datetime import datetime, timedelta
from time import strftime

from api import fetch_signal


class Home(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)

        self.history = []
        self.expiry_time = None

        root = BoxLayout(orientation="vertical", spacing=6, padding=6)
        self.add_widget(root)

        # =========================
        # TITLE IMAGE
        # =========================
        root.add_widget(
            Image(
                source="file_00000000989c71fa995c0bb4f763659a.png",
                size_hint_y=None,
                height=120
            )
        )

        # =========================
        # MARKET + JAM (FIX: MARKET VPS, JAM HP)
        # =========================
        self.market_label = Label(
            text="MARKET LOADING...",
            size_hint_y=None,
            height=30,
            font_size=16
        )
        root.add_widget(self.market_label)

        # =========================
        # SIGNAL AREA
        # =========================
        self.signal_label = Label(
            text="SIGNAL: ENTRY BUY DI JAM ..../ ENTRY SELL DI JAM .... / SIGNAL BUY BERAKHIR / SIGNAL SELL BERAKHIR",
            font_size=18,
            size_hint_y=None,
            height=80
        )

        self.status_label = Label(
            text="STATUS: ACTIVE/EXVIRED",
            size_hint_y=None,
            height=30
        )

        self.card = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=120
        )

        self.card.add_widget(self.signal_label)
        self.card.add_widget(self.status_label)

        root.add_widget(self.card)

        # =========================
        # TIMER
        # =========================
        self.timer_label = Label(
            text="TIMER: 55s / MENUNGGU SIGNAL",
            size_hint_y=None,
            height=30
        )
        root.add_widget(self.timer_label)

        # =========================
        # HISTORY HEADER
        # =========================
        header = BoxLayout(size_hint_y=None, height=30)

        headers = ["SIGNAL", "TIME", "STATUS"]

        for h in headers:
            header.add_widget(Label(text=h))

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
        market = data.get("market", "CRYPTO IDX")

        # =========================
        # MARKET + JAM HP REALTIME
        # =========================
        self.market_label.text = f"{market} | {strftime('%H:%M:%S')}"

        # =========================
        # SIGNAL DISPLAY (NO CHANGE TEXT)
        # =========================
        if signal == "BUY":
            self.signal_label.text = "SIGNAL: ENTRY BUY DI JAM ..../ SIGNAL BUY BERAKHIR"
            self.signal_label.color = (0, 1, 0, 1)

        elif signal == "SELL":
            self.signal_label.text = "SIGNAL: ENTRY SELL DI JAM ..../ SIGNAL SELL BERAKHIR"
            self.signal_label.color = (1, 0, 0, 1)

        else:
            self.signal_label.text = "SIGNAL: ENTRY BUY DI JAM ..../ ENTRY SELL DI JAM .... / SIGNAL BUY BERAKHIR / SIGNAL SELL BERAKHIR"
            self.signal_label.color = (1, 1, 1, 1)

        # =========================
        # STATUS
        # =========================
        if signal in ["BUY", "SELL"]:
            self.status_label.text = "STATUS: ACTIVE"
        else:
            self.status_label.text = "STATUS: EXVIRED"

        # =========================
        # TIMER LOGIC
        # =========================
        if signal in ["BUY", "SELL"] and entry != "-":
            try:
                h, m = map(int, entry.split(":"))
                base = datetime.now().replace(hour=h, minute=m, second=0)
                self.expiry_time = base + timedelta(seconds=55)
            except:
                self.expiry_time = datetime.now() + timedelta(seconds=55)
        else:
            self.expiry_time = None

        # =========================
        # HISTORY (NO DUPLICATE)
        # =========================
        row_data = [signal, entry, "ACTIVE" if self.expiry_time else "EXPIRED"]

        if self.history and self.history[0] == row_data:
            return

        self.history.insert(0, row_data)

        row = BoxLayout(size_hint_y=None, height=28)

        for d in row_data:

            lbl = Label(text=str(d))

            if signal == "BUY":
                lbl.color = (0, 1, 0, 1)
            elif signal == "SELL":
                lbl.color = (1, 0, 0, 1)
            else:
                lbl.color = (1, 1, 1, 1)

            row.add_widget(lbl)

        self.history_box.add_widget(row)

    # =========================
    # TIMER
    # =========================
    def update_timer(self, dt):

        if not self.expiry_time:
            self.timer_label.text = "TIMER: 55s / MENUNGGU SIGNAL"
            return

        remaining = int((self.expiry_time - datetime.now()).total_seconds())

        if remaining <= 0:
            self.timer_label.text = "TIMER: EXPIRED"
            self.status_label.text = "STATUS: EXVIRED"
            self.expiry_time = None
        else:
            self.timer_label.text = f"TIMER: {remaining}s / MENUNGGU SIGNAL"
