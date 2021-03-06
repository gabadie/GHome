from twilio.rest import TwilioRestClient
import sys
sys.path.append('..')
from enocean.devices import Actuator

class Phone(Actuator):
    account_sid = "AC5835465fb0e2e2e1dd00aadd5243a21a"
    auth_token = "ab526713ca5fa0ca12d987b629f83b43"
    client = TwilioRestClient(account_sid, auth_token)

    def callback_call(self, server):
        call = self.client.calls.create(to="+33626274011",
                                       from_="+33975184908",
                                       url="http://kachkach.com/twiml")
        print call.sid

    # def callback_sms(self, server):
    #     message = self.client.messages.create(to="+33626274011",
    #                                      from_="+33975184908",
    #                                  body="An alert was triggered by one of your devices. Please log-in to GHome for more information.")

    #     print message

if __name__ == '__main__':
    phone = Phone(device_id=112233)
    phone.callback_call(None)
