from django.shortcuts import redirect, render,HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
User = get_user_model()

# Create your views here.
def homePage(request):
    try:
        # Fetch the user ID from the session
        user_id = request.session.get('id')

        # Fetch the user details if the session contains an ID
        if user_id:
            user = User.objects.get(id=user_id)
        else:
            return render(request, 'home.html') 

        # You can also fetch other users (if needed, as per your original logic)
        pending_users = User.objects.filter(is_active=False)
        deletion_requests = User.objects.filter(deletion_requested=True)
        # Pass the user and any other required context to the template
        return render(request, 'home.html', {'user': user, 'pending_users': pending_users, 'deletion_requests': deletion_requests})
    except Exception as e:
        print(e)
        return HttpResponse("<h1>Something went wrong!</h1>")   
def aboutUs(request):
    try:
        return render(request, 'about.html', {})
    except Exception as e:
        print(e)
        return HttpResponse("<h1>something went wrong!!!</h1>")       

