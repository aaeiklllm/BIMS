from django.urls import path
from . import views
from .views import request_deletion

urlpatterns = [
    path('createaccount/', views.create_account, name='create_account'),
    path('loginpage/' , views.custom_login, name='custom_login'),
    path('logout' , views.logout),
    path('loginpage/reset_password', views.reset_password, name='reset_password'),
    path('adminlogin/', views.login_admin),

    path('checkusercheck/<roledata>' ,views.register_user),   
    path('approveusers/', views.approve_users, name='approve_users'),
    path('deleteusers/', views.delete_users, name='delete_users'),
    path('updateuser/', views.update_user, name='update_user'),

    path('request-deletion/', views.request_deletion, name='request_deletion'),
    path('approve-deletion/', views.approve_deletion, name='approve_deletion'),
    path('deny-deletion/', views.deny_deletion, name='deny_deletion'), 

    path('creation_requests/', views.creation_requests, name='creation_requests'),
    path('deletion_requests/', views.deletion_requests, name='deletion_requests'),

    path('home/', views.home, name='home'),
    path('biobankmanager/home/', views.biobankmanager_home, name='biobankmanager_home'),
    path('researcher/home/', views.researcher_home, name='researcher_home'),
    path('admin/home/', views.admin_home, name='admin_home'),
]