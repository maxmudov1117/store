from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import authenticate, login, logout

class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')
    def post(self, request):
        user = authenticate(
            username = request.POST.get('username'),
            password = request.POST.get('password')
        )
        if user:
            login(request,user)
            return redirect('home')
        return redirect('login')

def logout_view(request):
    logout(request)
    return redirect('home')