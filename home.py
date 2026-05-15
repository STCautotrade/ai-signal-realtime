import os
from datetime import datetime, timedelta

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle, Line

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView

from api import fetch_signal


BASE_DIR = os.path.dirname(__file__)


# ===================================
# CARD NEON
# ===================================

class Card(BoxLayout):

    def __init__(
        self,
        bg=(0.08,0.08,0.12,1),
        border=(0.2,0.7,1,1),
        h=70,
        **kw
    ):

        super().__init__(**kw)

        self.orientation="vertical"
        self.padding=dp(6)
        self.spacing=dp(4)

        self.size_hint_y=None
        self.height=dp(h)

        with self.canvas.before:

            self.bg=Color(*bg)

            self.rect=RoundedRectangle(
                radius=[18]
            )

        with self.canvas.after:

            self.border=Color(*border)

            self.line=Line(
                rounded_rectangle=(0,0,0,0,18),
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
            18

        )


    def set_bg(self,c):

        self.bg.rgba=c



# ===================================
# HISTORY
# ===================================

class HistoryRow(Card):

    def __init__(self,text,color):

        super().__init__(
            h=40,
            bg=(0.05,0.08,0.12,1)
        )

        lbl=Label(

            text=text,

            font_size=dp(10),

            color=color

        )

        self.add_widget(lbl)



# ===================================
# HOME
# ===================================

class Home(Screen):

    def __init__(self,**kw):

        super().__init__(**kw)

        self.history=[]
        self.last=""
        self.expiry_time=None

        root=BoxLayout(
            orientation="vertical",
            spacing=dp(6),
            padding=dp(6)
        )

        self.add_widget(root)


        # =====================
        # PNG TITLE
        # =====================

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


        # =====================
        # MARKET + JAM
        # =====================

        row=BoxLayout(

            spacing=dp(6),

            size_hint_y=None,

            height=dp(65)

        )


        market=Card(h=60)

        market.add_widget(
            Label(
                text="MARKET"
            )
        )

        self.market_label=Label(
            text="-"
        )

        market.add_widget(
            self.market_label
        )


        jam=Card(h=60)

        jam.add_widget(
            Label(
                text="JAM REALTIME HP WIB"
            )
        )

        self.clock=Label(
            text="00:00:00"
        )

        jam.add_widget(
            self.clock
        )

        row.add_widget(
            market
        )

        row.add_widget(
            jam
        )

        root.add_widget(
            row)


        # =====================
        # SIGNAL
        # =====================

        self.signal_card=Card(
            h=155
        )


        title=Label(

            text="SIGNAL AREA ( KONFIGURATION SIGNAL )",

            bold=True

        )

        self.signal_text=Label(

            text="MENUNGGU SIGNAL",

            halign="center"

        )

        self.signal_text.bind(

            width=lambda s,w:
            setattr(
                s,
                "text_size",
                (w-20,None)
            )

        )


        self.status=Label(

            text="STATUS: EXPIRED"

        )


        self.signal_card.add_widget(
            title
        )

        self.signal_card.add_widget(
            self.signal_text
        )

        self.signal_card.add_widget(
            self.status
        )

        root.add_widget(
            self.signal_card
        )


        # =====================
        # TIMER
        # =====================

        timer=Card(h=55)

        self.timer=Label(
            text="TIMER: MENUNGGU SIGNAL"
        )

        timer.add_widget(
            self.timer
        )

        root.add_widget(
            timer
        )


        # =====================
        # HISTORY
        # =====================

        root.add_widget(

            Label(
                text="HISTORY HEADER",
                size_hint_y=None,
                height=dp(20)
            )

        )


        scroll=ScrollView()

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
            self.update_clock,
            1
        )

        Clock.schedule_interval(
            self.update_timer,
            1
        )


    # =====================
    # JAM HP
    # =====================

    def update_clock(self,dt):

        self.clock.text=(
            datetime.now().strftime(
                "%H:%M:%S WIB"
            )
        )


    # =====================
    # TIMER
    # =====================

    def update_timer(self,dt):

        if not self.expiry_time:

            self.timer.text=(
                "TIMER: MENUNGGU SIGNAL"
            )

            return


        sec=int(
            (
                self.expiry_time-
                datetime.now()
            ).total_seconds()
        )


        if sec<0:
            sec=0


        self.timer.text=(
            f"TIMER: {sec}s"
        )


    # =====================
    # API
    # =====================

    def load(self,dt):

        data=fetch_signal()

        signal=data["signal"].upper()

        entry=data["entry_time"]

        market=data["market"]

        status=data["status"]


        self.market_label.text=(
            market.upper()
        )


        try:

            h,m=map(
                int,
                entry.split(":")
            )

            self.expiry_time=(

                datetime.now().replace(

                    hour=h,

                    minute=m,

                    second=0

                )

                +

                timedelta(
                    minutes=1
                )

            )

        except:
            pass


        if signal=="BUY":

            self.signal_card.set_bg(
                (0,0.6,0,.35)
            )

            self.signal_text.text=(

                f"SIGNAL: ENTRY BUY DI JAM {entry}"

            )

            color=(0,1,0,1)


        elif signal=="SELL":

            self.signal_card.set_bg(
                (0.6,0,0,.35)
            )

            self.signal_text.text=(

                f"SIGNAL: ENTRY SELL DI JAM {entry}"

            )

            color=(1,0,0,1)

        else:

            self.signal_card.set_bg(
                (0.08,0.08,0.12,1)
            )

            self.signal_text.text=(

                "SIGNAL BUY BERAKHIR / SIGNAL SELL BERAKHIR"

            )

            color=(1,1,1,1)


        self.status.text=(
            f"STATUS: {status}"
        )


        hist=(
            f"{signal} | JAM {entry} | {status}"
        )


        if hist!=self.last:

            self.last=hist

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


            if len(
                self.history
            )>100:

                self.history.pop()
