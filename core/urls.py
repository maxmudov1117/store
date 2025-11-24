from django.contrib import admin
from django.urls import path, include
from main.views import *
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('main/', include('main.urls')),
    path('auth/', include('users.urls')),
    path('stats/', include('stats.urls'))
]
