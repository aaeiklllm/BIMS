from django.urls import path
from . import views


urlpatterns = [
    path('createaccount/', views.create_account),
    path('checkusercheck/<roledata>' ,views.register_user),
    path('loginpage_researcher' , views.login),
    path('loginpage_manager' , views.login_manager),
    path('logout' , views.logout),
    path('approveusers/', views.approve_users, name='approve_users'),
    path('adminlogin/', views.login_admin),
    path('test/', views.test),
]