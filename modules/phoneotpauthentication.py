import kivy

kivy.require('1.11.1')
import requests
import time
import socketserver

from bs4 import BeautifulSoup
from socket import *
from _thread import *
from psutil import process_iter, AccessDenied
from signal import SIGTERM # or SIGKILL

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.modalview import ModalView
from kivy.core.window import Window

from .cefpython import cefpython, cefpython_initialize
from .cefbrowser import *

try:
    # Python 2
    from SimpleHTTPServer import test, SimpleHTTPRequestHandler
except ImportError:
    # Python 3
    from http.server import test, SimpleHTTPRequestHandler

requestsJar = requests.cookies.RequestsCookieJar()

# 2 problems:
# 1- with local test server: OSError: [WinError 10048] Only one usage of each socket address (protocol/network address/port) is normally permitted
#    this must shutdown server correctly or kill proc that use server host and port 
# 2- if connection with recaptach fail must close overpop.dismiss, self.modelv = none and cefpython.Shutdown() 

# TODO:
# - use templates to replace firebase credentials with its values  
# - cefbrowser size as windows size
# - shutdown background local server or kill its procces
# - show recaptcha errors message in popups and reload recaptcha by : self.modelv = none and cefpython.Shutdown()

class FireServer:
    httpd = None
    port = 8080
    httpd_thread = None 

    def create_server(self):
        
        handler = SimpleHTTPRequestHandler
        try:
            self.httpd = socketserver.TCPServer(("", self.port), handler)
            print("serving at port:" + str(self.port))
            self.httpd.serve_forever()
        except:
            print("port:" + str(self.port)+ 'already used')        

    def start(self):
        self.httpd_thread = start_new_thread(self.create_server, tuple())

    def stop(self):
        self.httpd.shutdown()

        # for proc in process_iter():
        #     for conns in proc.connections(kind='inet'):
        #         if conns.laddr.port == self.port:                   
        #             try:
        #                 proc.send_signal(SIGTERM) # or SIGKILL
        #                 print("stop serving at port:" + str(self.port))
        #             except AccessDenied:
        #                 print ("AccessDenied")
   
    
FireServer = FireServer() 
class OverPopup(ModalView):

    donebtn        = None
    dialog_size    = (390, 180)
    recaptach_size = (500, 500)
    donebtn_size   = (383,50)

    def __init__(self, LocalServer, *largs, **kwargs):
        super(OverPopup, self).__init__(**kwargs)
        self.cb1 = None
        self.LocalServer = LocalServer
        
    def on_open(self):
        if self.LocalServer:
            FireServer.start()

    def on_pre_dismiss(self):

        if self.LocalServer:
            FireServer.stop()

        # only if 
        # recaptach is verified 
        # or when change to next screen
        # or script shutdown
        #cefpython.Shutdown() 
        

class Visitor(object):
    callback = None
    def Visit(self, value):
         if value:
            soup = BeautifulSoup(value, features="html.parser")
            div  = soup.find_all('div')
            if len(div) == 9:
                target_div   = div[4]
                target_style = target_div["style"]
                result = target_style.find('visible') 
                if result == -1:
                    self.callback("hidden", None)
                else:
                    self.callback("visible", None)
      
myvisitor = Visitor()

class PhoneOTPAuthentication(object):

    cb1    = None
    modelv = None  

    recaptcha_url     = "http://localhost:8080/modules/recaptcha.html" 

    def __init__(self, firebase_config, ChangeToVerifyOTPScreenCallback, LocalServer= True, recaptcha_url = None, SendOTP_url = None, VerifyOTP_url = None, 
                 reload_every_time = None, SendOTPDoneCallback = None, SendOTPFailCallback = None, VerifyOTPDoneCallback = None, VerifyOTPFailCallback = None ):

        self.firebase_config      = firebase_config  
        self.LocalServer          = LocalServer 
        self.reload_every_time    = reload_every_time
        self.ChangeToVerifyOTPScreenCallback = ChangeToVerifyOTPScreenCallback

        self.SendOTPDoneCallback   = None 
        self.SendOTPFailCallback   = None 
        self.VerifyOTPDoneCallback = None 
        self.VerifyOTPFailCallback = None

        self.SendOTP_url     = SendOTP_url 
        self.VerifyOTP_url   = VerifyOTP_url 

        if not self.LocalServer:
            self.recaptcha_url   = recaptcha_url
        
    def create_recaptcha_on(self, modelv):

        dialog_size    = modelv.dialog_size
        recaptach_size = modelv.recaptach_size
        donebtn_size   = modelv.donebtn_size

        if not self.modelv:
            def url_handler(self, url):
                print("URL HANDLER", url)

            def title_handler(self, title):
                print("TITLE HANDLER", title)

            def close_handler(self):
                print("CLOSE HANDLER")

            def donebtn_visibility(value):
                if value == "hidden":
                    modelv.donebtn.text    = "Cancel"
                    modelv.donebtn.size    = donebtn_size
                    modelv.donebtn.width   = donebtn_size[0]
                    modelv.donebtn.hight   = donebtn_size[1]
                    modelv.donebtn.opacity = 1
                elif value == "visible": 
                    modelv.donebtn.text    = ""
                    modelv.donebtn.size    = (0,0)
                    modelv.donebtn.width   = 0
                    modelv.donebtn.hight   = 0
                    modelv.donebtn.opacity = 0
            
            def donebtn_text(obj, btn):
                modelv.donebtn.text = "Get OTP"

            def RecaptchaChallenge_handler(value, js_callback):
                donebtn_visibility(value)
                #js_callback.Call("I am a Python string #2", py_callback)

            def py_Recaptcharesponse_callback(value): 
                pass
                
            def Recaptchatoken_handler(value, js_callback):
                # store in session with expire time
                if value and value != "":

                    def VerifyOTPScreen(btn):
                        state = self.SendOTP()
                        if state:
                            #sleep()
                            if self.ChangeToVerifyOTPScreenCallback:
                                self.ChangeToVerifyOTPScreenCallback()
                            else:
                                App.get_running_app().sm.current= "VerifyOTP"
                            print("Screen changed")
                        else:
                            self.modelv = None
                            self.OverPopup.dismiss() 

                    requestsJar.set(name ='recaptcha_token', value=value, domain="localhost")
                    modelv.donebtn.bind(text=donebtn_text)
                    modelv.donebtn.bind(on_release=VerifyOTPScreen)
                    donebtn_visibility('hidden')

            def OnLoadingStateChange_callback(bw):
                Frame = bw._browser.GetMainFrame()
                if Frame:
                    myvisitor.callback = RecaptchaChallenge_handler           
                    Frame.GetSource(myvisitor)

            modelv.donebtn = Button(text='Cancel', font_size=14, size_hint=[None, None], size= donebtn_size, pos=((Window.width - dialog_size[0])/2+3,(Window.height - dialog_size[1])/2))

            modelv.donebtn.bind(on_release=modelv.dismiss)

            modelv.cb1 = CEFBrowser(
                url=self.recaptcha_url, 
                pos=((Window.width - recaptach_size[0])/2, (Window.height - recaptach_size[1])/2) , size=recaptach_size,
                OnLoadingStateChange_callback = OnLoadingStateChange_callback, 
                client_handler_callbacks = {
                    "RecaptchaChallenge_handler":RecaptchaChallenge_handler,
                    "Recaptchatoken_handler":Recaptchatoken_handler,
                    #"py_Recaptcharesponse_callback":py_Recaptcharesponse_callback,
                    #"__kivy__keyboard_update":bw._keyboard_update,
                    #"__kivy__selection_update":bw._selection_bubble._updat,
                    }
                )

            modelv.cb1.close_handler = close_handler
            modelv.cb1.bind(url=url_handler)
            modelv.cb1.bind(title=title_handler)

            w = Widget()
            w.add_widget(modelv.cb1)

            w.add_widget(modelv.donebtn)

            def OnwindowResize(window, width, height):
                modelv.donebtn.pos = ((width - dialog_size[0])/2+3,(height - dialog_size[1])/2)
                modelv.cb1.pos     = ((width - recaptach_size[0])/2, (height - recaptach_size[1])/2)

            Window.bind(on_pre_resize = OnwindowResize)

            modelv.add_widget(w)

            self.modelv = modelv

        return self.modelv    

    def GetOTP(self, phoneNumber):
        self.phoneNumber = phoneNumber
        self.OverPopup = self.create_recaptcha_on(OverPopup(LocalServer = True))

        # if you need reload cef every time can add remove self.modelv
        if self.reload_every_time:
            def delete_modelv(self_ob):
                self.modelv = None  
            self.OverPopup.bind(on_dismiss=delete_modelv)

        self.OverPopup.open()

    # this function only for test
    # for your firebase security, In real app must use this code on server
    def SendOTP(self):
        recapchaToken   = requestsJar["recaptcha_token"]
        post_data         = { "phoneNumber": "+"+str(self.phoneNumber),
                          "recaptchaToken": recapchaToken,
                        }

        url = 'https://www.googleapis.com/identitytoolkit/v3/relyingparty/sendVerificationCode?key='+ self.firebase_config["apiKey"] if self.LocalServer else self.SendOTP_url

        response = requests.post(url, json= post_data)

        if response.status_code == 200:
            #Ok
            if self.SendOTPDoneCallback:
                self.SendOTPDoneCallback()
            else:
                requestsJar.set(name ='recaptcha_sessionInfo', value=response.json()['sessionInfo'], domain="localhost") 
                print("Send OTP done") if self.LocalServer else print(response.text)
                return True
        else:
            # Show error
            if self.SendOTPFailCallback:
                self.SendOTPFailCallback()
            else:
                print(response.text) 
                return False
        
    # this function only for test
    # for your firebase security, In real app must use this code on server
    def VerifyOTP(self, code):

        post_data   = { "sessionInfo": requestsJar["recaptcha_sessionInfo"],
                        "code"       : code,
                    }
        
        url = 'https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPhoneNumber?key='+ self.firebase_config["apiKey"] if self.LocalServer else self.VerifyOTP_url    

        response = requests.post(url, json= post_data)                
        if response.status_code == 200:
            #Ok
            if self.VerifyOTPDoneCallback:
                self.VerifyOTPDoneCallback()
            else:
                print("OTP Correct") if self.LocalServer else print(response.text) 
                return True
        else:
            # Show error
            if self.VerifyOTPFailCallback:
                self.VerifyOTPFailCallback()
            else:
                print(response.text) 
                return False

          