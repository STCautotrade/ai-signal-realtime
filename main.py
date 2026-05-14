import requests
from datetime import datetime, timedelta
import webbrowser
import os

from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics import Color, RoundedRectangle, Line


DATA_URL = "http://157.10.252.46:5000/signal"
BASE_DIR = os.path.dirname(__file__)


# =========================
# CARD NEON
# =========================
class Card(BoxLayout):
    def __init__(self,
                 bg=(0.03,0.05,0.09,1),
                 border=(0,1,1,1),
                 h=90,
                 **kwargs):

        super().__init__(**kwargs)

        self.orientation="vertical"
        self.padding=dp(8)
        self.spacing=dp(4)
        self.size_hint_y=None
        self.height=dp(h)

        with self.canvas.before:
            self.bg=Color(*bg)
            self.rect=RoundedRectangle(radius=[18])

        with self.canvas.after:
            self.border=Color(*border)

            self.line=Line(
                rounded_rectangle=(0,0,0,0,18),
                width=1.8
            )

        self.bind(
            pos=self.update,
            size=self.update
        )

    def update(self,*args):

        self.rect.pos=self.pos
        self.rect.size=self.size

        self.line.rounded_rectangle=(
            *self.pos,
            *self.size,
            18
        )

    def set_bg(self,c):
        self.bg.rgba=c


# =========================
# HISTORY
# =========================
class HistoryRow(Card):

    def __init__(self,text):

        super().__init__(
            h=30,
            bg=(0.08,0.08,0.12,1)
        )

        self.label=Label(
            text=text,
            font_size=dp(9)
        )

        self.add_widget(self.label)


# =========================
# HOME
# =========================
class Home(Screen):

    def __init__(self,**kw):

        super().__init__(**kw)

        root=BoxLayout(
            orientation="vertical",
            spacing=dp(5),
            padding=dp(6)
        )

        root.add_widget(
            Image(
                source=os.path.join(
                    BASE_DIR,
                    "file_00000000989c71fa995c0bb4f763659a.png"
                ),
                size_hint_y=None,
                height=dp(140)
            )
        )

        row=BoxLayout(
            size_hint_y=None,
            height=dp(50),
            spacing=dp(5)
        )

        self.market=Card(h=50)
        self.clock=Card(h=50)

        self.market_label=Label(
            text="CRYPTO IDX 85%",
            font_size=dp(11)
        )

        self.clock_label=Label(
            text="00:00:00 WIB",
            font_size=dp(11)
        )

        self.market.add_widget(
            self.market_label
        )

        self.clock.add_widget(
            self.clock_label
        )

        row.add_widget(self.market)
        row.add_widget(self.clock)

        root.add_widget(row)

        self.signal=Card(h=120)

        self.signal_label=Label(
            text="WAITING SIGNAL...",
            font_size=dp(18)
        )

        self.entry=Label(
            text="ENTRY : -",
            font_size=dp(12)
        )

        self.status=Label(
            text="SYSTEM STANDBY",
            font_size=dp(10)
        )

        self.signal.add_widget(self.signal_label)
        self.signal.add_widget(self.entry)
        self.signal.add_widget(self.status)

        root.add_widget(self.signal)

        self.expire_card=Card(
            h=70
        )

        self.expire_label=Label(
            text="WAITING SIGNAL...",
            font_size=dp(20),
            bold=True
        )

        self.expire_card.add_widget(
            self.expire_label
        )

        root.add_widget(
            self.expire_card
        )

        root.add_widget(
            Label(
                text="HISTORY",
                size_hint_y=None,
                height=dp(20)
            )
        )

        self.history_scroll=ScrollView(
            size_hint=(1,None),
            height=dp(220)
        )

        self.history_box=BoxLayout(
            orientation="vertical",
            spacing=dp(2),
            size_hint_y=None
        )

        self.history_box.bind(
            minimum_height=
            self.history_box.setter(
                "height"
            )
        )

        self.history_scroll.add_widget(
            self.history_box
        )

        root.add_widget(
            self.history_scroll
        )

        self.add_widget(root)

        self.history=[]
        self.expiry_time=None
        self.last_signal=""

        Clock.schedule_interval(
            self.load,
            2
        )

        Clock.schedule_interval(
            self.clock_update,
            1
        )

        Clock.schedule_interval(
            self.update_expiry,
            1
        )

    def clock_update(self,dt):

        self.clock_label.text=(
            datetime.now().strftime(
                "%H:%M:%S WIB"
            )
                     )
        def expired(self,t):

        try:
            return (
                datetime.now().strftime(
                    "%H:%M"
                )>t
            )

        except:
            return False


    # COUNTDOWN SIGNAL
    def update_expiry(self,dt):

        if not self.expiry_time:

            self.expire_label.text=(
                "MENUNGGU SIGNAL BERIKUTNYA"
            )

            return

        remaining=int(
            (
                self.expiry_time-
                datetime.now()
            ).total_seconds()
        )

        if remaining<0:
            remaining=0

        self.expire_label.text=(
            f"EXPIRED : {remaining:02d} DETIK"
        )

        if remaining==0:

            self.expire_label.text=(
                "MENUNGGU SIGNAL BERIKUTNYA"
            )

            self.expiry_time=None


    # LOAD SIGNAL
    def load(self,dt):

        try:

            data=requests.get(
                DATA_URL,
                timeout=5
            ).json()

            signal=data.get(
                "signal",
                "WAITING"
            ).upper()

            entry=data.get(
                "entry_time",
                "-"
            )

            if signal not in ["BUY","SELL"]:

                self.signal.set_bg(
                    (0.03,0.05,0.09,1)
                )

                self.signal_label.text=(
                    "WAITING SIGNAL..."
                )

                self.entry.text="-"

                self.status.text=(
                    "MENUNGGU KONFIRMASI"
                )

                hist=None

            elif signal=="BUY":

                self.signal.set_bg(
                    (0,0.6,0.3,1)
                )

                self.signal_label.text=(
                    "BUY NOW"
                )

                self.entry.text=(
                    f"ENTRY BUY DI JAM {entry}"
                )

                self.status.text="ACTIVE"

                signal_key=signal+entry

                if signal_key!=self.last_signal:

                    self.expiry_time=(
                        datetime.now()+
                        timedelta(seconds=60)
                    )

                    self.last_signal=signal_key

                hist=(
                    f"MARKET CRYPTO IDX : SIGNAL BUY JAM {entry}"
                )

            else:

                self.signal.set_bg(
                    (0.8,0.1,0.2,1)
                )

                self.signal_label.text=(
                    "SELL NOW"
                )

                self.entry.text=(
                    f"ENTRY SELL DI JAM {entry}"
                )

                self.status.text="ACTIVE"

                signal_key=signal+entry

                if signal_key!=self.last_signal:

                    self.expiry_time=(
                        datetime.now()+
                        timedelta(seconds=60)
                    )

                    self.last_signal=signal_key

                hist=(
                    f"MARKET CRYPTO IDX : SIGNAL SELL JAM {entry}"
                )

            if hist and (
                not self.history
                or self.history[0]!=hist
            ):

                self.history.insert(
                    0,
                    hist
                )

                row=HistoryRow(hist)

                if "BUY" in hist:

                    row.set_bg(
                        (0,1,0.3,0.2)
                    )

                else:

                    row.set_bg(
                        (1,0.2,0.2,0.2)
                    )

                self.history_box.add_widget(
                    row,
                    index=0
                )

        except:

            self.signal_label.text=(
                "OFFLINE"
            )

            self.status.text=(
                "SERVER ERROR"
            )


# =========================
# MARTINGALE SCROLL
# =========================
class Martingale(Screen):

    def __init__(self,**kw):

        super().__init__(**kw)

        root=BoxLayout(
            orientation="vertical",
            padding=dp(8),
            spacing=dp(6)
        )

        title=Card(h=60)

        title.add_widget(
            Label(
                text="MARTINGALE SYSTEM",
                font_size=dp(18),
                bold=True
            )
        )

        root.add_widget(title)

        btn=Button(
            text="HITUNG",
            size_hint_y=None,
            height=dp(45),
            background_normal="",
            background_color=(
                0,0.7,1,0.8
            )
        )

        btn.bind(
            on_press=self.calc
        )

        root.add_widget(btn)

        scroll=ScrollView()

        self.result_box=Card(
            h=1200
        )

        self.result=Label(
            text="Klik HITUNG",
            font_size=dp(12),
            halign="left",
            valign="top",
            text_size=(dp(300),None),
            size_hint_y=None
        )

        self.result.bind(
            texture_size=self.resize
        )

        self.result_box.add_widget(
            self.result
        )

        scroll.add_widget(
            self.result_box
        )

        root.add_widget(scroll)

        self.base=14000

        self.add_widget(root)

    def resize(self,*args):

        self.result.height=(
            self.result.texture_size[1]
            +dp(50)
        )

        self.result_box.height=(
            self.result.height
            +dp(40)
        )

    def calc(self,instance):

        mults=[2,2.5,3,4]

        out=""

        for m in mults:

            val=self.base

            out+=(
                f"\n==== X{m} ====\n"
            )

            for i in range(1,11):

                val*=m

                out+=(
                    f"K{i}: {int(val)}\n"
                )

        self.result.text=out


class AppMain(App):

    def build(self):

        sm=ScreenManager()

        home=Home(name="home")
        mart=Martingale(name="mart")

        sm.add_widget(home)
        sm.add_widget(mart)

        root=BoxLayout(
            orientation="vertical"
        )

        root.add_widget(sm)

        nav=BoxLayout(
            size_hint_y=None,
            height=dp(50)
        )

        nav.add_widget(
            Button(
                text="HOME",
                on_press=lambda x:
                sm.switch_to(home)
            )
        )

        nav.add_widget(
            Button(
                text="MART",
                on_press=lambda x:
                sm.switch_to(mart)
            )
        )

        nav.add_widget(
            Button(
                text="TRADE",
                on_press=lambda x:
                webbrowser.open(
                    "https://stcbroker.id"
                )
            )
        )

        root.add_widget(nav)

        return root


if __name__=="__main__":
    AppMain().run()
