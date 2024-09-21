from django.shortcuts import redirect, render,HttpResponse
from django.contrib.auth.models import User
from accounts.models import UserroleMap
from django.contrib.auth import get_user_model
User = get_user_model()

# Create your views here.
def homePage(request):
    try:
        pending_users = User.objects.filter(is_active=False)
        pending_researchers = []
        pending_bbms = []

        for user in pending_users:
            roles = UserroleMap.objects.filter(user_id=user)
            for role in roles:
                if role.role_id.role == 'Researcher':
                    pending_researchers.append(user)
                elif role.role_id.role == 'BiobankManager':
                    pending_bbms.append(user)

        return render(request, 'home.html', {
            'pending_users': pending_users,
            'pending_researchers': pending_researchers,
            'pending_bbms': pending_bbms,
        })
    except Exception as e:
        print(e)
        return HttpResponse("<h1>something went wrong!!!</h1>")    
def aboutUs(request):
    try:
        return render(request, 'about.html', {})
    except Exception as e:
        print(e)
        return HttpResponse("<h1>something went wrong!!!</h1>")       