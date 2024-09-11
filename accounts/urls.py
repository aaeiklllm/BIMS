from django.urls import path
from . import views


urlpatterns = [
    path('createaccount/', views.create_account),
    path('checkusercheck/<roledata>' ,views.register_user),
    path('researcherlogin' , views.researcher_login),
    path('managerlogin' , views.manager_login),
    path('loginpage' , views.admin_login),
    path('logout' , views.logout),
    path('approveusers/', views.approve_users),
]