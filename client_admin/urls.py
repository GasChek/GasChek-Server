from django.urls import path
from .views import (
    CreateUserAPI,
    AdminLoginAPI,
    List_Unverified_UsersAPI,
    List_Verified_UsersAPI,
    List_Not_Connected_With_Device_UsersAPI,
    Verify_User_Connection_With_DeviceAPI,
)

urlpatterns = [
    path("admin_login/", AdminLoginAPI.as_view()),
    path("create_user/", CreateUserAPI.as_view()),
    path("list_unverified_users/", List_Unverified_UsersAPI.as_view()),
    path("list_verified_users/", List_Verified_UsersAPI.as_view()),
    path(
        "list_not_connected_with_device_users/",
        List_Not_Connected_With_Device_UsersAPI.as_view(),
    ),
    path("verify_connection/", Verify_User_Connection_With_DeviceAPI.as_view()),
]
