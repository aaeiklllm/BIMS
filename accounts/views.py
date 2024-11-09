from django.core.checks import messages
from django.shortcuts import redirect, render
from django.http import HttpResponse, response
from django.contrib.auth.models import User
from .models import UserroleMap
from .models import Role
import uuid
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import *
from django.contrib.auth import authenticate, login
from django.contrib import messages 
from django.contrib.auth import get_user_model
from datetime import datetime
import json
from urllib import response
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
import random
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import UserProfile
from django.contrib.auth.hashers import make_password
# Model to store reset codes (create this if you don't have one)
from .models import PasswordResetCode
from django.utils import timezone
from datetime import timedelta


User = get_user_model()

def register_user(request, roledata):
    try:
        if request.method =='POST':
            uname=request.POST.get('uname',None)
            email=request.POST.get('eml',None)
            first_name = request.POST.get('first_name',None)
            middle_name = request.POST.get('middle_name',None)
            last_name = request.POST.get('last_name',None)
            position = request.POST.get('position',None)
            unit = request.POST.get('unit',None)
            mobile_number = request.POST.get('mobile_number',None)

            pwd=request.POST.get('pwd',None)

            if User.objects.filter(username=uname).exists():
                messages.add_message(request, messages.ERROR, "Username already exists. Please choose another one.")
                return redirect('')
            elif User.objects.filter(email=email).exists():
                messages.add_message(request, messages.ERROR, "Email already used for an account. Please choose another one.")
                return redirect('')
            else:
                user_obj=User.objects.create(username=uname,first_name=first_name, middle_name=middle_name,last_name=last_name, position=position,unit=unit, mobile_number=mobile_number, password=pwd,email=email, is_active=False, is_superuser=False)
                user_obj.set_password(pwd)
                user_obj.save()
                if roledata == 'BiobankManager':
                    role_name = Role.objects.filter(role='BiobankManager').first()
                    
                    userRole= UserroleMap.objects.create(user_id=user_obj, role_id=role_name)
                    userRole.save()
                    messages.add_message(request, messages.SUCCESS, "Biobank manager account pending approval. Please check your email inbox.")
                    try:
                        send_mail(
                            subject='Thank you for creating an account with us!',
                            message='',
                            html_message=f'''Hi {uname}, <br><br>
                        We will send you a response using the email address you have provided within 2-4 business days.<br><br>
                        For further inquiries, please contact us at techassist.bims@gmail.com.<br><br>Regards,<br>
                        BIMS''',
                            from_email=settings.EMAIL_HOST_USER,
                            recipient_list=[email]
                        )
                        return render(request, 'thank_you.html') 
                    except Exception as e:
                        print(e)
                        return render(request, 'ragister.html',{'message':'Failed To Send Email'})
                else:
                    role_name = Role.objects.filter(role='Researcher').first()
            
                    userRole= UserroleMap.objects.create(user_id=user_obj, role_id=role_name)
                    userRole.save()
                    messages.add_message(request, messages.SUCCESS, "Researcher account pending approval.  Please check your email inbox")
                    try:
                        send_mail(
                            subject='Thank you for creating an account with us!',
                            message='',
                            html_message=f'''Hi {uname}, <br><br>
                        We will send you a response using the email address you have provided within 2-4 business days.<br><br>
                        For further inquiries, please contact us at techassist.bims@gmail.com.<br><br>Regards,<br>
                        BIMS''',
                            from_email=settings.EMAIL_HOST_USER,
                            recipient_list=[email]
                        )
                        return render(request, 'thank_you.html')
                    except Exception as e:
                        print(e)
                        return render(request, 'ragister.html',{'message':'Failed To Send Email'})
        messages.add_message(request, messages.ERROR, "Please Add Valid Details !")
        return render(request, 'ragister.html')    
    except Exception as e:
        print(e)
        messages.add_message(request, messages.ERROR, "Something Went Wrong!")
        return render(request, 'index.html') 
def create_account(request):
    role = request.GET.get('role')

    roledata_mapping = {
        'BiobankManager': 'BiobankManager',
        'Researcher': 'Researcher',
    }

    roledata = roledata_mapping.get(role)
    message = f"Create {roledata}"
    
    context = {
        'roledata': roledata,
        'message': message,
    }
    
    return render(request, 'ragister.html', context=context)

def create_sample(request):
    messages.add_message(request, messages.SUCCESS, "Sample has been created.")
    return render(request, 'create_sample.html')

def home(request):
    return render(request, 'home.html')  

def biobankmanager_home(request):
    user_id = request.session.get("user_id") 
    user = User.objects.get(id=user_id)  

    context = {
        'user': user,
    }
    return render(request, 'biobankmanager_home.html', context)

def researcher_home(request):
    user_id = request.session.get("user_id") 
    user = User.objects.get(id=user_id)  

    context = {
        'user': user,
    }
    return render(request, 'researcher_home.html', context)

def admin_home(request):
    return render(request, 'admin_home.html')

#Admin Creation Requests (For Navbar)
def creation_requests(request):
    pending_users = User.objects.filter(is_active=False, deletion_requested=False)  # Filter for creation requests only

    biobank_managers = []  # Initialize empty lists to avoid errors
    researchers = []

    for user in pending_users:
        user_role_map = UserroleMap.objects.filter(user_id=user).first()
        if user_role_map:
            role = user_role_map.role_id.role
            if role == 'BiobankManager':
                biobank_managers.append(user)
            elif role == 'Researcher':
                researchers.append(user)

    deletion_requests = User.objects.filter(deletion_requested=True)  # Separate query for deletion requests

    # Pass both creation and deletion requests in the context
    return render(request, 'admin_home.html', {
        'pending_users': pending_users,
        'deletion_request_count': deletion_requests.count(),
        'creation_request_count': pending_users.count(),
        'biobank_managers': biobank_managers,
        'researchers': researchers,
        'active_tab': 'creation_requests'
    })

#Admin Deletion Requests (For Navbar)
def deletion_requests(request):
    deletion_requests = User.objects.filter(deletion_requested=True)  # Separate query for deletion requests

    biobank_managers = []  # Initialize empty lists
    researchers = []

    for user in deletion_requests:
        user_role_map = UserroleMap.objects.filter(user_id=user).first()
        if user_role_map:
            role = user_role_map.role_id.role
            if role == 'BiobankManager':
                biobank_managers.append(user)
            elif role == 'Researcher':
                researchers.append(user)

    pending_users = User.objects.filter(is_active=False, deletion_requested=False)  # Filter for creation requests

    # Pass both creation and deletion requests in the context
    return render(request, 'admin_home.html', {
        'deletion_requests': deletion_requests,
        'deletion_request_count': deletion_requests.count(),
        'creation_request_count': pending_users.count(),
        'biobank_managers2': biobank_managers,
        'researchers2': researchers,
        'active_tab': 'deletion_requests'
    })


def approve_users(request):
    pending_users = User.objects.filter(is_active=False)
    deletion_requests = User.objects.filter(deletion_requested=True)  # Separate query for deletion requests

    # Create empty lists for each role
    biobank_managers = []
    researchers = []

    # Loop through pending users and separate them by role
    for user in pending_users:
        # Assuming UserRoleMap model relates User and Role
        user_role_map = UserroleMap.objects.filter(user_id=user).first()
        
        if user_role_map:
            role = user_role_map.role_id.role  # Adjust based on your actual model structure
            if role == 'BiobankManager':
                biobank_managers.append(user)
            elif role == 'Researcher':
                researchers.append(user)

    if request.method == 'POST':
        user_id = request.POST.get('user_id')

        if user_id:
            try:
                user = User.objects.get(id=user_id)
                uname = user.username
                email = user.email
                user.is_active = True
                user.save()
                messages.add_message(request, messages.SUCCESS, f"Account for {user.first_name} {user.last_name} has been approved.")
                
                # Send email notification here
                try:
                    send_mail(
                        subject='Your Account Creation Has Been Approved!',
                        message='',  # Leave plain text message empty since we're using HTML
                        html_message=f'''Hi {uname}, <br><br>
                                        We are pleased to inform you that your request to create an account has been <strong>approved</strong>. You can now access your account and begin using our services.<br><br>
                                        <strong>Account Details:</strong><br>
                                        Username: {uname}<br>
                                        Email: {email}<br><br>
                                        To log in, visit <a href="https://example.com/login">our login page</a> and enter your credentials.<br><br>
                                        If you have any questions or need assistance, please contact us at techassist.bims@gmail.com.<br><br>
                                        Regards,<br>
                                        BIMS''',
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[email]
                    )
                except Exception as e:
                    print(e)
                    messages.add_message(request, messages.ERROR, 'Failed to send email notification.')
            
            except User.DoesNotExist:
                messages.add_message(request, messages.ERROR, 'User not found.')
            
            return redirect('approve_users')

    return render(request, 'admin_home.html', {
        'pending_users': pending_users,
        'deletion_request_count': deletion_requests.count(),
        'creation_request_count': pending_users.count(),
        'biobank_managers': biobank_managers,
        'researchers': researchers,
        'active_tab': 'creation_requests'
    })

#User request for deletion
def request_deletion(request):
    user_id = request.session.get("user_id")
    user = User.objects.get(id=user_id)
    
    # Handle deletion request
    if user_id:  # Check if the user is logged in
        user = UserProfile.objects.get(id=user_id)  # Get the user profile based on session id
        user.deletion_requested = True  # Set the flag for deletion request
        user.save()
        messages.success(request, "Deletion request has been made.")
        user_role = get_user_role(user)  # Function to determine user role
        if user_role == 'Admin':
            return redirect('admin_home')
        elif user_role == 'BiobankManager':
            return redirect('biobankmanager_home')
        elif user_role == 'Researcher':
            return redirect('researcher_home')
        else:
            return redirect("")  
    else:
        messages.error(request, "You need to be logged in to request deletion.")
        return redirect('/accounts/loginpage/')  # Redirect to the login page

def delete_users(request):
    pending_users = User.objects.filter(is_active=False)
    deletion_requests = User.objects.filter(deletion_requested=True)

     # Create empty lists for each role
    biobank_managers = []
    researchers = []

    # Loop through pending users and separate them by role
    for user in pending_users:
        user_role_map = UserroleMap.objects.filter(user_id=user).first()
        
        if user_role_map:
            role = user_role_map.role_id.role  # Adjust based on your actual model structure
            if role == 'BiobankManager':
                biobank_managers.append(user)
            elif role == 'Researcher':
                researchers.append(user)

    if request.method == 'POST':
        user_id = request.POST.get('user_id')

        try:
            # Attempt to retrieve and delete the user
            user = UserProfile.objects.get(id=user_id)
            email = user.email
            user_name = f"{user.first_name} {user.last_name}"  # Store user name for messaging

            # Send email notification here
            try:
                send_mail(
                    subject='Your Account Creation Request Has Been Denied',
                    message='',  # Leave plain text message empty since we're using HTML
                    html_message=f'''Hi {user_name}, <br><br>
                                        We regret to inform you that your request to create an account has been <strong>denied</strong>. Unfortunately, we are unable to approve your account at this time.<br><br>
                                        If you believe this is an error or have any questions, please contact us at techassist.bims@gmail.com for further assistance.<br><br>
                                        Regards,<br>
                                        BIMS''',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email]
                )
            except Exception as e:
                print(e)
                messages.add_message(request, messages.ERROR, 'Failed to send email notification.')

            user.delete()
            messages.add_message(request, messages.SUCCESS, f"Account for {user_name} has been deleted.")
        except UserProfile.DoesNotExist:
            messages.add_message(request, messages.ERROR, 'User not found.')
            return redirect('delete_users')  # Redirect back to the same page or appropriate view

        return redirect('delete_users') 

    
    return render(request, 'admin_home.html', {
        'pending_users': pending_users,
        'deletion_request_count': deletion_requests.count(),
        'creation_request_count': pending_users.count(),
        'biobank_managers': biobank_managers,
        'researchers': researchers,
        'active_tab': 'creation_requests'
    })

def custom_login(request):
    print(f"Request path: {request.path}")
    print(f"GET parameters: {request.GET}")

    role = request.GET.get('role')

    roledata_mapping = {
       'BiobankManager': 'BiobankManager',
       'Researcher': 'Researcher',
    }

    roledata = roledata_mapping.get(role)

    try:
        if request.method == 'POST':
            email = request.POST.get('eml', None)
            pwd = request.POST.get('pwd', None)

            user = User.objects.get(username=email)

            if 'forgot_password' in request.POST:
                if not email:                
                    messages.add_message(request, messages.ERROR, "Please enter your username.")
                    return redirect(request.path)

                # Password reset logic
                reset_code = random.randint(100000, 999999)
                PasswordResetCode.objects.create(user=user, code=reset_code, created_at=timezone.now())

                try:
                    send_mail(
                        subject='Password Reset Code',
                        message='',  # Leave plain text message empty since we're using HTML
                        html_message=f'''Your password reset code is {reset_code}''',
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[user.email]
                    )
                except Exception as e:
                    print(e)
                    return render(request, 'index.html', {'message': 'Failed To Send Email'})

                messages.add_message(request, messages.SUCCESS, "Password reset code sent to your email.")
                return render(request, 'reset.html')

            ubj = authenticate(request, username=email, password=pwd) 
            if ubj is None:
                messages.add_message(request, messages.ERROR, "Invalid credentials/User not activated!")
                return redirect(request.path)
            
            login(request, ubj)

            q = User.objects.filter(username=email).filter
            table1_data = UserroleMap.objects.filter(user_id=ubj.id).first()
            if table1_data:
                userRole = Role.objects.filter(id=table1_data.role_id.id).first()
                print(userRole.role)

                request.session["role"] = userRole.role
                request.session["user_id"] = ubj.id
                print(f"User ID from session: {request.session.get('user_id')}")
                
                if q and ubj:
                    messages.add_message(request, messages.SUCCESS, f"Welcome Back, {userRole.role}")
                    if userRole.role == 'BiobankManager':
                        return redirect('biobankmanager_home')  # Replace with the actual URL name
                    elif userRole.role == 'Researcher':
                        return redirect('researcher_home')  # Replace with the actual URL name
                    elif userRole.role == 'Admin':
                        return redirect('admin_home')  # Replace with the actual URL name
                else:
                    messages.add_message(request, messages.SUCCESS, f"Welcome Back, {userRole.role}")
                    return redirect("")  # Fallback if no specific role

            else:
                messages.add_message(request, messages.ERROR, "User role not found.")
                return redirect(request.path)
        else:
            return render(request, 'index.html', {'role': roledata})
    except Exception as e:
        print(e)
        messages.add_message(request, messages.ERROR, "Something Went Wrong!")
        return render(request, 'index.html', {'role': roledata})

def login_admin(request):
    try:
        if request.method =='POST':
            email=request.POST.get('eml',None)
            pwd=request.POST.get('pwd',None)
            ubj= authenticate(request, username=email, password=pwd) 
            if ubj == None:
                messages.add_message(request, messages.ERROR, "Invalid credentials/User not activated!")
                return redirect(request.path)
            
            login(request, ubj)

            q = User.objects.filter(username=email).filter
            table1_data= UserroleMap.objects.filter(user_id=ubj.id).first()
            userRole= Role.objects.filter(id=table1_data.role_id.id).first()
            request.session["role"]=userRole.role
            if q and ubj:
                messages.add_message(request, messages.SUCCESS, f"Welcome Back, {userRole.role}")
                return redirect('creation_requests')
            else:
                return redirect('creation_requests')
        else:
            return render(request, 'admin_login.html')
    except Exception as e:
        print(e)
        messages.add_message(request, messages.ERROR, "Something Went Wrong!")
        return render(request, 'admin_login.html')

def logout(request):
    try:
        del request.session['role']
        messages.add_message(request, messages.SUCCESS, f"Log out successful.")
        return redirect('')
    except:
        return HttpResponse('<h3 style="text-align:center"> Somthing went wrong !!!!!</h3>')

def update_user(request):
    user_id = request.session.get("user_id")
    user = User.objects.get(id=user_id)

    if request.method == 'POST':
        # Get the updated information from the form
        user.username = request.POST.get('uname', user.username)
        user.email = request.POST.get('email', user.email)
        user.first_name = request.POST.get('first_name', user.first_name)
        user.middle_name = request.POST.get('middle_name', user.middle_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.unit = request.POST.get('unit',user.unit)
        user.position = request.POST.get('position', user.position)
        user.mobile_number = request.POST.get('mobile_number', user.mobile_number)

        try:
            # Attempt to save user
            user.save()
            messages.success(request, "User details updated successfully")
            user_role = get_user_role(user)  # Function to determine user role
            if user_role == 'Admin':
                return redirect('admin_home')
            elif user_role == 'BiobankManager':
                return redirect('biobankmanager_home')
            elif user_role == 'Researcher':
                return redirect('researcher_home')
            else:
                return redirect("")
        except Exception as e:
            print(f"Error saving user: {e}")  # Log the error
            messages.error(request, f"Error updating user: {e}")

    context = {
        'user': user
    }
    return render(request, 'home.html', context)

def get_user_role(user):
    table1_data = UserroleMap.objects.filter(user_id=user.id).first()
    if table1_data:
        user_role = Role.objects.filter(id=table1_data.role_id.id).first()
        return user_role.role if user_role else None
    return None

#Admin Approve or Deny
def approve_deletion(request):
    deletion_requests = User.objects.filter(deletion_requested=True)  # Separate query for deletion requests
    pending_users = User.objects.filter(is_active=False)

    biobank_managers = []  # Initialize empty lists
    researchers = []

    for user in deletion_requests:
        user_role_map = UserroleMap.objects.filter(user_id=user).first()
        if user_role_map:
            role = user_role_map.role_id.role
            if role == 'BiobankManager':
                biobank_managers.append(user)
            elif role == 'Researcher':
                researchers.append(user)
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user = UserProfile.objects.get(id=user_id)
        user.delete()
        messages.add_message(request, messages.SUCCESS, f"Account for {user.first_name} {user.last_name} has been deleted.")
        return redirect('approve_deletion')
    return render(request, 'admin_home.html', {
        'deletion_requests': deletion_requests,
        'deletion_request_count': deletion_requests.count(),
        'creation_request_count': pending_users.count(),
        'biobank_managers2': biobank_managers,
        'researchers2': researchers,
        'active_tab': 'deletion_requests'
    })

#Admin Approve or Deny
def deny_deletion(request):
    deletion_requests = User.objects.filter(deletion_requested=True)  # Separate query for deletion requests
    pending_users = User.objects.filter(is_active=False)

    biobank_managers = []  # Initialize empty lists
    researchers = []

    for user in deletion_requests:
            user_role_map = UserroleMap.objects.filter(user_id=user).first()
            if user_role_map:
                role = user_role_map.role_id.role
                if role == 'BiobankManager':
                    biobank_managers.append(user)
                elif role == 'Researcher':
                    researchers.append(user)

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user = UserProfile.objects.get(id=user_id)
        user.deletion_requested = False
        user.save()
        messages.add_message(request, messages.SUCCESS, f"Account deletion request for {user.first_name} {user.last_name} has been denied.")
        return redirect('deny_deletion')
    
    return render(request, 'admin_home.html', {
        'deletion_requests': deletion_requests,
        'deletion_request_count': deletion_requests.count(),
        'creation_request_count': pending_users.count(),
        'biobank_managers2': biobank_managers,
        'researchers2': researchers,
        'active_tab': 'deletion_requests'
    })
  
def reset_password(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')  # Get the confirm password

        # Check if the new password and confirm password match
        if new_password != confirm_password:
            messages.add_message(request, messages.ERROR, "Passwords do not match.")
            return render(request, 'reset.html')

        try:
            # Look for the reset code that matches and is not used
            reset_code_obj = PasswordResetCode.objects.get(code=code, is_used=False)

            # Check if the code is still valid (e.g., within 24 hours)
            if timezone.now() - reset_code_obj.created_at > timedelta(hours=24):
                messages.add_message(request, messages.ERROR, "Reset code has expired.")
                return render(request, 'reset.html')

            # Update the user's password
            user = reset_code_obj.user
            user.password = make_password(new_password)  # Hash the new password
            user.save()

            # Mark the reset code as used
            reset_code_obj.is_used = True
            reset_code_obj.save()

            # return JsonResponse({'success': True, 'message': 'Password updated successfully'})
            messages.add_message(request, messages.SUCCESS, f"Password updated successfully.")
            return render(request, 'index.html')

        except PasswordResetCode.DoesNotExist:
            messages.add_message(request, messages.ERROR, "Invalid code entered.")
            return render(request, 'reset.html')

    # If not POST, render the reset page
    return render(request, 'reset.html')
