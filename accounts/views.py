from django.core.checks import messages
from django.shortcuts import redirect, render
from django.http import HttpResponse, response
from django.contrib.auth.models import User
import uuid
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import *
from django.contrib.auth import authenticate
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
                messages.add_message(request, messages.ERROR, "User Already Exists")
                return redirect('')
            elif User.objects.filter(email=email).exists():
                messages.add_message(request, messages.ERROR, "User Already Exists")
                return redirect('')
            else:
                user_obj=User.objects.create(username=uname,first_name=first_name, middle_name=middle_name,last_name=last_name, position=position,unit=unit, mobile_number=mobile_number, password=pwd,email=email, is_active=False, is_superuser=False)
                user_obj.set_password(pwd)
                user_obj.save()
                if roledata == 'BiobankManager':
                    role_name = Role.objects.filter(role='BiobankManager').first()
                    
                    userRole= UserroleMap.objects.create(user_id=user_obj, role_id=role_name)
                    userRole.save()
                    messages.add_message(request, messages.SUCCESS, "Biobank Manager pending approval")
                    try:
                        send_mail(
                            subject='Thank you for creating an account with us!',
                            message='',
                            html_message=f'''Hi {uname}, <br><br>
                        We will send you a response using the email address you have provided within 2-4 business days.<br><br>
                        For further inquiries, please contact us at bims@gmail.com.<br><br>Regards,<br>
                        BIMS''',
                            from_email=settings.EMAIL_HOST_USER,
                            recipient_list=[email]
                        )
                    except Exception as e:
                        print(e)
                        return render(request, 'ragister.html',{'message':'Failed To Send Email'})
                    finally:
                        return redirect('')
                else:
                    role_name = Role.objects.filter(role='Researcher').first()
            
                    userRole= UserroleMap.objects.create(user_id=user_obj, role_id=role_name)
                    userRole.save()
                    messages.add_message(request, messages.SUCCESS, "Researcher pending approval")
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
                    except Exception as e:
                        print(e)
                        return render(request, 'ragister.html',{'message':'Failed To Send Email'})
                    finally:
                        return redirect('')
        messages.add_message(request, messages.ERROR, "Please Add Valid Details !")
        return render(request, 'ragister.html')    
    except Exception as e:
        print(e)
        messages.add_message(request, messages.ERROR, "Something Went Wrong!")
        return render(request, 'index.html') 
        # Change this index.html

def create_account(request):
    role = request.GET.get('role')

    roledata_mapping = {
        'BiobankManager': 'BiobankManager',
        'Researcher': 'Researcher',
    }

    roledata = roledata_mapping.get(role)
    message = f"Create {roledata}"
    
    # Pass roledata and message to the template context
    context = {
        'roledata': roledata,
        'message': message,
    }
    
    return render(request, 'ragister.html', context=context)

# def create_sample(request):

#     return render(request, 'create_sample.html')


def approve_users(request):
    pending_users = User.objects.filter(is_active=False)

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
                                        If you have any questions or need assistance, please contact us at bims@gmail.com.<br><br>
                                        Regards,<br>
                                        BIMS''',
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[email]
                    )
                except Exception as e:
                    print(e)
                    return render(request, 'home.html', {'message': 'Failed To Send Email'})
                finally:
                    return render(request, 'home.html', {'biobank_managers': biobank_managers, 'researchers': researchers})

            except User.DoesNotExist:
                pass  

    return render(request, 'home.html', {'biobank_managers': biobank_managers, 'researchers': researchers})

def delete_users(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user = UserProfile.objects.get(id=user_id)
        # Perform the actual deletion of the user
        user.delete()
        messages.success(request, f"Account for {user.first_name} {user.last_name} has been deleted.")
    return redirect('')  # Redirect to the admin page

def login(request):
    role = request.GET.get('role')

    roledata_mapping = {
       'BiobankManager': 'BiobankManager',
       'Researcher': 'Researcher',
    }

    roledata = roledata_mapping.get(role)

    try:
        if request.method =='POST':
            email=request.POST.get('eml',None)
            pwd=request.POST.get('pwd',None)
            
            # print(request.POST)
            user = User.objects.get(username=email)
            if 'forgot_password' in request.POST:
                if not email:
                    messages.error(request, "Please enter your username.")
                    return redirect(request.path)
                # Proceed with password reset logic
                # Send the reset code to the email/username
                # Generate a random verification code
                reset_code = random.randint(100000, 999999)

                # Save code in the PasswordResetCode model (linked with User)
                PasswordResetCode.objects.create(user=user, code=reset_code, created_at=timezone.now())

                # Send code via email
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
                    return render(request, 'index.html',{'message':'Failed To Send Email'})
                messages.success(request, "Password reset code sent to your email.")
                return render(request, 'reset.html')

            ubj= authenticate(request, username=email, password=pwd) 
            if ubj == None:
                messages.add_message(request, messages.ERROR, "Invalid credentials/User not activated!")
                return redirect(request.path)
            q = User.objects.filter(username=email).filter(is_staff=True)
            table1_data= UserroleMap.objects.filter(user_id=ubj.id).first()
            userRole= Role.objects.filter(id=table1_data.role_id.id).first()
            user = User.objects.get(id=ubj.id)
            request.session["role"]=userRole.role
            request.session["id"]=user.id
            if q and ubj:
                messages.add_message(request, messages.SUCCESS, f"Welcome Back, {userRole.role}")
                return redirect("")
            else:
                return redirect("")
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

            q = User.objects.filter(username=email).filter(is_staff=True)
            table1_data= UserroleMap.objects.filter(user_id=ubj.id).first()
            userRole= Role.objects.filter(id=table1_data.role_id.id).first()
            request.session["role"]=userRole.role
            if q and ubj:
                messages.add_message(request, messages.SUCCESS, f"Welcome Back, {userRole.role}")
                return redirect("")
            else:
                return redirect("")
        else:
            return render(request, 'admin_login.html')
    except Exception as e:
        print(e)
        messages.add_message(request, messages.ERROR, "Something Went Wrong!")
        return render(request, 'admin_login.html')

def logout(request):
    try:
        del request.session['role']
        return redirect('')
    except:
        return HttpResponse('<h3 style="text-align:center"> Somthing went wrong !!!!!</h3>')
    
def test(request):
    role = request.GET.get('role')

    roledata_mapping = {
        'BiobankManager': 'BiobankManager',
        'Researcher': 'Researcher',
    }

    roledata = roledata_mapping.get(role)
    message = f"Create {roledata}"
    
    # Pass roledata and message to the template context
    context = {
        'roledata': roledata,
        'message': message,
    }
    
    return render(request, 'index copy.html', context=context)

def update_user(request, user_id):
    user = User.objects.get(id=user_id)

    if request.method == 'POST':
        # Get the updated information from the form
        user.username = request.POST.get('uname', user.username)
        user.email = request.POST.get('email', user.email)
        user.first_name = request.POST.get('first_name', user.first_name)
        user.middle_name = request.POST.get('middle_name', user.middle_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.position = request.POST.get('position', user.position)
        user.mobile_number = request.POST.get('mobile_number', user.mobile_number)

        try:
            # Attempt to save user
            user.save()
            messages.success(request, "User details updated successfully")
            return redirect('')
        except Exception as e:
            print(f"Error saving user: {e}")  # Log the error
            messages.error(request, f"Error updating user: {e}")

    context = {
        'user': user
    }
    return render(request, 'home.html', context)


def request_deletion(request):
    user_id = request.session.get('id')  # Assuming you set 'id' in the session upon login
    
    # Handle deletion request
    if user_id:  # Check if the user is logged in
        user = UserProfile.objects.get(id=user_id)  # Get the user profile based on session id
        user.deletion_requested = True  # Set the flag for deletion request
        user.save()
        messages.success(request, "Deletion request has been made.")
    else:
        messages.error(request, "You need to be logged in to request deletion.")
        return redirect('/accounts/loginpage/')  # Redirect to the login page
    
    # Get all users who requested deletion (for admin to see)
    # if request.session.get('role') == 'Admin':
    deletion_requests = UserProfile.objects.filter(deletion_requested=True)
    # else:
    #     deletion_requests = []

    
    # Pass the user to the template as well
    return render(request, 'home.html', {
        'deletion_requests': deletion_requests,  # Pass deletion requests to the template for admin
        'user': user,  # Pass the logged-in user to the template
    })

def approve_deletion(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user = UserProfile.objects.get(id=user_id)
        # Perform the actual deletion of the user
        user.delete()
        messages.success(request, f"Account for {user.first_name} {user.last_name} has been deleted.")
    return redirect('')  # Redirect to the admin page

def deny_deletion(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user = UserProfile.objects.get(id=user_id)
        # Simply reset the deletion_requested flag
        user.deletion_requested = False
        user.save()
        messages.success(request, f"Account deletion request for {user.first_name} {user.last_name} has been denied.")
    return redirect('')  # Redirect to the admin page


def reset_password(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        new_password = request.POST.get('new_password')

        try:
            reset_code_obj = PasswordResetCode.objects.get(code=code, is_used=False)

            # Check if code is still valid (e.g., within 24 hours)
            if timezone.now() - reset_code_obj.created_at > timedelta(hours=24):
                return JsonResponse({'success': False, 'message': 'Code expired'})

            # Update the user password
            user = reset_code_obj.user
            user.password = make_password(new_password)
            user.save()

            # Mark the reset code as used
            reset_code_obj.is_used = True
            reset_code_obj.save()

            # return JsonResponse({'success': True, 'message': 'Password updated successfully'})
            messages.success(request, 'Password updated successfully')
            return render(request, 'index.html')
        except PasswordResetCode.DoesNotExist:
            messages.error(request, "Invalid code")
            return render(request, 'reset.html')
            # return JsonResponse({'success': False, 'message': 'Invalid code'})

    return render(request, 'reset.html')

