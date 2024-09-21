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


# @auth_middleware
# def addResearcher(request):
#     try:
#         data={'roledata': 'Researcher' , 'message': "Create Researcher"}
#         return  render(request, 'ragister.html', context= data )
#     except:
#         messages.add_message(request, messages.ERROR, "something went wrong!!")
#         return render(request, 'index.html')

def approve_users(request):
    pending_users = User.objects.filter(is_active=False)
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id')

        if user_id:
            try:
                user = User.objects.get(id=user_id)
                uname = user.username
                email = user.email
                user.is_active = True
                user.save()
                # send email notification here
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
                    return render(request, 'home.html',{'message':'Failed To Send Email'})
                finally:
                    return render(request, 'home.html', {'pending_users': pending_users})
            except User.DoesNotExist:
                pass  

    return render(request, 'home.html', {'pending_users': pending_users})

def login(request):
    try:
        if request.method =='POST':
            email=request.POST.get('eml',None)
            pwd=request.POST.get('pwd',None)
            ubj= authenticate(request, username=email, password=pwd) 
            if ubj == None:
                messages.add_message(request, messages.ERROR, "Invalid credentials/User not activated!")
                return redirect('/accounts/loginpage')

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
            return render(request, 'index.html')
    except Exception as e:
        print(e)
        messages.add_message(request, messages.ERROR, "Something Went Wrong!")
        return render(request, 'index.html')

def logout(request):
    try:
        del request.session['role']
        return redirect('')
    except:
        return HttpResponse('<h3 style="text-align:center"> Somthing went wrong !!!!!</h3>')

