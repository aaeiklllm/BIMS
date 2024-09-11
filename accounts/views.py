from django.core.checks import messages
from django.shortcuts import redirect, render
from django.http import HttpResponse, response
from django.contrib.auth.models import User
import uuid
from django.contrib import messages
from .models import *
from django.contrib.auth import authenticate
from django.contrib import messages 

def register_user(request, roledata):
    try:
        if request.method =='POST':
            uname=request.POST.get('uname',None)
            email=request.POST.get('eml',None)
            pwd=request.POST.get('pwd',None)

            if User.objects.filter(username=uname).exists():
                messages.add_message(request, messages.ERROR, "User Already Exists")
                return redirect('')
            else:
                user_obj=User.objects.create(username=uname,password=pwd,email=email,is_active=False)
                user_obj.set_password(pwd)
                user_obj.save()
                if roledata == 'BiobankManager':
                    role_name = Role.objects.filter(role='BiobankManager').first()
                    print(role_name.id)
                    userRole= UserroleMap.objects.create(user_id=user_obj, role_id=role_name)
                    userRole.save()
                    messages.add_message(request, messages.SUCCESS, "Biobank Manager pending approval")
                    return redirect('')
                else:
                    role_name = Role.objects.filter(role='Researcher').first()
            
                    userRole= UserroleMap.objects.create(user_id=user_obj, role_id=role_name)
                    userRole.save()
                    messages.add_message(request, messages.SUCCESS, "Researcher pending approval")

                    return redirect('')
        messages.add_message(request, messages.ERROR, "Please Add Valid Details !")
        return render(request, 'ragister.html')    
    except Exception as e:
        print(e)
        messages.add_message(request, messages.ERROR, "Something Went Wrong!")
        return render(request, 'index.html') 
        # Change this index.html

def create_account(request):
    try:
        data={'roledata': 'BiobankManager' , 'message': "Create Biobank Manager"} #Create option to have choices for this
        return  render(request, 'ragister.html', context= data )
    except:
        messages.add_message(request, messages.ERROR, "Something Went Wrong!")  
        return render(request, 'index.html')

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
    print(pending_users)
    

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user = User.objects.get(id=user_id)
        user.is_active = True 
        user.save()
        # Send email notification

    return render(request, 'approve_users.html', {'pending_users': pending_users})



def researcher_login(request):
    try:
        if request.method =='POST':
            email=request.POST.get('eml',None)
            pwd=request.POST.get('pwd',None)
            print(email)
            print(pwd)
            ubj= authenticate(request, username=email, password=pwd) 
            if ubj == None:
                messages.add_message(request, messages.ERROR, "Invalid credentials!")
                print(ubj)
                return redirect('/accounts/researcherlogin')

            q = User.objects.filter(username=email).filter(is_staff=True)
            table1_data= UserroleMap.objects.filter(user_id=ubj.id).first()
            userRole= Role.objects.filter(id=table1_data.role_id.id).first()
            request.session["role"]=userRole.role
            if q and ubj:
                messages.add_message(request, messages.SUCCESS, "Welcome Back Researcher")
                return redirect("")
            else:
                messages.add_message(request, messages.SUCCESS, "Welcome Back Researcher")
                return redirect("")
        else:
            return render(request, 'loginResearcher.html')
    except Exception as e:
        print(e)
        messages.add_message(request, messages.ERROR, "Something Went Wrong!")
        return render(request, 'loginResearcher.html')
    
def manager_login(request):
    try:
        if request.method =='POST':
            email=request.POST.get('eml',None)
            pwd=request.POST.get('pwd',None)
            ubj= authenticate(request, username=email, password=pwd) 
            if ubj == None:
                messages.add_message(request, messages.ERROR, "Invalid credentials!")
                return redirect('/accounts/managerlogin')

            q = User.objects.filter(username=email).filter(is_staff=True)
            table1_data= UserroleMap.objects.filter(user_id=ubj.id).first()
            userRole= Role.objects.filter(id=table1_data.role_id.id).first()
            request.session["role"]=userRole.role
            if q and ubj:
                messages.add_message(request, messages.SUCCESS, "Welcome Back Researcher")
                return redirect("")
            else:
                messages.add_message(request, messages.SUCCESS, "Welcome Back Researcher")
                return redirect("")
        else:
            return render(request, 'loginBM.html')
    except Exception as e:
        print(e)
        messages.add_message(request, messages.ERROR, "Something Went Wrong!")
        return render(request, 'loginBM.html')

def admin_login(request):
    try:
        if request.method =='POST':
            email=request.POST.get('eml',None)
            pwd=request.POST.get('pwd',None)
            ubj= authenticate(request, username=email, password=pwd) 
            if ubj == None:
                messages.add_message(request, messages.ERROR, "Invalid credentials!")
                return redirect('/accounts/loginpage')

            q = User.objects.filter(username=email).filter(is_staff=True)
            table1_data= UserroleMap.objects.filter(user_id=ubj.id).first()
            userRole= Role.objects.filter(id=table1_data.role_id.id).first()
            request.session["role"]=userRole.role
            if q and ubj:
                messages.add_message(request, messages.SUCCESS, "Welcome Back")
                return redirect("")
            else:
                messages.add_message(request, messages.SUCCESS, "Welcome Back")
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

