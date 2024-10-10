from django.contrib import admin
from django.urls import path
from home import views

urlpatterns = [
    path('', views.homePage, name=''),
    path('aboutUs', views.aboutUs, name='aboutUs'),
    path('createsample', views.create_sample, name='createsample'),
    path('createaliquot', views.create_aliquot, name='createaliquot'),
    path('latest-sample-id/', views.get_latest_sample_id, name='latest_sample_id'),
    path('get-sample-ids/', views.get_sample_ids, name='get_sample_ids'),
    path('get_sample_unit/', views.get_sample_unit, name='get_sample_unit'), 
    path('viewsample', views.view_sample, name='viewsample'),

]
