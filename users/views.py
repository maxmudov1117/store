from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import User
from main.models import Branch


class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        user = authenticate(
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )
        if user:
            login(request, user)
            return redirect('home')
        return render(request, 'login.html', {'error': "Foydalanuvchi nomi yoki parol noto'g'ri!"})


def logout_view(request):
    logout(request)
    return redirect('login')


class StaffManagementView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = 'login'
    
    def test_func(self):
        return self.request.user.is_superuser
        
    def get(self, request):
        users = User.objects.all().order_by('-is_superuser', 'username')
        branches = Branch.objects.all()
        return render(request, 'management.html', {'users': users, 'branches': branches})
        
    def post(self, request):
        if not request.user.is_superuser:
            return redirect('home')
            
        user_id = request.POST.get('user_id')
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        branch_id = request.POST.get('branch_id')
        is_active = request.POST.get('is_active') == 'on'
        
        branch = get_object_or_404(Branch, id=branch_id) if branch_id else None
        
        if user_id:
            user = get_object_or_404(User, id=user_id)
            user.username = username
            user.first_name = first_name
            user.last_name = last_name
            user.phone_number = phone_number
            user.branch = branch
            user.is_active = is_active
            if password:
                user.set_password(password)
            user.save()
        else:
            User.objects.create_user(
                username=username, 
                first_name=first_name, 
                last_name=last_name, 
                phone_number=phone_number,
                password=password, 
                branch=branch, 
                is_active=is_active
            )
        return redirect('management')


class ProfileView(LoginRequiredMixin, View):
    login_url = 'login'
    
    def get(self, request):
        return render(request, 'profile.html')
        
    def post(self, request):
        user = request.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.phone_number = request.POST.get('phone_number')
        
        new_password = request.POST.get('new_password')
        if new_password:
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)
        else:
            user.save()
            
        return redirect('profile')