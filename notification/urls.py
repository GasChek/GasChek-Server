from django.urls import path
from .views import Register_Push_Notification

urlpatterns = [
    path("reg_push/", Register_Push_Notification.as_view()),
]
