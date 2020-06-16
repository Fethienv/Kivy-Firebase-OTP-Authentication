import kivy

kivy.require('1.11.1')

from kivy.app import App
from kivy.lang import Builder
from kivy.factory import Factory

from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen

from kivy.properties import BooleanProperty
from kivy.core.window import Window

from modules.cefpython import cefpython, cefpython_initialize

from modules.phoneotpauthentication import PhoneOTPAuthentication


firebase_config = {
                    "apiKey"              : "AIzaSyDdT5CKe4ISB91z7R4uWuREoMVWhtBzfgI",
                    "authDomain"          : "sahari-18615.firebaseapp.com",
                    "databaseURL"         : "https://sahari-18615.firebaseio.com",
                    "projectId"           : "sahari-18615",
                    "storageBucket"       : "sahari-18615.appspot.com",
                    "messagingSenderId"   : "576094375251",
                    "appId"               : "1:576094375251:web:0a8508470c41ab3e7965a6",
                    "measurementId"       : "G-YVDG2TW324",
                }


def GoToVerifyOTPScreen():
    App.get_running_app().sm.current= "VerifyOTP"

OTPAuthentication = PhoneOTPAuthentication( 
                                              firebase_config = firebase_config, 
                                              ChangeToVerifyOTPScreenCallback = GoToVerifyOTPScreen,  
                                              LocalServer= True
                                            )

class SendOTPScreen(Screen):
    
    def GetOTP(self):
        phoneNumber = self.ids.Phone_Input.text
        OTPAuthentication.GetOTP(phoneNumber)     

class VerifyOTPScreen(Screen):

    def VerifyOTP(self):
        code = self.ids.OTP_Input.text
        OTPAuthentication.VerifyOTP(code)

       
# Main application
class MainApp(App):

    def __init__(self, url="", *largs, **kwargs):
        super(MainApp, self).__init__(**kwargs)

    def build(self):
        self.sm = Builder.load_file('index.kv')
        self.sm.current = "SendOTP"

        return self.sm
     
if __name__ == "__main__":
    MainApp().run()
    cefpython.Shutdown() 