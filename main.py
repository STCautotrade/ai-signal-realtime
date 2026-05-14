import requests
from datetime import datetime, timedelta
import webbrowser
import os
import time

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


DATA_URL="http://157.10.252.46:5000/signal"
BASE_DIR=os.path.dirname(__file__)


# =========================
# CARD
# =========================

class Card(BoxLayout):

    def __init__(
        self,
        bg=(0.03,0.05,0.09,1),
        border=(0,1,1,1),
        h=90,
        **kwargs
    ):

        super().__init__(**kwargs)

        self.orientation="vertical"
        self.padding=dp(8)
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
            h=60,
            bg=(0.08,0.08,0.12,1)
        )

        self.label=Label(
            text=text,
            font_size=dp(10),
            halign="left",
            valign="middle",
            text_size=(dp(300),None)
        )

        self.label.bind(
            texture_size=self.resize
        )

        self.add_widget(
            self.label
        )

    def resize(self,*args):

        h=max(
            dp(60),
            self.label.texture_size[1]+dp(20)
        )

        self.height=h


# =========================
# HOME
# =========================

class Home(Screen):

    def __init__(self,**kw):

        super().__init__(**kw)

        self.lang="id"

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
            text="00:00:00",
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


        lang_row=BoxLayout(
            size_hint_y=None,
            height=dp(40),
            spacing=dp(4)
        )

        btn_id=Button(
            text="Indonesia",
            on_press=lambda x:
            self.set_lang("id")
        )

        btn_en=Button(
            text="English",
            on_press=lambda x:
            self.set_lang("en")
        )

        btn_es=Button(
            text="Español",
            on_press=lambda x:
            self.set_lang("es")
        )

        lang_row.add_widget(btn_id)
        lang_row.add_widget(btn_en)
        lang_row.add_widget(btn_es)

        root.add_widget(lang_row)


        self.signal=Card(h=120)

        self.signal_label=Label(
            text="WAITING SIGNAL...",
            font_size=dp(18)
        )

        self.entry=Label(
            text="ENTRY:-",
            font_size=dp(12)
        )

        self.status=Label(
            text="SYSTEM STANDBY",
            font_size=dp(10)
        )

        self.signal.add_widget(
            self.signal_label
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


        self.expire_card=Card(
            h=70
        )

        self.expire_label=Label(
            text="WAITING SIGNAL",
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
            spacing=dp(4),
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


    def set_lang(self,lang):

        self.lang=lang


    def clock_update(self,dt):

        zona=time.tzname[0]

        self.clock_label.text=(
            datetime.now().strftime(
                f"%H:%M:%S {zona}"
            )
        )


    def expired(self,t):

        try:

            return(
                datetime.now().strftime(
                    "%H:%M"
                )>t
            )

        except:

            return False


    def waiting_text(self):

        if self.lang=="id":
            return "MENUNGGU SIGNAL BERIKUTNYA"

        elif self.lang=="en":
            return "WAITING NEXT SIGNAL"

        return "ESPERANDO SIGUIENTE SEÑAL"



    def signal_text(self):

        if self.lang=="id":
            return "MENUNGGU SIGNAL..."

        elif self.lang=="en":
            return "WAITING SIGNAL..."

        return "ESPERANDO SEÑAL..."


    def update_expiry(self,dt):

        if not self.expiry_time:

            self.expire_label.text=(
                self.waiting_text()
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

            self.expiry_time=None



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


            hist=None


            if signal=="BUY":

                self.signal.set_bg(
                    (0,0.7,0.3,1)
                )

                self.signal_label.text="BUY NOW"

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


            elif signal=="SELL":

                self.signal.set_bg(
                    (0.9,0.2,0.2,1)
                )

                self.signal_label.text="SELL NOW"

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


            else:

                self.signal.set_bg(
                    (0.03,0.05,0.09,1)
                )

                self.signal_label.text=(
                    self.signal_text()
                )

                self.entry.text="-"

                self.status.text=(
                    "MENUNGGU KONFIRMASI"
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


                if len(
                    self.history_box.children
                )>20:

                    self.history_box.remove_widget(
                        self.history_box.children[-1]
                    )


        except:

            self.signal_label.text="OFFLINE"
            self.status.text="SERVER ERROR"



class Martingale(Screen):

    def __init__(self,**kw):

        super().__init__(**kw)

        root=BoxLayout(
            orientation="vertical"
        )

        root.add_widget(
            Label(
                text="MARTINGALE"
            )
        )

        self.add_widget(root)



class AppMain(App):


    def build(self):

        sm=ScreenManager()

        home=Home(
            name="home"
        )

        mart=Martingale(
            name="mart"
        )

        sm.add_widget(home)
        sm.add_widget(mart)

        return sm



if __name__=="__main__":
    AppMain().run()
