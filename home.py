from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.clock import Clock
from time import strftime

from api import fetch_signal


class Card(BoxLayout):

    def __init__(
        self,
        bg=(0.05,0.08,0.12,.95),
        line=(0,1,1,1),
        **kwargs
    ):

        super().__init__(**kwargs)

        with self.canvas.before:

            Color(*bg)
            self.bg = RoundedRectangle(
                radius=[18]
            )

            Color(*line)
            self.border = Line(
                rounded_rectangle=(0,0,0,0,18),
                width=1.2
            )

        self.bind(pos=self.update_ui)
        self.bind(size=self.update_ui)

    def update_ui(self,*a):

        self.bg.pos=self.pos
        self.bg.size=self.size

        self.border.rounded_rectangle=(
            self.x,
            self.y,
            self.width,
            self.height,
            18
        )


class Home(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)

        self.history=[]

        root=BoxLayout(
            orientation="vertical",
            spacing=8,
            padding=8
        )

        self.add_widget(root)

        # ======================
        # TITLE PNG
        # ======================

        root.add_widget(
            Image(
                source="file_00000000989c71fa995c0bb4f763659a.png",
                size_hint_y=None,
                height=70
            )
        )


        # ======================
        # MARKET + JAM
        # ======================

        top=BoxLayout(
            spacing=6,
            size_hint_y=None,
            height=75
        )


        market_card=Card(
            orientation="vertical"
        )

        market_card.add_widget(
            Label(
                text="MARKET"
            )
        )

        self.market=Label(
            text="CRYPTO IDX",
            font_size=16,
            bold=True
        )

        market_card.add_widget(
            self.market
        )


        jam_card=Card(
            orientation="vertical"
        )

        jam_card.add_widget(
            Label(
                text="JAM REALTIME HP WIB"
            )
        )

        self.clock=Label(
            text="00:00:00",
            font_size=16,
            bold=True
        )

        jam_card.add_widget(
            self.clock
        )


        top.add_widget(
            market_card
        )

        top.add_widget(
            jam_card
        )

        root.add_widget(top)



        # ======================
        # SIGNAL CARD
        # ======================

        self.signal_card=Card(
            orientation="vertical",
            size_hint_y=None,
            height=170,
            spacing=5,
            padding=8
        )

        self.signal_card.add_widget(

            Label(
                text="SIGNAL AREA ( KONFIGURATION SIGNAL )",
                size_hint_y=None,
                height=25,
                bold=True
            )

        )



        self.signal=Label(

            text="SIGNAL: ENTRY BUY DI JAM ..../ ENTRY SELL DI JAM .... / SIGNAL BUY BERAKHIR / SIGNAL SELL BERAKHIR",

            text_size=(320,None),

            halign="center"

        )


        self.status=Label(

            text="STATUS: ACTIVE/EXVIRED",

            size_hint_y=None,

            height=30

        )


        self.signal_card.add_widget(
            self.signal
        )

        self.signal_card.add_widget(
            self.status
        )

        root.add_widget(
            self.signal_card
        )


        # ======================
        # TIMER
        # ======================

        timer=Card(
            size_hint_y=None,
            height=55
        )


        self.timer=Label(
            text="TIMER: 55s / MENUNGGU SIGNAL"
        )

        timer.add_widget(
            self.timer
        )

        root.add_widget(
            timer
        )



        # ======================
        # HISTORY HEADER
        # ======================

        root.add_widget(

            Label(
                text="HISTORY HEADER",
                size_hint_y=None,
                height=25
            )

        )


        scroll=ScrollView()


        self.history_box=BoxLayout(

            orientation="vertical",

            spacing=6,

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
            self.update_data,
            2
        )

        Clock.schedule_interval(
            self.update_clock,
            1
        )


    # ======================
    # JAM HP
    # ======================

    def update_clock(self,dt):

        self.clock.text=(
            strftime("%H:%M:%S")
        )


    # ======================
    # API
    # ======================

    def update_data(self,dt):

        data=fetch_signal()

        signal=data.get(
            "signal",
            "-"
        )

        entry=data.get(
            "entry_time",
            "-"
        )

        market=data.get(
            "market",
            "CRYPTO IDX"
        )


        self.market.text=(
            market.upper()
        )


        if signal=="BUY":

            self.signal.text=(
                f"SIGNAL: ENTRY BUY DI JAM {entry} / SIGNAL BUY BERAKHIR"
            )

            self.status.text=(
                "STATUS: ACTIVE"
            )

            self.signal.color=(
                0,1,0,1
            )


        elif signal=="SELL":

            self.signal.text=(
                f"SIGNAL: ENTRY SELL DI JAM {entry} / SIGNAL SELL BERAKHIR"
            )

            self.status.text=(
                "STATUS: ACTIVE"
            )

            self.signal.color=(
                1,0,0,1
            )


        else:

            self.status.text=(
                "STATUS: EXVIRED"
            )


        txt=f"{signal} | {entry} | EXPIRED"


        if txt in self.history:
            return


        self.history.insert(
            0,
            txt
        )


        row=Card(

            size_hint_y=None,

            height=42
        )


        lbl=Label(
            text=txt
        )


        if signal=="BUY":

            lbl.color=(
                0,1,0,1
            )


        elif signal=="SELL":

            lbl.color=(
                1,0,0,1
            )


        row.add_widget(
            lbl
        )


        self.history_box.add_widget(
            row
        )


        if len(
            self.history
        )>100:

            self.history.pop()
