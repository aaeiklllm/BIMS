from django.contrib import admin
from django.urls import path
from home import views

urlpatterns = [
    path('', views.homePage, name=''),
    path('aboutUs', views.aboutUs, name='aboutUs'),
    path('createsample', views.create_sample),

]
