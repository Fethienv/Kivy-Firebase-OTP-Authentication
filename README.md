# Kivy Firebase Phone OTP Authentication
Use firebase otp phone authentication with kivy

### Exemple screenshots:

![Screenshot 1](https://github.com/Fethienv/Kivy-Firebase-OTP-Authentication/blob/master/images/screen1.PNG)
![Screenshot 2](https://github.com/Fethienv/Kivy-Firebase-OTP-Authentication/blob/master/images/screen2.PNG)
![Screenshot 3](https://github.com/Fethienv/Kivy-Firebase-OTP-Authentication/blob/master/images/screen3.PNG)
![Screenshot 4](https://github.com/Fethienv/Kivy-Firebase-OTP-Authentication/blob/master/images/screen4.PNG)
![Screenshot 5](https://github.com/Fethienv/Kivy-Firebase-OTP-Authentication/blob/master/images/screen5.PNG)

### How to implement it ?:

#### Requirements:
- python 3.7
- kivy >= 1.11.1
- cefpython3
- BeautifulSoup
- psutil

#### Installation:

1- create virtual environment

2- install all requirements

```

python -m pip install -r requirements.txt


```

2- clone phoneotpauthentication folder to you project folder

3- import phoneotpauthentication, cefpython and cefpython_initialize:

```

from phoneotpauthentication.cefpython import cefpython, cefpython_initialize

from phoneotpauthentication import PhoneOTPAuthentication

```

4- create firebase configuration variable:

```

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


```

**Note:** you can let firebase_config values empty if you won't use local server

5- create change screen function:

```

def GoToVerifyOTPScreen():
    App.get_running_app().sm.current= "VerifyOTP"


```

6- define OTPAuthentication object:

```

OTPAuthentication = PhoneOTPAuthentication( 
                                              firebase_config = firebase_config, 
                                              ChangeToVerifyOTPScreenCallback = GoToVerifyOTPScreen,  
                                              LocalServer= True
                                            )

```

* Arguments:

Argument | value
------------ | -------------
firebase_config |  dict of firebase configuration
ChangeToVerifyOTPScreenCallback |  your defined change screen function
LocalServer  |  True or false, for use local or your own server
recaptcha_url |  url to html file to load recaptch verifier (clone this [file!](https://github.com/Fethienv/Kivy-Firebase-OTP-Authentication/blob/master/phoneotpauthentication/recaptcha.html) to your server)
SendOTP_url   |  url for post phone and recaptcha token to your server than to firebase from you server
VerifyOTP_url |  url for post otp and sessionInfo to your server than to firebase from you server
reload_every_time |  True or False, for reload recaptcha page every time click send otp
SendOTPDoneCallback |  your defined function to run some code when send otp done
SendOTPFailCallback |  your defined function to run some code when send otp fail
VerifyOTPDoneCallback |  your defined function to run some code when otp is correct
VerifyOTPFailCallback |  your defined function to run some code when otp was wrong

7- create your widgets and add action to send and verify otp, exp:

```

class SendOTPScreen(Screen):
    
    def GetOTP(self):
        phoneNumber = self.ids.Phone_Input.text
        OTPAuthentication.GetOTP(phoneNumber)     

class VerifyOTPScreen(Screen):

    def VerifyOTP(self):
        code = self.ids.OTP_Input.text
        OTPAuthentication.VerifyOTP(code)

```

8- create your app:

```

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


```

**Note:** don't forget `cefpython.Shutdown()`


9- run it:

```

python test.py


```



