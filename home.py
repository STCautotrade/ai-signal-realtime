import requests
from datetime import datetime, timedelta
import os

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen
from kivy.graphics import Color, RoundedRectangle, Line

DATA_URL = "http://157.10.252.46:5000/signal"
BASE_DIR = os.path.dirname(__file__)


# =========================
# CARD NEON
# =========================

class Card(BoxLayout):

    def __init__(
        self,
        bg=(0.08,0.08,0.12,1),
        border=(0.2,0.7,1,1),
        h=90,
        **kwargs
    ):

        super().__init__(**kwargs)

        self.orientation="vertical"

        self.padding=dp(6)
        self.spacing=dp(4)

        self.size_hint_y=None
        self.height=dp(h)

        with self.canvas.before:

            self.bg=Color(*bg)

            self.rect=RoundedRectangle(
                radius=[16]
            )

        with self.canvas.after:

            self.border=Color(*border)

            self.line=Line(
                rounded_rectangle=(0,0,0,0,16),
                width=1.2
            )

        self.bind(
            pos=self.update,
            size=self.update
        )


    def update(self,*a):

        self.rect.pos=self.pos
        self.rect.size=self.size

        self.line.rounded_rectangle=(
            self.x,
            self.y,
            self.width,
            self.height,
            16
        )


    def set_bg(self,c):

        self.bg.rgba=c



# =========================
# HISTORY ROW
# =========================

class HistoryRow(Card):

    def __init__(self,text,color,**kw):

        super().__init__(
            h=38,
            bg=(0.08,0.08,0.12,1)
        )

        lbl=Label(
            text=text,
            font_size=dp(10),
            color=color
        )

        self.add_widget(lbl)



# =========================
# HOME
# =========================

class Home(Screen):

    def __init__(self,**kw):

        super().__init__(**kw)

        self.history=[]
        self.expiry_time=None
        self.last_signal=""

        root=BoxLayout(
            orientation="vertical",
            spacing=dp(6),
            padding=dp(6)
        )

        self.add_widget(root)

        # PNG

        root.add_widget(

            Image(

                source=os.path.join(
                    BASE_DIR,
                    "file_00000000989c71fa995c0bb4f763659a.png"
                ),

                size_hint_y=None,

                height=dp(100)

            )

        )


        # MARKET + JAM

        row=BoxLayout(

            size_hint_y=None,

            height=dp(60),

            spacing=dp(5)

        )


        self.market=Card(h=55)

        self.market.add_widget(
            Label(
                text="MARKET"
            )
        )

        self.market_label=Label(
            text="CRYPTO IDX"
        )

        self.market.add_widget(
            self.market_label
        )



        self.clock=Card(h=55)

        self.clock.add_widget(
            Label(
                text="JAM REALTIME HP WIB"
            )
        )

        self.clock_label=Label(
            text="00:00:00"
        )

        self.clock.add_widget(
            self.clock_label
        )



        row.add_widget(
            self.market
        )

        row.add_widget(
            self.clock
        )

        root.add_widget(row)


        # SIGNAL

        self.signal=Card(
            h=145
        )


        self.signal_title=Label(

            text="SIGNAL AREA ( KONFIGURATION SIGNAL )",

            bold=True

        )


        self.entry=Label(

            text="SIGNAL: ENTRY BUY DI JAM ..../ ENTRY SELL DI JAM .... / SIGNAL BUY BERAKHIR / SIGNAL SELL BERAKHIR",

            halign="center"

        )

        self.entry.bind(
            width=lambda s,w:
            setattr(
                s,
                "text_size",
                (w-20,None)
            )
        )


        self.status=Label(
            text="STATUS: ACTIVE/EXVIRED"
        )


        self.signal.add_widget(
            self.signal_title
        )

        self.signal.add_widget(
            self.entry
        )

        self.signal.add_widget(
            self.status
        )

        root.add_widget(
            self.signal
        )


        # TIMER

        self.expire_card=Card(
            h=60
        )

        self.expire_label=Label(
            text="TIMER: 55s / MENUNGGU SIGNAL"
        )

        self.expire_card.add_widget(
            self.expire_label
        )

        root.add_widget(
            self.expire_card
        )


        # HISTORY

        root.add_widget(

            Label(
                text="HISTORY HEADER",
                size_hint_y=None,
                height=dp(20)
            )

        )


        scroll=ScrollView(
            size_hint=(1,1)
        )

        self.history_box=BoxLayout(

            orientation="vertical",

            spacing=dp(4),

            size_hint_y=None

        )

        self.history_box.bind(
            minimum_height=
            self.history_box.setter(
                "height"
            )
        )


        scroll.add_widget(
            self.history_box
        )

        root.add_widget(
            scroll
        )


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


    def update_expiry(self,dt):

        if not self.expiry_time:

            self.expire_label.text=(
                "TIMER: MENUNGGU SIGNAL"
            )

            return


        s=int(
            (
                self.expiry_time-
                datetime.now()
            ).total_seconds()
        )


        if s<0:
            s=0


        self.expire_label.text=(
            f"TIMER: {s}s"
        )


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

            market=data.get(
                "market",
                "CRYPTO IDX"
            )


            self.market_label.text=(
                market.upper()
            )


            if signal=="BUY":

                self.signal.set_bg(
                    (0,0.5,0,0.35)
                )

                self.entry.text=(
                    f"SIGNAL: ENTRY BUY DI JAM {entry} / SIGNAL BUY BERAKHIR"
                )

                self.status.text=(
                    "STATUS: ACTIVE"
                )

                color=(0,1,0,1)


            elif signal=="SELL":

                self.signal.set_bg(
                    (0.5,0,0,0.35)
                )

                self.entry.text=(
                    f"SIGNAL: ENTRY SELL DI JAM {entry} / SIGNAL SELL BERAKHIR"
                )

                self.status.text=(
                    "STATUS: ACTIVE"
                )

                color=(1,0,0,1)

            else:

                self.signal.set_bg(
                    (0.08,0.08,0.12,1)
                )

                self.entry.text=(
                    "SIGNAL EXPIRED"
                )

                self.status.text=(
                    "STATUS: EXVIRED"
                )

                color=(1,1,1,1)


            hist=f"{signal} | JAM {entry} | EXPIRED"


            if hist not in self.history:

                self.history.insert(
                    0,
                    hist
                )

                self.history_box.add_widget(

                    HistoryRow(
                        hist,
                        color
                    ),

                    index=0
                )


        except:

            self.entry.text="OFFLINE"
            self.status.text="SERVER ERROR"
