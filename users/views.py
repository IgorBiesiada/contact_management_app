from django.shortcuts import render
from django.contrib.auth.views import LoginView
from .forms import UserLoginForm
from django.contrib.auth import logout
from django.shortcuts import redirect
# Create your views here.


class LoginUserView(LoginView):
    form_class = UserLoginForm
    template_name = 'login_form.html'
    redirect_authenticated_user = False

def logout_view(request):
    logout(request)
    return redirect('users:login')