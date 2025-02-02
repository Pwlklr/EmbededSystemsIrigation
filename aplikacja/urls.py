"""
URL configuration for aplikacja project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', views.home_view, name='home'),
    path('', views.home_view, name='home'),
    path('schedule/', views.schedule_view, name='schedule'),
    path('weather/', views.weather_view, name='weather'),
    path('sensor/', views.sensor_view, name='sensor'),
    path('delete_events/', views.delete_events, name='delete_events'),
    path('settings/', views.settings_view, name='settings'),
    path('statistics/', views.statistics_view, name='statistics'),
    path('test/', views.test_view, name='test'),
    
]
