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

from phoneotpauthentication.cefpython import cefpython, cefpython_initialize

from phoneotpauthentication import PhoneOTPAuthentication


firebase_config = {
                    "apiKey"              : "",
                    "authDomain"          : "",
                    "databaseURL"         : "",
                    "projectId"           : "",
                    "storageBucket"       : "",
                    "messagingSenderId"   : "",
                    "appId"               : "",
                    "measurementId"       : "",
                }


def GoToVerifyOTPScreen(obj, widget):
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