from django.shortcuts import redirect, render,HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from .models import Samples, Comorbidities, Lab_Test, Aliquot, Storage
from django.db.models import Max
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
User = get_user_model()
from accounts.models import UserroleMap 
from .models import Request_Sample, Research_Project, RS_Comorbidities, RS_Lab_Test, RS_Step4, RS_Step5, Approve_Reject_Request, Acknowledgement_Receipt, Acknowledgement_Storage
from datetime import datetime
from django.core.exceptions import ValidationError

# Create your views here.

def home(request):
    return render(request, 'home.html')  

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
        'biobank_managers': biobank_managers,
        'researchers': researchers,
        'active_tab': 'deletion_requests'
    })


def admin_home(request):
    try:
        user_id = request.session.get("user_id") 
        user = User.objects.get(id=user_id)  
       
        print(f"User ID from homePage: {user_id}")
        if user_id:
            user = User.objects.get(id=user_id)
        else:
            return render(request, 'admin_home.html') 

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

        return render(request, 'admin_home.html', {
            'user': user,
            'pending_users': pending_users,
            'deletion_requests': deletion_requests,
            'biobank_managers': biobank_managers,  
            'researchers': researchers,  
            'biobank_managers2': biobank_managers2,  
            'researchers2': researchers2,  
            'deletion_request_count': deletion_requests.count(),
            'creation_request_count': pending_users.count(),
            'active_tab': 'creation_requests'      
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



def request_sample(request):
    if request.method == 'POST':
        # Collect Request Sample data
        erb_approval = request.FILES.get('erb_approval')
        type_selected = request.POST.get('typeValue')
        sex = request.POST.get('sex')
        age = request.POST.get('age')
        clinical_diagnosis = request.POST.get('clinical_diagnosis')
        amount = request.POST.get('amount')
        unit = request.POST.get('unit')
        desired_start_date = request.POST.get('desired_start_date')

        # Validate and parse the desired_start_date
        if desired_start_date:
            try:
                desired_start_date = datetime.strptime(desired_start_date, '%Y-%m-%d').date()
            except ValueError:
                raise ValidationError(f"{desired_start_date} is not a valid date. Expected format: YYYY-MM-DD.")
        else:
            desired_start_date = None


        # Create and save Request Sample instance
        request_sample = Request_Sample.objects.create(
            erb_approval=erb_approval,
            type=type_selected, 
            sex=sex,
            age=age,
            clinical_diagnosis=clinical_diagnosis,
            amount=amount,
            unit=unit,
            desired_start_date=desired_start_date
        )
        request_sample.save()
       
        # Collect Research Project data
        title = request.POST.get('title')
        principal_investigator = request.POST.get('investigator')
        description = request.POST.get('description')
        anticipated_initiation_date = request.POST.get('initiation_date')
        anticipated_completion_date = request.POST.get('completion_date')
        erb_number = request.POST.get('erb')
        funding_source = request.POST.get('funding')

        # Validate and parse dates for Research Project
        if anticipated_initiation_date:
            try:
                anticipated_initiation_date = datetime.strptime(anticipated_initiation_date, '%Y-%m-%d').date()
            except ValueError:
                raise ValidationError(f"{anticipated_initiation_date} is not a valid date. Expected format: YYYY-MM-DD.")
        else:
            anticipated_initiation_date = None

        if anticipated_completion_date:
            try:
                anticipated_completion_date = datetime.strptime(anticipated_completion_date, '%Y-%m-%d').date()
            except ValueError:
                raise ValidationError(f"{anticipated_completion_date} is not a valid date. Expected format: YYYY-MM-DD.")
        else:
            anticipated_completion_date = None

        # Create and save Research Project instance
        research_project = Research_Project.objects.create(
            request_sample=request_sample,  # Associate with the request sample
            title=title,
            principal_investigator=principal_investigator,
            description=description,
            anticipated_initiation_date=anticipated_initiation_date,
            anticipated_completion_date=anticipated_completion_date,
            erb_number=erb_number,
            funding_source=funding_source,
        )
        research_project.save()
    
    return render(request, 'request_sample.html')


def request_sample_step2(request):
    if request.method == 'POST':

        # Collect Request Sample data
        erb_approval = request.FILES.get('erb_approval')
        
        # Create and save Request Sample instance
        request_sample = Request_Sample(
            erb_approval = erb_approval
        )
        request_sample.save()
        
    return render(request, 'request_sample_2.html')


def request_sample_step3(request):
    if request.method == 'POST':
        # Collect Request Sample data
        type_selected = request.POST.get('typeValue')
        sex = request.POST.get('sex')
        age = request.POST.get('age')
        clinical_diagnosis = request.POST.get('clinical_diagnosis')
        amount = request.POST.get('amount')
        unit = request.POST.get('unit')

        # Create and save Request Sample instance
        rs_step3 = RS_Step3(
            type=type_selected, 
            sex=sex,
            age=age,
            clinical_diagnosis=clinical_diagnosis,
            amount=amount,
            unit=unit,
        )
        rs_step3.save()

        # Collect and save Comorbidities
        comorbidities = request.POST.get('comorbidities')
        if comorbidities:
            for comorbidity in comorbidities.split(','):
                comorbidity_instance = RS_Comorbidities(
                    step3_id = rs_step3,
                    comorbidity=comorbidity.strip()  # Clean any extra spaces
                )
                comorbidity_instance.save()

        # Collect and save Lab Tests
        lab_tests = request.POST.get('lab_tests')
        if lab_tests:
            for lab_test in lab_tests.split(','):
                lab_test_instance = RS_Lab_Test(
                    step3_id = rs_step3,
                    labtest=lab_test.strip()  # Clean any extra spaces
                )
                lab_test_instance.save()

    return render(request, 'request_sample_3.html')

def request_sample_step4(request):
    if request.method == 'POST':
        # Collect Step4 data
        multiple_samples = request.POST.get('multiple_samples')
        time_points = request.POST.get('time_points')
        interval = request.POST.get('interval')
        interval_unit = request.POST.get('interval_unit')
        start_date_ddmmyyyy = request.POST.get('start_date_ddmmyyyy')
        start_date_mmyyyy = request.POST.get('start_date_mmyyyy')
        start_date_yyyy = request.POST.get('start_date_yyyy')

        # Set default None values if the fields are not filled out
        if not start_date_ddmmyyyy:
            start_date_ddmmyyyy = None
        if not start_date_mmyyyy:
            start_date_mmyyyy = None
        if not start_date_yyyy:
            start_date_yyyy = None

        # Create and save Step4 instance
        rs_step4 = RS_Step4(
            multiple_samples=multiple_samples, 
            time_points=time_points,
            interval=interval,
            interval_unit=interval_unit,
            start_date_ddmmyyyy=start_date_ddmmyyyy,
            start_date_mmyyyy=start_date_mmyyyy,
            start_date_yyyy=start_date_yyyy,
        )
        rs_step4.save()
    
    return render(request, 'request_sample_4.html')

def request_sample_step5(request):
    if request.method == 'POST':
        # Collect Step5 data
        different_sources = request.POST.get('different_sources')
        num_participants = request.POST.get('num_participants')
        multiple_timepoints_each = request.POST.get('multiple_timepoints_each')
        time_points = request.POST.get('time_points')
        interval = request.POST.get('interval')
        interval_unit = request.POST.get('interval_unit')
        start_date_ddmmyyyy = request.POST.get('start_date_ddmmyyyy')
        start_date_mmyyyy = request.POST.get('start_date_mmyyyy')
        start_date_yyyy = request.POST.get('start_date_yyyy')
        collection_date_ddmmyyyy = request.POST.get('collection_date_ddmmyyyy')
        collection_date_mmyyyy = request.POST.get('collection_date_mmyyyy')
        collection_date_yyyy = request.POST.get('collection_date_yyyy')

        # Set default None values if the fields are not filled out
        start_date_ddmmyyyy = start_date_ddmmyyyy if start_date_ddmmyyyy else None
        start_date_mmyyyy = start_date_mmyyyy if start_date_mmyyyy else None
        start_date_yyyy = start_date_yyyy if start_date_yyyy else None
        collection_date_ddmmyyyy = collection_date_ddmmyyyy if collection_date_ddmmyyyy else None
        collection_date_mmyyyy = collection_date_mmyyyy if collection_date_mmyyyy else None
        collection_date_yyyy = collection_date_yyyy if collection_date_yyyy else None

        # Handle the time_points field
        # If "No" is selected for multiple_timepoints_each, ignore time_points
        if multiple_timepoints_each == 'no':
            time_points = None  # Set time_points to None if "No" for multiple time points

        # Create and save Step5 instance
        rs_step5 = RS_Step5(
            different_sources=different_sources,
            num_participants=num_participants, 
            multiple_timepoints_each=multiple_timepoints_each,
            time_points=time_points,
            interval=interval,
            interval_unit = interval_unit,
            start_date_ddmmyyyy=start_date_ddmmyyyy,
            start_date_mmyyyy=start_date_mmyyyy,
            start_date_yyyy=start_date_yyyy, 
            collection_date_ddmmyyyy=collection_date_ddmmyyyy,
            collection_date_mmyyyy=collection_date_mmyyyy,
            collection_date_yyyy=collection_date_yyyy,
        )
        rs_step5.save()
    return render(request, 'request_sample_5.html')

def request_sample_step6(request):
    if request.method == 'POST':
        # Collect Step6 data
        desired_start_date = request.POST.get('desired_start_date')

        # Create and save Step6 instance
        rs_step6 = RS_Step6(
            desired_start_date=desired_start_date,
        )
        rs_step6.save()

    return render(request, 'request_sample_6.html')

def request_sample_step7(request):
    return render(request, 'request_sample_7.html')

def request_sample_ty(request):
    return render(request, 'request_sample_ty.html')