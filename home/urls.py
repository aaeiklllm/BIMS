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
    path('sample_detail/edit/<int:sample_id>/', views.edit_sample, name='edit_sample'),
    path('sample_detail/delete/<int:sample_id>/', views.delete_sample, name='delete_sample'),

    # View request sample
    path('view_request_sample', views.view_request_sample, name='view_request_sample'),
    path('view_details/<int:id>/', views.view_details, name='view_details'),
    path('update_view_details/<int:id>/', views.update_view_details, name='update_view_details'), 
    path('create_ack_receipt/<int:id>/', views.create_ack_receipt, name='create_ack_receipt'),
    path('download_ack_receipt/<int:ack_id>/', views.download_ack_receipt, name='download_ack_receipt'),

    # Request sample
    path('requestsample', views.request_sample, name='requestsample'),
    path('requestsample/step7/<int:sample_id>/', views.request_sample_step7, name='request_sample_step7'),
    path('requestsample/ty', views.request_sample_ty, name='request_sample_ty'),
    path('request_sample/delete/<int:pk>/', views.delete_request_sample, name='delete_request_sample'),

    path('myrequests', views.my_requests, name='myrequests'),
    path('viewrequestsampledetails/<int:sample_id>/', views.view_request_sample_details, name='viewrequestsampledetails'),
    path('editrequestsample/<int:sample_id>/', views.edit_request_sample, name='editrequestsample'),
    path('editrequestsample/step7/<int:sample_id>/', views.edit_request_sample_step7, name='edit_request_sample_step7'),
  
  # Inventory status
    path('inventory_status', views.inventory_status, name='inventory_status'),
    path('generate-pdf/', views.generate_pdf, name='generate_pdf'),
    
]
