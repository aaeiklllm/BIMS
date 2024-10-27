from django.contrib import admin
from django.urls import path
from home import views

urlpatterns = [
    path('', views.home, name=''),
    path('aboutUs', views.aboutUs, name='aboutUs'),
     path('admin/home/', views.admin_home, name='admin_home'),

    # Create samples
    path('createsample', views.create_sample, name='createsample'),
    path('createaliquot', views.create_aliquot, name='createaliquot'),
    path('latest-sample-id/', views.get_latest_sample_id, name='latest_sample_id'),
    path('get-sample-ids/', views.get_sample_ids, name='get_sample_ids'),
    path('get_sample_unit/', views.get_sample_unit, name='get_sample_unit'),

    # View samples 
    path('viewsample', views.view_sample, name='viewsample'),
    path('sample_detail/<int:sample_id>/', views.sample_detail, name='sample_detail'),

    # Request sample
    path('requestsample', views.request_sample, name='requestsample'),
    path('requestsample/step7/<int:sample_id>/', views.request_sample_step7, name='request_sample_step7'),
    path('requestsample/ty', views.request_sample_ty, name='request_sample_ty'),
]
