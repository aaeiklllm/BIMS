from django.shortcuts import redirect, render,HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
User = get_user_model()
from accounts.models import UserroleMap  # Adjust if necessary


# Create your views here.
def homePage(request):
    try:
        user_id = request.session.get('id')
        if user_id:
            user = User.objects.get(id=user_id)
        else:
            return render(request, 'home.html') 

        # Get pending users and deletion requests
        pending_users = User.objects.filter(is_active=False)
        deletion_requests = User.objects.filter(deletion_requested=True)

        # Separate pending users by role
        biobank_managers = []
        researchers = []

        for user in pending_users:
            user_role_map = UserroleMap.objects.filter(user_id=user).first()  # Assuming you have this model
            
            if user_role_map:
                role = user_role_map.role_id.role  # Adjust based on your actual model structure
                if role == 'BiobankManager':
                    biobank_managers.append(user)
                elif role == 'Researcher':
                    researchers.append(user)

        return render(request, 'home.html', {
            'user': user,
            'pending_users': pending_users,
            'deletion_requests': deletion_requests,
            'biobank_managers': biobank_managers,  # Pass the list to the template
            'researchers': researchers,             # Pass the list to the template
        })
    except Exception as e:
        print(e)
        return HttpResponse("<h1>Something went wrong!</h1>")

def aboutUs(request):
    try:
        return render(request, 'about.html', {})
    except Exception as e:
        print(e)
        return HttpResponse("<h1>something went wrong!!!</h1>")       

