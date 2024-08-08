from fcm_django.models import FCMDevice
from firebase_admin.messaging import Message
import threading


class Notification(threading.Thread):
    def __init__(self, reg_id, title, body):
        self.reg_id = reg_id
        self.title = title
        self.body = body
        threading.Thread.__init__(self)

    def run(self):
        try:
            device = FCMDevice.objects.get(registration_id=self.reg_id, active=True)
            message = Message(
                data={
                    "title": self.title,
                    "body": self.body,
                    "image": "https://gaschek.netlify.app/static/media/logo.2278fcc1c56ef14abe57.png",
                }
            )
            for i in range(3):
                device.send_message(message)
        except Exception as e:
            print(e)
