from django.urls import path
from . import views


urlpatterns = [
    path('createaccount/', views.create_account),
    path('checkusercheck/<roledata>' ,views.register_user),
    path('loginpage' , views.login),
    path('logout' , views.logout),
    path('approveusers/', views.approve_users, name='approve_users'),
    path('updateuser/<int:user_id>/', views.update_user, name='update_user'),
]