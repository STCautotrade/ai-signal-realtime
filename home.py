import os
from datetime import datetime

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle, Line

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView

from api import fetch_signal


BASE_DIR=os.path.dirname(__file__)


# =========================
# CARD
# =========================

class Card(BoxLayout):

    def __init__(
        self,
        bg=(0.15,0.15,0.15,1),
        border=(0,0.8,1,1),
        h=70,
        radius=18,
        **kw
    ):

        super().__init__(**kw)

        self.orientation="vertical"
        self.padding=dp(6)
        self.spacing=dp(4)

        self.size_hint_y=None
        self.height=dp(h)

        self.rad=radius

        with self.canvas.before:

            self.bg=Color(*bg)

            self.rect=RoundedRectangle(
                radius=[self.rad]
            )

        with self.canvas.after:

            self.border=Color(*border)

            self.line=Line(
                rounded_rectangle=(
                    0,0,0,0,self.rad
                ),
                width=1.3
            )

        self.bind(
            pos=self.update_ui,
            size=self.update_ui
        )


    def update_ui(self,*a):

        self.rect.pos=self.pos
        self.rect.size=self.size

        self.line.rounded_rectangle=(

            self.x,
            self.y,
            self.width,
            self.height,
            self.rad

        )


    def set_bg(self,c):
        self.bg.rgba=c



# =========================
# HISTORY ROW
# =========================

class HistoryRow(Card):

    def __init__(
        self,
        text,
        color
    ):

        super().__init__(
            h=38,
            bg=color
        )

        self.add_widget(

            Label(
                text=text,
                font_size=dp(10)
            )

        )



# =========================
# HOME
# =========================

class Home(Screen):

    def __init__(self,**kw):

        super().__init__(**kw)

        self.saved=""


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
                    "IMG_20260515_104812.png"
                ),

                size_hint_y=None,

                height=dp(90)

            )

        )


        # TOP CARD

        row=BoxLayout(
            spacing=dp(6),
            size_hint_y=None,
            height=dp(55)
        )


        market=Card(h=55)

        market.add_widget(
            Label(
                text="CRYPTO IDX 85%"
            )
        )


        jam=Card(h=55)

        self.clock=Label(
            text="00:00:00 WIB"
        )

        jam.add_widget(
            self.clock
        )


        row.add_widget(market)
        row.add_widget(jam)

        root.add_widget(row)


        # SIGNAL

        self.signal_card=Card(
            h=160,
            radius=35,
            bg=(0.5,0.5,0.5,1)
        )


        self.signal_card.add_widget(

            Label(
    text="SIGNAL REALTIME KONFIGURATION",
    bold=True
            )

        )


        self.signal_text=Label(
            text="SIGNAL EXPIRED"
        )

        self.signal_status=Label(
            text="WAITING"
        )


        self.signal_card.add_widget(
            self.signal_text
        )

        self.signal_card.add_widget(
            self.signal_status
        )

        root.add_widget(
            self.signal_card
        )


        # TIMER

        timer=Card(h=50)

        self.timer=Label(
            text="MENUNGGU SIGNAL"
        )

        timer.add_widget(
            self.timer
        )

        root.add_widget(
            timer
        )


        # HISTORY

        root.add_widget(

            Label(
                text="HISTORY SIGNAL",
                size_hint_y=None,
                height=dp(22)
            )

        )


        scroll=ScrollView(
            size_hint_y=None,
            height=dp(300)
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
            self.update_clock,
            1
        )

        Clock.schedule_interval(
            self.load,
            1
        )


    # =========================

    def update_clock(
        self,
        dt
    ):

        self.clock.text=(

            datetime.now().strftime(
                "%H:%M:%S WIB"
            )

        )


    # =========================

    def add_history(
        self,
        text,
        color
    ):

        if text==self.saved:
            return

        self.saved=text


        self.history_box.add_widget(

            HistoryRow(
                text,
                color
            ),

            index=0

        )


        while len(
            self.history_box.children
        )>100:

            self.history_box.remove_widget(
                self.history_box.children[-1]
            )


    # =========================

    def load(self,dt):

        data=fetch_signal()

        signal=data.get(
            "signal",
            "WAITING"
        ).upper()

        entry=data.get(
            "entry_time",
            "-"
        )


        now=datetime.now()


        try:

            h,m=map(
                int,
                entry.split(":")
            )

            now_sec=(
                now.hour*3600+
                now.minute*60+
                now.second
            )

            expire_sec=(
                h*3600+
                m*60+
                60
            )

            remain=(
                expire_sec-
                now_sec
            )

            expired=remain<=0

            if remain<0:
                remain=0

        except:

            remain=0
            expired=False


        if signal in [
            "BUY",
            "SELL"
        ]:

            if expired:

                self.timer.text=(
                    "TIMER : MENUNGGU SIGNAL"
                )

            else:

                self.timer.text=(

                    f"TIMER : {remain}s"

                )

        else:

            self.timer.text=(
                "MENUNGGU SIGNAL"
            )


        # BUY

        if signal=="BUY":

            if expired:

                self.signal_text.text=(
                    "SIGNAL BUY EXPIRED"
                )

                self.signal_status.text=(
                    "WAITING"
                )

                self.signal_card.set_bg(
                    (.5,.5,.5,1)
                )

                self.add_history(

                    f"SIGNAL BUY {entry} BERAKHIR",

                    (0,0.4,0,0.5)

                )

            else:

                self.signal_text.text=(

                    f"ENTRY BUY DI JAM {entry}"

                )

                self.signal_status.text=(
                    "ACTIVE"
                )

                self.signal_card.set_bg(
                    (0,.7,0,1)
                )


        # SELL

        elif signal=="SELL":

            if expired:

                self.signal_text.text=(
                    "SIGNAL SELL EXPIRED"
                )

                self.signal_status.text=(
                    "WAITING"
                )

                self.signal_card.set_bg(
                    (.5,.5,.5,1)
                )

                self.add_history(

                    f"SIGNAL SELL {entry} BERAKHIR",

                    (0.5,0,0,0.5)

                )

            else:

                self.signal_text.text=(

                    f"ENTRY SELL DI JAM {entry}"

                )

                self.signal_status.text=(
                    "ACTIVE"
                )

                self.signal_card.set_bg(
                    (.8,0,0,1)
    )
