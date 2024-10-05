from django.shortcuts import redirect, render,HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from .models import Samples, Comorbidities, Lab_Test, Aliquot, Storage
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

from .models import Samples, Comorbidities, Lab_Test, Aliquot, Storage

def create_sample(request):
    if request.method == 'POST':
        # Collect Sample data
        type = request.POST.get('type')
        sex = request.POST.get('sex')
        age = request.POST.get('age')
        clinical_diagnosis = request.POST.get('clinical_diagnosis')
        amount = request.POST.get('amount')
        unit = request.POST.get('unit')
        date_collected = request.POST.get('date_collected')
        consent_form = request.FILES.get('consent_form')

        # Create and save Sample instance
        sample = Samples(
            type=type,
            sex=sex,
            age=age,
            clinical_diagnosis=clinical_diagnosis,
            amount=amount,
            unit=unit,
            date_collected=date_collected,
            consent_form=consent_form
        )
        sample.save()

        # Collect Comorbidity data
        comorbidity = request.POST.get('comorbidity')
        if comorbidity:  # Only save if there's a comorbidity
            comorbidity_instance = Comorbidities(
                sample_id=sample,
                comorbidity=comorbidity
            )
            comorbidity_instance.save()

        # Collect Lab Test data
        labtest = request.POST.get('labtest')
        if labtest:  # Only save if there's a lab test
            lab_test_instance = Lab_Test(
                sample_id=sample,
                labtest=labtest
            )
            lab_test_instance.save()

        # Collect Aliquot data
        aliquot_amount = request.POST.get('aliquot_amount')
        aliquot_unit = request.POST.get('aliquot_unit')
        if aliquot_amount and aliquot_unit:  # Ensure both fields are filled
            aliquot_instance = Aliquot(
                sample_id=sample,
                amount=aliquot_amount,
                unit=aliquot_unit
            )
            aliquot_instance.save()

            # Collect Storage data
            freezer_num = request.POST.get('freezer_num')
            shelf_num = request.POST.get('shelf_num')
            rack_num = request.POST.get('rack_num')
            box_num = request.POST.get('box_num')
            container = request.POST.get('container')
            storage_instance = Storage(
                aliquot_id=aliquot_instance,
                sample_id=sample,
                freezer_num=freezer_num,
                shelf_num=shelf_num,
                rack_num=rack_num,
                box_num=box_num,
                container=container
            )
            storage_instance.save()

        return redirect('')  # Redirect to a success page after saving

    return render(request, 'create_sample.html')  # Render the form template on GET request