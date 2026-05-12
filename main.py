import requests
import time
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Line
from datetime import datetime


DATA_URL = "http://157.10.252.46:5000/signal"


# ======================
# ENTRY BOX (RGB EFFECT)
# ======================
class EntryBox(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=15, **kwargs)

        self.size_hint_y = None
        self.height = 160

        self.mode = "WAIT"

        with self.canvas.before:
            self.color = Color(0.2, 0.2, 0.2, 1)
            self.bg = RoundedRectangle(radius=[20])

        # RGB LINE (ANIMATED BORDER)
        with self.canvas.after:
            self.line_color = Color(0, 1, 0, 1)
            self.border = Line(rounded_rectangle=(0, 0, 0, 0, 20), width=2)

        self.bind(pos=self.update_graphics, size=self.update_graphics)

        self.label_title = Label(text="MENUNGGU SIGNAL .....", font_size=28, bold=True)
        self.label_time = Label(text="-", font_size=18)

        self.add_widget(self.label_title)
        self.add_widget(self.label_time)

        Clock.schedule_interval(self.rgb_animation, 0.1)

    # ======================
    # UPDATE POSITION
    # ======================
    def update_graphics(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

        self.border.rounded_rectangle = (
            self.x, self.y, self.width, self.height, 20
        )

    # ======================
    # RGB ANIMATION SIMULATION
    # ======================
    def rgb_animation(self, dt):

        if self.mode == "BUY":
            self.line_color.rgba = (0, 1, 0, 1)

        elif self.mode == "SELL":
            self.line_color.rgba = (1, 0, 0, 1)

        else:
            # cycling RGB effect
            t = time.time()
            r = abs((time.time() % 3) - 1.5) / 1.5
            g = abs((time.time() % 2) - 1) / 1
            b = abs((time.time() % 4) - 2) / 2
            self.line_color.rgba = (r, g, b, 1)


# ======================
# MAIN APP
# ======================
class SignalUI(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=10, spacing=10, **kwargs)

        # 🔥 BACKGROUND ABU-ABU FIX
        Window.clearcolor = (0.12, 0.12, 0.14, 1)

        self.history = []

        # ======================
        # TITLE
        # ======================
        self.title = Label(
            text="🚀 AI SIGNAL PRO",
            font_size=40,
            bold=True,
            size_hint_y=None,
            height=60,
            color=(0.2, 0.8, 1, 1)
        )
        self.add_widget(self.title)

        # ======================
        # CLOCK
        # ======================
        self.clock = Label(text="00:00:00", font_size=36, size_hint_y=None, height=50)
        self.add_widget(self.clock)

        # ======================
        # MARKET
        # ======================
        self.market = Label(text="MARKET: -", size_hint_y=None, height=30)
        self.add_widget(self.market)

        # ======================
        # ENTRY BOX (🔥 CORE)
        # ======================
        self.entry_box = EntryBox()
        self.add_widget(self.entry_box)

        # ======================
        # HISTORY
        # ======================
        self.history_label = Label(text="HISTORY:\n-", font_size=14)
        self.add_widget(self.history_label)

        Clock.schedule_interval(self.update_clock, 1)
        Clock.schedule_interval(self.load_signal, 1)

    # ======================
    # CLOCK
    # ======================
    def update_clock(self, dt):
        self.clock.text = datetime.now().strftime("%H:%M:%S")

    # ======================
    # LOAD SIGNAL
    # ======================
    def load_signal(self, dt):

        try:
            r = requests.get(DATA_URL + "?t=" + str(time.time()), timeout=5)
            data = r.json()

            signal = data.get("signal", "WAITING")
            market = data.get("market", "-")
            entry_time = data.get("entry_time", "-")

            self.market.text = f"MARKET: {market}"

            # ======================
            # BUY
            # ======================
            if signal.upper() == "BUY":

                self.entry_box.mode = "BUY"

                self.entry_box.label_title.text = "ENTRY BUY"
                self.entry_box.label_time.text = f"ENTRY BUY DI JAM {entry_time}"

                self.history.insert(0, f"BUY - {entry_time}")

            # ======================
            # SELL
            # ======================
            elif signal.upper() == "SELL":

                self.entry_box.mode = "SELL"

                self.entry_box.label_title.text = "ENTRY SELL"
                self.entry_box.label_time.text = f"ENTRY SELL DI JAM {entry_time}"

                self.history.insert(0, f"SELL - {entry_time}")

            # ======================
            # WAIT
            # ======================
            else:

                self.entry_box.mode = "WAIT"

                self.entry_box.label_title.text = "MENUNGGU SIGNAL ....."
                self.entry_box.label_time.text = "-"

            self.history_label.text = "HISTORY:\n" + "\n".join(self.history[:6])

        except Exception as e:
            print("ERROR:", e)
            self.entry_box.label_title.text = "OFFLINE"


class MainApp(App):

    def build(self):
        return SignalUI()


if __name__ == "__main__":
    MainApp().run()
