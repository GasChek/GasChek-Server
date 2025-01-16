from django.core.mail import send_mail
import numpy as np
import threading
from django.conf import settings
from accounts.models import Token


class HandleEmail(threading.Thread):
    def __init__(self, user, mode):
        self.user = user
        self.mode = mode
        threading.Thread.__init__(self)

    def run(self):
        subject = "GasChek"
        otp = str(np.random.randint(100000, 999999 + 1))
        message = f"Your otp is {otp}"
        email_from = settings.EMAIL_HOST_USER

        if self.mode == "create":
            Token.objects.create(user=self.user, otp=otp)
        else:
            user_token = Token.objects.get(user=self.user)
            user_token.otp = otp
            user_token.save()

        send_mail(subject, message, email_from, [self.user.email], fail_silently=False)


# class HandleEmail_User(threading.Thread):
#     def __init__(self, email, mode):
#         self.email = email
#         self.mode = mode
#         threading.Thread.__init__(self)

#     def run(self):
#         subject = 'GasChek'
#         otp = str(random.randint(100000, 999999))
#         message = 'Your otp is {}'.format(otp)
#         email_from = settings.EMAIL_HOST_USER

#         if self.mode == "create":
#             user = User.objects.get(email=self.email)
#             Token.objects.create(user=user, otp=otp)
#         else:
#             user_token = Token.objects.get(user__email=self.email)
#             user_token.otp = otp
#             user_token.save()

#         send_mail(
#             subject,
#             message,
#             email_from,
#             [self.email],
#             fail_silently=False
#         )
