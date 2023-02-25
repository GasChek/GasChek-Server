from django.core.mail import send_mail
import random
import threading
from django.conf import settings
from accounts.models import Token


class HandleEmail(threading.Thread):
    def __init__(self, user, mode):
        self.user = user
        self.mode = mode
        threading.Thread.__init__(self)

    def run(self):
        subject = 'GasChek Gas Dealer Account'
        otp = str(random.randint(100000, 999999))
        message = 'Your otp is {}'.format(otp)
        email_from = settings.EMAIL_HOST_USER

        if self.mode == "create":
            Token.objects.create(user=self.user, otp=otp)
        else:
            user_token = Token.objects.get(user=self.user)
            user_token.otp = otp
            user_token.save()

        send_mail(
            subject,
            message,
            email_from,
            [self.user],
            fail_silently=False
        )
