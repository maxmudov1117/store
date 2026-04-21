from django.urls import path

from users.views import *

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('management/', StaffManagementView.as_view(), name='management'),
    path('profile/', ProfileView.as_view(), name='profile'),
]

