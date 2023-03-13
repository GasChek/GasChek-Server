from django.urls import path
from .views import (CreateUserAPI, 
                    AdminLoginAPI, 
                    List_Unverified_UsersAPI,
                    List_Verified_UsersAPI,
                    Verify_UserAPI)

urlpatterns = [
    path('admin_login/', AdminLoginAPI.as_view()),
    path('create_user/', CreateUserAPI.as_view()),
    path('list_unverified_users/', List_Unverified_UsersAPI.as_view()),
    path('list_verified_users/', List_Verified_UsersAPI.as_view()),
    path('verify_user/', Verify_UserAPI.as_view()),
]
