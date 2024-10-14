from django.shortcuts import redirect, render,HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from .models import Samples, Comorbidities, Lab_Test, Aliquot, Storage
from django.db.models import Max
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
User = get_user_model()
from accounts.models import UserroleMap 


# Create your views here.
def homePage(request):
    try:
        user_id = request.session.get('id')
        print(f"User ID from homePage: {user_id}")
        if user_id:
            user = User.objects.get(id=user_id)
        else:
            return render(request, 'home.html') 

        print(f"User from homePage1: {user}")
        # Get pending users and deletion requests
        pending_users = User.objects.filter(is_active=False)
        deletion_requests = User.objects.filter(deletion_requested=True)

        #For pending
        biobank_managers = []
        researchers = []

        #For deletion
        biobank_managers2 = []
        researchers2 = []

        #For deletion
        biobank_managers2 = []
        researchers2 = []

        # users = User.objects.get(id=user_id)
        for users in pending_users:
            user_role_map = UserroleMap.objects.filter(user_id=users).first()  # Assuming you have this model
            print(f"user_role_map from homePage1: {user_role_map}")
            
            if user_role_map:
                role = user_role_map.role_id.role  # Adjust based on your actual model structure
                print(role)
                if role == 'BiobankManager':
                    biobank_managers.append(users)
                elif role == 'Researcher':
                    researchers.append(users)

        for user in deletion_requests:
            user_role_map2 = UserroleMap.objects.filter(user_id=user).first()
        
            if user_role_map2:
                role = user_role_map2.role_id.role  # Adjust based on your actual model structure
                if role == 'BiobankManager':
                    biobank_managers2.append(user)
                elif role == 'Researcher':
                    researchers2.append(user)

        return render(request, 'home.html', {
            'user': user,
            'pending_users': pending_users,
            'deletion_requests': deletion_requests,
            'biobank_managers': biobank_managers,  
            'researchers': researchers,  
            'biobank_managers2': biobank_managers2,  
            'researchers2': researchers2,            
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
        type_selected = request.POST.get('typeValue')
        sex = request.POST.get('sex')
        age = request.POST.get('age')
        clinical_diagnosis = request.POST.get('clinical_diagnosis')
        amount = request.POST.get('amount')
        unit = request.POST.get('unit')
        date_collected = request.POST.get('date_collected')
        consent_form = request.FILES.get('consent_form')

        # Create and save Sample instance
        sample = Samples(
            type=type_selected,
            sex=sex,
            age=age,
            clinical_diagnosis=clinical_diagnosis,
            amount=amount,
            unit=unit,
            date_collected=date_collected,
            consent_form=consent_form
        )
        sample.save()

        freezer_num = request.POST.get('freezer_num')
        shelf_num = request.POST.get('shelf_num')
        rack_num = request.POST.get('rack_num')
        box_num = request.POST.get('box_num')
        container = request.POST.get('container')

        # Create and save storage instance
        storage_instance = Storage(
            sample_id=sample,  # Reference the sample instance directly
            freezer_num=freezer_num,
            shelf_num=shelf_num,
            rack_num=rack_num,
            box_num=box_num,
            container=container
        )
        storage_instance.save()

       # Collect and save Comorbidities
        comorbidities = request.POST.get('comorbidities')
        if comorbidities:
            for comorbidity in comorbidities.split(','):
                comorbidity_instance = Comorbidities(
                    sample_id=sample,
                    comorbidity=comorbidity.strip()  # Clean any extra spaces
                )
                comorbidity_instance.save()

        # Collect and save Lab Tests
        lab_tests = request.POST.get('lab_tests')
        if lab_tests:
            for lab_test in lab_tests.split(','):
                lab_test_instance = Lab_Test(
                    sample_id=sample,
                    labtest=lab_test.strip()  # Clean any extra spaces
                )
                lab_test_instance.save()

        return redirect('')  # Redirect to a success page after saving

    return render(request, 'create_sample.html')  # Render the form template on GET request

def create_aliquot(request):
    if request.method == 'POST':
        # Get the selected sample ID
        sample_id = request.POST.get('previous_sample_id')
        sample = get_object_or_404(Samples, id=sample_id)
        
        # Collect Aliquot data
        aliquot_amount = request.POST.get('amount2')
        aliquot_unit = request.POST.get('unit2')

        # Create and save Aliquot instance
        aliquot_instance = Aliquot(
            sample_id=sample,
            amount=aliquot_amount,
            unit=aliquot_unit
        )
        aliquot_instance.save()

        # Collect Storage data
        freezer_num = request.POST.get('freezer_num2')
        shelf_num = request.POST.get('shelf_num2')
        rack_num = request.POST.get('rack_num2')
        box_num = request.POST.get('box_num2')
        container = request.POST.get('container2')

        # Create and save Storage instance, linking it to the saved aliquot
        storage_instance = Storage(
            sample_id=sample,  # Reference the sample instance directly
            aliquot_id=aliquot_instance,  # Link to the aliquot
            freezer_num=freezer_num,
            shelf_num=shelf_num,
            rack_num=rack_num,
            box_num=box_num,
            container=container
        )
        storage_instance.save()

        return redirect('')  # Redirect to a success page after saving

    return render(request, 'create_sample.html')  # Render the form template on GET request

def get_latest_sample_id(request):
    latest_sample = Samples.objects.aggregate(Max('id'))
    next_sample_id = (latest_sample['id__max'] or 0) + 1
    return JsonResponse({'sample_id': next_sample_id})

def get_sample_ids(request):
    sample_ids = list(Samples.objects.values_list('id', flat=True))
    return JsonResponse({'sample_ids': sample_ids})

def get_sample_unit(request):
    if request.method == 'GET':
        sample_id = request.GET.get('sample_id')  
        if sample_id:
            try:
                sample = Samples.objects.get(id=sample_id)
                return JsonResponse({'unit': sample.unit}) 
            except Samples.DoesNotExist:
                return JsonResponse({'error': 'Sample not found'}, status=404)

    return JsonResponse({'error': 'Invalid request'}, status=400)

def view_sample(request):
    samples = Samples.objects.prefetch_related('comorbidities_set', 'lab_test_set', 'aliquot_set', 'storage_set')
    return render(request, 'view_sample.html', {'samples': samples})

def sample_detail(request, sample_id):
    # Fetch the specific sample, prefetching related comorbidities, lab tests, aliquots, and storage
    sample = get_object_or_404(Samples.objects.prefetch_related('comorbidities_set', 'lab_test_set', 'aliquot_set', 'storage_set'), id=sample_id)

    # Get all related storage details
    first_storage_info = sample.storage_set.first()
    
    # Get total number of aliquots for the sample
    total_aliquots = sample.aliquot_set.count()
    
    # Get individual aliquots and their associated storage
    aliquots = sample.aliquot_set.prefetch_related('storage_set').all()

    return render(request, 'sample_detail.html', {
        'sample': sample,
        'first_storage_info': first_storage_info,
        'total_aliquots': total_aliquots,
        'aliquots': aliquots,
    })
