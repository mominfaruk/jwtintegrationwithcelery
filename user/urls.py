from django.urls import path
from .views import *


urlpatterns = [
    path('register/', RegisterUser.as_view(), name='register'),
    path('token_verify/', TokenVerifyViews.as_view(), name='token_verify'),
]
