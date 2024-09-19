from django.shortcuts import redirect, render,HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
User = get_user_model()

# Create your views here.
def homePage(request):
    try:
        pending_users = User.objects.filter(is_active=False)
        return render(request, 'home.html', {'pending_users': pending_users})
    except Exception as e:
        print(e)
        return HttpResponse("<h1>something went wrong!!!</h1>")    
def aboutUs(request):
    try:
        return render(request, 'about.html', {})
    except Exception as e:
        print(e)
        return HttpResponse("<h1>something went wrong!!!</h1>")       