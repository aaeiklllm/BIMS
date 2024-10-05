from django.urls import path
from . import views
from .views import request_deletion

urlpatterns = [
    path('createaccount/', views.create_account, name='create_account'),
    path('createsample', views.create_sample),
    path('checkusercheck/<roledata>' ,views.register_user),
    path('loginpage/' , views.login),
    path('logout' , views.logout),
    path('approveusers/', views.approve_users, name='approve_users'),
    path('deleteusers/', views.delete_users, name='delete_users'),
    path('updateuser/<int:user_id>/', views.update_user, name='update_user'),
    path('request-deletion/', views.request_deletion, name='request_deletion'),
    path('approve-deletion/', views.approve_deletion, name='approve_deletion'),
    path('deny-deletion/', views.deny_deletion, name='deny_deletion'),
    path('reset_password', views.reset_password, name='reset_password'),
    path('adminlogin/', views.login_admin),
    path('test/', views.test),
]