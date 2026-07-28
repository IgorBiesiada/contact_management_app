from django.urls import path
from . views import LoginUserView, logout_view


app_name = 'users'

urlpatterns = [
    path('', LoginUserView.as_view(), name='login'),
    path('logout/', logout_view, name='logout')
]