from django.shortcuts import redirect, render,HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from .models import Samples, Comorbidities, Lab_Test, Aliquot, Storage
from django.db.models import Max
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
User = get_user_model()
from accounts.models import UserroleMap 
from .models import Request_Sample, Research_Project, RS_Comorbidities, RS_Lab_Test, RS_Step4, RS_Step5, Approve_Reject_Request, Create_Ack_Receipt, Ack_Sample
from datetime import datetime
from django.core.exceptions import ValidationError
from django.contrib import messages 
from django.db.models import Prefetch
from accounts.models import UserProfile
from django.db.models import Q
from django.utils import timezone
from django.db import transaction
from django.core.files.storage import default_storage
from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from collections import defaultdict
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.checks import messages
from django.contrib import messages 

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import textwrap  

import pytz
from django.db.models import Prefetch
from accounts.models import UserProfile
from django.db.models import Q
from django.utils import timezone
from django.db import transaction

from django.http import FileResponse, Http404
from django.core.files.base import ContentFile
from reportlab.pdfgen import canvas
from django.urls import reverse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from django.db import transaction

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
@transaction.atomic
def create_sample(request):
    if request.method == 'POST':
        # Collect Sample data
        id_created = request.POST.get('sample_id')
        type_selected = request.POST.get('typeValue')
        sex = request.POST.get('sex')
        age = request.POST.get('age')
        clinical_diagnosis = request.POST.get('clinical_diagnosis')
        other_diagnosis = request.POST.get("other_diagnosis")
        amount = request.POST.get('amount')
        unit = request.POST.get('unit')
        date_collected = request.POST.get('date_collected')
        consent_form = request.FILES.get('consent_form')

        if clinical_diagnosis == "Others":
            clinical_diagnosis = other_diagnosis

        try:
            # Create and save Sample instance
            sample = Samples(
                id = id_created,
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

            messages.success(request, f"Sample created successfully.")
            return redirect('')  # Redirect to a success page after saving
        
        except Exception as e:
            messages.error(request, f"Error creating sample: {e}")
            return redirect('create_sample.html')

    used_containers = Storage.objects.values_list('container', flat=True)

    return render(request, 'create_sample.html', {'used_containers': list(used_containers)})

@transaction.atomic
def create_aliquot(request):
    if request.method == 'POST':
        # Get the selected sample ID
        sample_id = request.POST.get('previous_sample_id')
        sample = get_object_or_404(Samples, id=sample_id)
        
        # Collect Aliquot data
        aliquot_amount = request.POST.get('amount2')
        aliquot_unit = request.POST.get('unit2')

        try:
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

            messages.success(request, f"Aliquot successfully created from sample.")
            return redirect('')  # Redirect to a success page after saving
    
        except Exception as e:
            messages.error(request, f"Error creating aliquot: {e}")
            return redirect('')

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

@transaction.atomic
def view_sample(request):
    research_projects = Research_Project.objects.prefetch_related(
        'request_samples__sample'  # Prefetch samples through request_samples
    ).all()

    # Prepare the project data
    projects = []
    for project in research_projects:
        # Get all sample IDs linked to the project
        sample_ids = [
            sample.id
            for request_sample in project.request_samples.all()
            for sample in request_sample.sample.all()
        ]
        projects.append({"name": project.title, "count": len(sample_ids), "sample_ids": sample_ids})

    samples = Samples.objects.prefetch_related('comorbidities_set', 'lab_test_set', 'aliquot_set', 'storage_set').order_by('last_modified')
    request_samples_dict = {}
    for sample in samples:
        sample_id = sample.id
        ack_samples = Ack_Sample.objects.filter(sample_id=sample_id)

        request_samples = []

        for ack_sample in ack_samples:
            print(f"Ack_Sample ID: {ack_sample.id}")

            # Get the related Create_Ack_Receipt
            ack_receipt = ack_sample.create_ack_receipt
            if not ack_receipt:
                print(f"No associated Create_Ack_Receipt found for Ack_Sample ID: {ack_sample.id}")
                continue 

            print(f"Create Ack Receipt: {ack_receipt.id}")

            # Get the related Approve_Reject_Request
            approval_record = Approve_Reject_Request.objects.filter(create_ack_receipt=ack_receipt).first()
            if not approval_record:
                print(f"No associated Approve_Reject_Request found for Create_Ack_Receipt ID: {ack_receipt.id}")
                continue  

            print(f"Approval Record: {approval_record.id}")

            # Get the associated Request_Sample
            request_sample = approval_record.request_sample
            if not request_sample:
                print(f"No associated Request_Sample found for Approve_Reject_Request ID: {approval_record.id}")
                continue 

            print(f"Request Sample: {request_sample.id}")

            if request_sample not in request_samples:
                request_samples.append(request_sample)

        # Add the list of request_samples to the dictionary, keyed by sample_id
        if request_samples:
            request_samples_dict[sample_id] = request_samples
            print(f"request_samples_dict: {request_samples_dict}")
    return render(request, 'view_sample.html', {'samples': samples, 'projects': projects, 'request_samples': request_samples, 'request_samples_dict': request_samples_dict})

# def sample_detail(request, sample_id):
#     # Fetch the specific sample, prefetching related comorbidities, lab tests, aliquots, and storage
#     sample = get_object_or_404(Samples.objects.prefetch_related('comorbidities_set', 'lab_test_set', 'aliquot_set', 'storage_set'), id=sample_id)

#     # Get all related storage details
#     first_storage_info = sample.storage_set.first()
    
#     # Get total number of aliquots for the sample
#     total_aliquots = sample.aliquot_set.count()
    
#     # Get individual aliquots and their associated storage
#     aliquots = sample.aliquot_set.prefetch_related('storage_set').all()

#     return render(request, 'sample_detail.html', {
#         'sample': sample,
#         'first_storage_info': first_storage_info,
#         'total_aliquots': total_aliquots,
#         'aliquots': aliquots,
#     })

@transaction.atomic
def edit_sample(request, sample_id):
    # Fetch the existing sample and its related data
    sample = get_object_or_404(Samples.objects.prefetch_related('comorbidities_set', 'lab_test_set', 'aliquot_set', 'storage_set'), id=sample_id)

    if request.method == "POST":
        # Collect Sample data from the form
        type_selected = request.POST.get('typeValue', sample.type)
        sex = request.POST.get('sex', sample.sex)
        age = request.POST.get('age', sample.age)
        clinical_diagnosis = request.POST.get('clinical_diagnosis', sample.clinical_diagnosis)
        amount = request.POST.get('amount', sample.amount)
        unit = request.POST.get('unit', sample.unit)
        date_collected = request.POST.get('date_collected', sample.date_collected)
        consent_form = request.FILES.get('consent_form')
        # Retrieve form values from POST request
        freezer_num = request.POST.get('freezer_num')
        shelf_num = request.POST.get('shelf_num')
        rack_num = request.POST.get('rack_num')
        box_num = request.POST.get('box_num')

        # Update the sample instance's fields
        sample.type = type_selected
        sample.sex = sex
        sample.age = age
        sample.clinical_diagnosis = clinical_diagnosis
        sample.amount = amount
        sample.unit = unit
        sample.date_collected = date_collected

        storage_instance = sample.storage_set.first()  # Use .first() to get a single instance

        # Check if a storage instance exists before trying to update it
        if storage_instance:
            # Update the storage attributes
            storage_instance.freezer_num = freezer_num
            storage_instance.shelf_num = shelf_num
            storage_instance.rack_num = rack_num
            storage_instance.box_num = box_num
            storage_instance.save()  # Save changes to storage instance

        # Update the consent form only if a new file is uploaded
        if consent_form:
            sample.consent_form = consent_form

        sample.save()              # Save changes in sample


        # Update Comorbidities
        comorbidities = request.POST.get('comorbidities', '')
        
        # Clear existing comorbidities
        sample.comorbidities_set.all().delete()  # Clear existing entries if you want to replace them

        # Add new comorbidities
        if comorbidities:
            for comorbidity in comorbidities.split(','):
                comorbidity_instance = Comorbidities(
                    sample_id=sample,
                    comorbidity=comorbidity.strip()  # Clean any extra spaces
                )
                comorbidity_instance.save()

        # Update Lab Tests
        lab_tests = request.POST.get('lab_tests', '')

        # Clear existing lab tests
        sample.lab_test_set.all().delete()  # Clear existing entries if you want to replace them

        # Add new lab tests
        if lab_tests:
            for lab_test in lab_tests.split(','):
                lab_test_instance = Lab_Test(
                    sample_id=sample,
                    labtest=lab_test.strip()  # Clean any extra spaces
                )
                lab_test_instance.save()

        messages.success(request, "Sample information updated successfully.")
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

    return render(request, 'edit_sample.html', {'sample': sample})

def delete_sample(request, sample_id):
    sample = get_object_or_404(Samples.objects.prefetch_related('comorbidities_set', 'lab_test_set', 'aliquot_set', 'storage_set'), id=sample_id)

    if request.method == "POST":
        # Handle the deletion
        if "confirm_delete" in request.POST:
            sample.delete()
            messages.success(request, "Sample deleted successfully.")

    samples = Samples.objects.prefetch_related('comorbidities_set', 'lab_test_set', 'aliquot_set', 'storage_set')
    return render(request, 'view_sample.html', {'samples': samples})

@transaction.atomic
def request_sample(request):
    user_id = request.session.get("user_id")  # Get the user ID from the session
    if not user_id:
        # Redirect to login page if no user ID is found in the session
        messages.error(request, "You need to be logged in to make a request.")
        return redirect('accounts:loginpage')

    current_user = User.objects.get(id=user_id)  # Get the user using the ID

    # Fetch all research projects from the database
    research_projects = Research_Project.objects.all()
    request_samples = Request_Sample.objects.all()
    
    projects_context = []

    for project in research_projects:
        # Check if the user has requested a sample for this project
        has_requested_sample = project.request_samples.filter(requested_by=request.user).exists()
        
        # Check if the project is past its anticipated completion date
        if project.anticipated_completion_date and project.anticipated_completion_date < datetime.now().date():
            is_past_due = True
        else:
            is_past_due = False

        # Store the project with its precomputed conditions
        projects_context.append({
            'project': project,
            'has_requested_sample': has_requested_sample,
            'is_past_due': is_past_due,
        })

    if request.method == 'POST':
        selected_project_id = request.POST.get('existing-project')  # Get selected project ID
        selected_project = None
        
        if selected_project_id:
            # Fetch the project from the database
            selected_project = get_object_or_404(Research_Project, id=selected_project_id)

        try:

            # Collect Request Sample data
            erb_approval = request.FILES.get('erb_approval')
            type_selected = request.POST.get('typeValue')
            sex = request.POST.get('sex')
            age = request.POST.get('age')
            age_from = request.POST.get('age_from')
            age_to = request.POST.get('age_to')
            clinical_diagnosis = request.POST.get('clinical_diagnosis')
            other_diagnosis = request.POST.get("other_diagnosis")
            amount = request.POST.get('amount')
            unit = request.POST.get('unit')
            desired_start_date = request.POST.get('desired_start_date')

            if clinical_diagnosis == "Others":
                clinical_diagnosis = other_diagnosis

            # Convert the desired_start_date to a date format if it's provided
            if desired_start_date:
                if desired_start_date == "":  # Handle empty or null values
                    desired_start_date = None
                else: 
                    try:
                        desired_start_date = datetime.strptime(desired_start_date, '%Y-%m-%d').date()
                    except ValueError:
                        raise ValidationError(f"{desired_start_date} is not a valid date. Expected format: YYYY-MM-DD.")
            else:
                desired_start_date = None

            if age == '':
                age = None
            if amount == '':
                amount = None

            # Create and save Request Sample instance
            request_sample = Request_Sample(
                erb_approval=erb_approval,
                type=type_selected, 
                sex=sex,
                age=age,
                age_from=age_from,
                age_to=age_to,
                clinical_diagnosis=clinical_diagnosis,
                amount=amount,
                unit=unit,
                desired_start_date=desired_start_date,
                requested_by=request.user,
                research_project=selected_project
            )
            request_sample.save()

            if not selected_project:
                # Create a new project if no existing one was selected
                title = request.POST.get('title')
                principal_investigator = request.POST.get('investigator')
                description = request.POST.get('description')
                anticipated_initiation_date = request.POST.get('initiation-date')
                anticipated_completion_date = request.POST.get('completion-date')
                erb_number = request.POST.get('erb')
                funding_source = request.POST.get('funding')

                # Convert anticipated initiation and completion dates if provided
                if anticipated_initiation_date:
                    if anticipated_initiation_date == "":  # Handle empty or null values
                        anticipated_initiation_date = None
                    else: 
                        try:
                            anticipated_initiation_date = datetime.strptime(anticipated_initiation_date, '%Y-%m-%d').date()
                        except ValueError:
                            raise ValidationError(f"{anticipated_initiation_date} is not a valid date. Expected format: YYYY-MM-DD.")
                else:
                    anticipated_initiation_date = None

                if anticipated_completion_date:
                    if anticipated_completion_date == "":  # Handle empty or null values
                        anticipated_completion_date = None
                    else: 
                        try:
                            anticipated_completion_date = datetime.strptime(anticipated_completion_date, '%Y-%m-%d').date()
                        except ValueError:
                            raise ValidationError(f"{anticipated_completion_date} is not a valid date. Expected format: YYYY-MM-DD.")
                else:
                    anticipated_completion_date = None

                # Create and associate the new project with the request sample
                new_project = Research_Project.objects.create(
                    title=title,
                    principal_investigator=principal_investigator,
                    description=description,
                    anticipated_initiation_date=anticipated_initiation_date,
                    anticipated_completion_date=anticipated_completion_date,
                    erb_number=erb_number,
                    funding_source=funding_source
                )

                # Link the new project to the request sample
                request_sample.research_project = new_project
                request_sample.save()

            # Collect and save Comorbidities
            comorbidities = request.POST.get('comorbidities')
            if comorbidities:
                for comorbidity in comorbidities.split(','):
                    comorbidity_instance = RS_Comorbidities(
                        request_sample = request_sample,
                        comorbidity=comorbidity.strip()  # Clean any extra spaces
                    )
                    comorbidity_instance.save()

            # Collect and save Lab Tests
            lab_tests = request.POST.get('lab_tests')
            if lab_tests:
                for lab_test in lab_tests.split(','):
                    lab_test_instance = RS_Lab_Test(
                        request_sample = request_sample,
                        labtest=lab_test.strip()  # Clean any extra spaces
                    )
                    lab_test_instance.save()
        
            # Collect Step4 data
            multiple_samples = request.POST.get('multiple_samples')
            time_points1 = request.POST.get('time_points1')
            interval = request.POST.get('interval')
            interval_unit = request.POST.get('interval_unit')
            start_date_ddmmyyyy = request.POST.get('start_date_ddmmyyyy')
            start_date_mmyyyy = request.POST.get('start_date_mmyyyy')
            start_date_yyyy = request.POST.get('start_date_yyyy')

            # Validate and parse the start_date_ddmmyyyy
            if start_date_ddmmyyyy:
                if start_date_ddmmyyyy == "":  # Handle empty or null values
                    start_date_ddmmyyyy = None
                else: 
                    try:
                        start_date_ddmmyyyy = datetime.strptime(start_date_ddmmyyyy, '%Y-%m-%d').date()
                    except ValueError:
                        raise ValidationError(f"{start_date_ddmmyyyy} is not a valid date. Expected format: YYYY-MM-DD.")
            else:
                start_date_ddmmyyyy = None

            # Ensure 'time_points1', 'interval', and 'start_date_yyyy' are None if empty
            if time_points1 == '':
                time_points1 = None
            else:
                time_points1 = int(time_points1) if time_points1 else None  # Convert to int if not None

            # Initialize interval as None by default
            if interval == '':
                interval = None
            else:
                try:
                    interval = int(interval)  # Convert to int if provided
                except ValueError:
                    interval = None  # Handle case where conversion fails

            if start_date_yyyy == '':
                start_date_yyyy = None
            else:
                start_date_yyyy = int(start_date_yyyy) if start_date_yyyy else None  # Convert to int if not None


            # Create and save Step4 instance
            rs_step4 = RS_Step4(
                request_sample=request_sample,  # Associate with the request sample
                multiple_samples=multiple_samples, 
                time_points1=time_points1,
                interval=interval,
                interval_unit=interval_unit,
                start_date_ddmmyyyy=start_date_ddmmyyyy,
                start_date_mmyyyy=start_date_mmyyyy,
                start_date_yyyy=start_date_yyyy,
            )
            rs_step4.save()

            # Collect Step5 data
            different_sources = request.POST.get('different_sources')
            num_participants = request.POST.get('num_participants')
            multiple_timepoints_each = request.POST.get('multiple_timepoints_each')
            time_points2 = request.POST.get('time_points2')
            interval = request.POST.get('interval')
            interval_unit = request.POST.get('interval_unit')
            start_date_ddmmyyyy = request.POST.get('start_date_ddmmyyyy')
            start_date_mmyyyy = request.POST.get('start_date_mmyyyy')
            start_date_yyyy = request.POST.get('start_date_yyyy')
            collection_date_ddmmyyyy = request.POST.get('collection_date_ddmmyyyy')
            collection_date_mmyyyy = request.POST.get('collection_date_mmyyyy')
            collection_date_yyyy = request.POST.get('collection_date_yyyy')

            # Validate and parse the start_date_ddmmyyyy
            if start_date_ddmmyyyy:
                if start_date_ddmmyyyy == "":  # Handle empty or null values
                    start_date_ddmmyyyy = None
                else: 
                    try:
                        start_date_ddmmyyyy = datetime.strptime(start_date_ddmmyyyy, '%Y-%m-%d').date()
                    except ValueError:
                        raise ValidationError(f"{start_date_ddmmyyyy} is not a valid date. Expected format: YYYY-MM-DD.")
            else:
                start_date_ddmmyyyy = None

            if collection_date_ddmmyyyy:
                if collection_date_ddmmyyyy == "":  # Handle empty or null values
                    collection_date_ddmmyyyy = None
                else:
                    try:
                        collection_date_ddmmyyyy = datetime.strptime(collection_date_ddmmyyyy, '%Y-%m-%d').date()
                    except ValueError:
                        raise ValidationError(f"{collection_date_ddmmyyyy} is not a valid date. Expected format: YYYY-MM-DD.")
            else:
                collection_date_ddmmyyyy = None

            if num_participants == '':
                num_participants = None
            if time_points2 == '':
                time_points2 = None
            if interval == '':
                interval = None
            if start_date_yyyy == '':
                start_date_yyyy = None
            if collection_date_yyyy == '':
                collection_date_yyyy = None

            # Handle the time_points2 field
            # If "No" is selected for multiple_timepoints_each, ignore time_points2
            if multiple_timepoints_each == 'no':
                time_points2 = None  # Set time_points2 to None if "No" for multiple time points

            # Create and save Step5 instance
            rs_step5 = RS_Step5(
                request_sample=request_sample,  # Associate with the request sample
                different_sources=different_sources,
                num_participants=num_participants, 
                multiple_timepoints_each=multiple_timepoints_each,
                time_points2=time_points2,
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

            approval_record = Approve_Reject_Request.objects.create(
                request_sample=request_sample,  # Associate the request_sample here
                approve_reject="pending",
            )
            approval_record.save()
            
            messages.success(request, f"Sample request created successfully.")
            return redirect('request_sample_step7', sample_id=request_sample.id)
        except Exception as e:
            messages.error(request, f"Error creating sample request: {e}")
            return redirect('')

    # For a GET request, render the form page
    return render(request, 'request_sample.html', {'research_projects': research_projects, 'request_samples': request_samples, 'projects_context': projects_context})

def calculate_total_samples(step4, step5):
    # Start with 0 samples initially (after Step 3)
    total_samples = 0

    # Step 4: Adding time points if multiple samples are requested
    if step4 and step4.multiple_samples == 'yes':
        time_points_step4 = step4.time_points1 or 0
        total_samples += time_points_step4

        # Step 5: Adding participants and multiplying if multiple time points are selected
        if step5 and step5.different_sources == 'yes':
            # Number of additional participants from Step 5
            num_participants = step5.num_participants or 0
            
            # Check if multiple time points are required for each participant
            if step5.multiple_timepoints_each == 'yes':
                time_points_step5 = step5.time_points2 or 1
                total_samples += num_participants * time_points_step5
            else:
                # If no time points, just add the number of participants
                total_samples += num_participants
        if step5 and step5.different_sources == 'no':
            total_samples = total_samples

    elif step4 and step4.multiple_samples == 'no':
        # If Step 4 is "no", we still account for the initial sample
        total_samples = 0

        # Step 5: Adding participants and multiplying if multiple time points are selected
        if step5 and step5.different_sources == 'yes':
            # Number of additional participants from Step 5
            num_participants = step5.num_participants or 0
            
            # Check if multiple time points are required for each participant
            if step5.multiple_timepoints_each == 'yes':
                time_points_step5 = step5.time_points2 or 1
                total_samples += num_participants * time_points_step5
            else:
                # If no time points, just add the number of participants
                total_samples += num_participants
        if step5 and step5.different_sources == 'no':
            total_samples = 1

    return total_samples


def request_sample_step7(request, sample_id):
    # Fetch the request sample from the database using the sample_id
    request_sample = get_object_or_404(Request_Sample, id=sample_id)
    research_project = request_sample.research_project  # Access the single related project
    comorbidities = RS_Comorbidities.objects.filter(request_sample=request_sample)
    lab_tests = RS_Lab_Test.objects.filter(request_sample=request_sample)
    step4_data = RS_Step4.objects.filter(request_sample=request_sample).first()
    step5_data = RS_Step5.objects.filter(request_sample=request_sample).first()

    # Calculate the total number of sample requests using the helper function
    total_samples = calculate_total_samples(step4_data, step5_data)

    # Prepare context with all the fetched data
    context = {
        'request_sample': request_sample,
        'research_project': research_project,  # Pass the single related project
        'comorbidities': comorbidities,
        'lab_tests': lab_tests,
        'step4': step4_data,
        'step5': step5_data,
        'total_samples': total_samples  # Add this line
    }
    
    return render(request, 'request_sample_step7.html', context)

def request_sample_ty(request):
    return render(request, 'request_sample_ty.html')

def delete_request_sample(request, pk):
    request_sample = get_object_or_404(Request_Sample, pk=pk)
    request_sample.delete()
    messages.success(request, "Request sample deleted successfully.")
    return redirect('')  # Replace with your desired redirect URL

@transaction.atomic
def edit_request_sample(request, sample_id):
    # Fetch the existing Request Sample and its associated project
    request_sample = get_object_or_404(Request_Sample, id=sample_id)
    research_projects = Research_Project.objects.all()  

    existing_comorbidities = RS_Comorbidities.objects.filter(request_sample=request_sample)
    existing_comorbidities_list = [comorbidity.comorbidity for comorbidity in existing_comorbidities]

    existing_lab_tests = RS_Lab_Test.objects.filter(request_sample=request_sample)
    existing_lab_tests_list = [lab_test.labtest for lab_test in existing_lab_tests]

    rs_step4 = RS_Step4.objects.filter(request_sample=request_sample).first()
    rs_step5 = RS_Step5.objects.filter(request_sample=request_sample).first()

    request_samples = Request_Sample.objects.all()
    
    projects_context = []

    for project in research_projects:
        # Check if the user has requested a sample for this project
        has_requested_sample = project.request_samples.filter(requested_by=request.user).exists()
        
        # Check if the project is past its anticipated completion date
        if project.anticipated_completion_date and project.anticipated_completion_date < datetime.now().date():
            is_past_due = True
        else:
            is_past_due = False

        # Store the project with its precomputed conditions
        projects_context.append({
            'project': project,
            'has_requested_sample': has_requested_sample,
            'is_past_due': is_past_due,
        })
    
    if request.method == 'POST':
        # Check if the user selected to create a new project or select an existing one
        project_option = request.POST.get('project')  # 'existing' or 'new'
        selected_project_id = request.POST.get('existing-project')  # Get the selected existing project ID

        try:

            if project_option == 'existing' and selected_project_id:
                # Associate the selected existing project with the sample
                selected_project = get_object_or_404(Research_Project, id=selected_project_id)
                request_sample.research_project = selected_project  # Set the ForeignKey to the selected project
                request_sample.save()

            elif project_option == 'new':
                # Collect new project data from the form
                title = request.POST.get('title')
                principal_investigator = request.POST.get('investigator')
                description = request.POST.get('description')
                initiation_date = request.POST.get('initiation-date')
                completion_date = request.POST.get('completion-date')
                erb_number = request.POST.get('erb')
                funding_source = request.POST.get('funding')

                # Validate and convert dates if provided
                if initiation_date:
                    if initiation_date == "":  # Handle empty or null values
                        initiation_date = None
                    else: 
                        try:
                            initiation_date = datetime.strptime(initiation_date, '%Y-%m-%d').date()
                        except ValueError:
                            raise ValidationError(f"{initiation_date} is not a valid date. Expected format: YYYY-MM-DD.")
                else:
                    initiation_date = None

                if completion_date:
                    if completion_date == "":  # Handle empty or null values
                        completion_date = None
                    else: 
                        try:
                            completion_date = datetime.strptime(completion_date, '%Y-%m-%d').date()
                        except ValueError:
                            raise ValidationError(f"{completion_date} is not a valid date. Expected format: YYYY-MM-DD.")
                else:
                    completion_date = None

                # Create a new Research_Project instance
                new_project = Research_Project.objects.create(
                    title=title,
                    principal_investigator=principal_investigator,
                    description=description,
                    anticipated_initiation_date=initiation_date,
                    anticipated_completion_date=completion_date,
                    erb_number=erb_number,
                    funding_source=funding_source
                )

                # Associate the new project with the request sample
                request_sample.research_project = new_project  # Set the ForeignKey to the new project

            erb_approval = request.FILES.get('erb_approval')  # New file if uploaded
            type_selected = request.POST.get('typeValue')
            sex = request.POST.get('sex')
            age = request.POST.get('age')
            age_from = request.POST.get('age_from')
            age_to = request.POST.get('age_to')
            clinical_diagnosis = request.POST.get('clinical_diagnosis')
            other_diagnosis = request.POST.get("other_diagnosis")
            amount = request.POST.get('amount')
            unit = request.POST.get('unit')
            desired_start_date = request.POST.get('desired_start_date')

            if clinical_diagnosis == "Others":
                clinical_diagnosis = other_diagnosis

            # Convert the desired_start_date to a date format if it's provided
            if desired_start_date:
                if desired_start_date == "":  # Handle empty or null values
                    desired_start_date = None
                else: 
                    try:
                        desired_start_date = datetime.strptime(desired_start_date, '%Y-%m-%d').date()
                    except ValueError:
                        raise ValidationError(f"{desired_start_date} is not a valid date. Expected format: YYYY-MM-DD.")
            else:
                desired_start_date = None

            # If these are empty strings, convert them to None instead of trying to convert empty strings to integers
            age = None if age == '' else (int(age) if age is not None else None)
            age_from = None if age_from == '' else (int(age_from) if age_from is not None else None)
            age_to = None if age_to == '' else (int(age_to) if age_to is not None else None)

            # Update the Request Sample instance fields
            if erb_approval:
                request_sample.erb_approval = erb_approval  # Only update if a new file is uploaded

            request_sample.type = type_selected
            request_sample.sex = sex
            request_sample.age = age
            request_sample.age_from = age_from
            request_sample.age_to = age_to
            request_sample.clinical_diagnosis = clinical_diagnosis
            request_sample.amount = amount
            request_sample.unit = unit
            request_sample.desired_start_date = desired_start_date
            
            request_sample.save()

            # Handle comorbidities
            new_comorbidities = request.POST.get('comorbidities') 
            RS_Comorbidities.objects.filter(request_sample=request_sample).delete()

            # Add new comorbidities to the request_sample if provided
            if new_comorbidities:
                for comorbidity in new_comorbidities.split(','):
                    comorbidity = comorbidity.strip()  # Remove any extra spaces
                    if comorbidity:  # Check if it's not empty
                        RS_Comorbidities.objects.create(
                            request_sample=request_sample,
                            comorbidity=comorbidity
                        )   

            # Handle lab tests
            new_lab_tests = request.POST.get('lab_tests')
            RS_Lab_Test.objects.filter(request_sample=request_sample).delete()

            if new_lab_tests:
                for lab_test in new_lab_tests.split(','):
                    lab_test = lab_test.strip()  # Remove any extra spaces
                    if lab_test:  # Ensure it's not empty
                        RS_Lab_Test.objects.create(
                            request_sample=request_sample,
                            labtest=lab_test
                        )

            # Handle Step4 data
            multiple_samples = request.POST.get('multiple_samples')
            time_points1 = request.POST.get('time_points1')
            interval = request.POST.get('interval')
            interval_unit = request.POST.get('interval_unit')
            start_date_ddmmyyyy = request.POST.get('start_date_ddmmyyyy')
            start_date_mmyyyy = request.POST.get('start_date_mmyyyy')
            start_date_yyyy = request.POST.get('start_date_yyyy')

            # Validate and parse start_date_ddmmyyyy
            if start_date_ddmmyyyy:
                if start_date_ddmmyyyy == "":  # Handle empty or null values
                    start_date_ddmmyyyy = None
                else: 
                    try:
                        start_date_ddmmyyyy = datetime.strptime(start_date_ddmmyyyy, '%Y-%m-%d').date()
                    except ValueError:
                        raise ValidationError(f"{start_date_ddmmyyyy} is not a valid date. Expected format: YYYY-MM-DD.")
            else:
                start_date_ddmmyyyy = None

            # Convert fields to None if empty
            time_points1 = int(time_points1) if time_points1 else None
            interval = int(interval) if interval else None
            start_date_yyyy = int(start_date_yyyy) if start_date_yyyy else None

            # Update or create RS_Step4 instance
            rs_step4, created = RS_Step4.objects.update_or_create(
                request_sample=request_sample,
                defaults={
                    'multiple_samples': multiple_samples,
                    'time_points1': time_points1,
                    'interval': interval,
                    'interval_unit': interval_unit,
                    'start_date_ddmmyyyy': start_date_ddmmyyyy,
                    'start_date_mmyyyy': start_date_mmyyyy,
                    'start_date_yyyy': start_date_yyyy,
                }
            )

            # Collect Step5 data
            different_sources = request.POST.get('different_sources')
            num_participants = request.POST.get('num_participants')
            multiple_timepoints_each = request.POST.get('multiple_timepoints_each')
            time_points2 = request.POST.get('time_points2')
            interval = request.POST.get('interval')
            interval_unit = request.POST.get('interval_unit')
            start_date_ddmmyyyy = request.POST.get('start_date_ddmmyyyy')
            start_date_mmyyyy = request.POST.get('start_date_mmyyyy')
            start_date_yyyy = request.POST.get('start_date_yyyy')
            collection_date_ddmmyyyy = request.POST.get('collection_date_ddmmyyyy')
            collection_date_mmyyyy = request.POST.get('collection_date_mmyyyy')
            collection_date_yyyy = request.POST.get('collection_date_yyyy')

            # Validate and parse the start_date_ddmmyyyy
            if start_date_ddmmyyyy:
                if start_date_ddmmyyyy == "":  # Handle empty or null values
                    start_date_ddmmyyyy = None
                else: 
                    try:
                        start_date_ddmmyyyy = datetime.strptime(start_date_ddmmyyyy, '%Y-%m-%d').date()
                    except ValueError:
                        raise ValidationError(f"{start_date_ddmmyyyy} is not a valid date. Expected format: YYYY-MM-DD.")
            else:
                start_date_ddmmyyyy = None

            # Validate and parse the collection_date_ddmmyyyy
            if collection_date_ddmmyyyy:
                if collection_date_ddmmyyyy == "":  # Handle empty or null values
                    collection_date_ddmmyyyy = None
                else: 
                    try:
                        collection_date_ddmmyyyy = datetime.strptime(collection_date_ddmmyyyy, '%Y-%m-%d').date()
                    except ValueError:
                        raise ValidationError(f"{collection_date_ddmmyyyy} is not a valid date. Expected format: YYYY-MM-DD.")
            else:
                collection_date_ddmmyyyy = None

            # Convert empty strings to None
            num_participants = int(num_participants) if num_participants else None
            time_points2 = int(time_points2) if time_points2 else None
            interval = int(interval) if interval else None
            start_date_yyyy = int(start_date_yyyy) if start_date_yyyy else None
            collection_date_yyyy = int(collection_date_yyyy) if collection_date_yyyy else None

            # Handle the time_points2 field based on multiple_timepoints_each
            if multiple_timepoints_each == 'no':
                time_points2 = None  # Set time_points2 to None if "No" for multiple time points

            # Update or create RS_Step5 instance
            rs_step5, created = RS_Step5.objects.update_or_create(
                request_sample=request_sample,  # Match the request_sample
                defaults={
                    'different_sources': different_sources,
                    'num_participants': num_participants,
                    'multiple_timepoints_each': multiple_timepoints_each,
                    'time_points2': time_points2,
                    'interval': interval,
                    'interval_unit': interval_unit,
                    'start_date_ddmmyyyy': start_date_ddmmyyyy,
                    'start_date_mmyyyy': start_date_mmyyyy,
                    'start_date_yyyy': start_date_yyyy,
                    'collection_date_ddmmyyyy': collection_date_ddmmyyyy,
                    'collection_date_mmyyyy': collection_date_mmyyyy,
                    'collection_date_yyyy': collection_date_yyyy,
                }
            )   

            messages.success(request, f"Sample request edited successfully.")
            return redirect('edit_request_sample_step7', sample_id=request_sample.id)
        except Exception as e:
            messages.error(request, f"Error editing sample request: {e}")
            
            # Log the full traceback for further inspection
            import traceback
            print(traceback.format_exc())  # Or use logging
            return redirect('')

    # Render the form for editing with existing project data
    return render(request, 'edit_request_sample.html', {
        'request_sample': request_sample,
        'research_projects': research_projects,
        'existing_comorbidities': existing_comorbidities_list,
        'existing_lab_tests': existing_lab_tests_list,
        'rs_step4': rs_step4,
        'rs_step5': rs_step5,
        'projects_context': projects_context,
    })

def edit_request_sample_step7(request, sample_id):
    # Fetch the request sample from the database using the sample_id
    request_sample = get_object_or_404(Request_Sample, id=sample_id)
    research_project = request_sample.research_project  # Access the single related project
    comorbidities = RS_Comorbidities.objects.filter(request_sample=request_sample)
    lab_tests = RS_Lab_Test.objects.filter(request_sample=request_sample)
    step4_data = RS_Step4.objects.filter(request_sample=request_sample).first()
    step5_data = RS_Step5.objects.filter(request_sample=request_sample).first()

    # Calculate the total number of sample requests using the helper function
    total_samples = calculate_total_samples(step4_data, step5_data)

    # Prepare context with all the fetched data
    context = {
        'request_sample': request_sample,
        'research_project': research_project,  # Pass the single related project
        'comorbidities': comorbidities,
        'lab_tests': lab_tests,
        'step4': step4_data,
        'step5': step5_data,
        'total_samples': total_samples  # Add this line
    }
    
    return render(request, 'edit_request_sample_step7.html', context)

def view_request_sample_details(request, sample_id):
# Fetch the request sample from the database using the sample_id
    request_sample = get_object_or_404(Request_Sample, id=sample_id)
    research_project = request_sample.research_project
    comorbidities = RS_Comorbidities.objects.filter(request_sample=request_sample)
    lab_tests = RS_Lab_Test.objects.filter(request_sample=request_sample)
    step4_data = RS_Step4.objects.filter(request_sample=request_sample).first()
    step5_data = RS_Step5.objects.filter(request_sample=request_sample).first()

    # Calculate the total number of sample requests using the helper function
    total_number_of_samples = calculate_total_samples(step4_data, step5_data)

    # Prepare context with all the fetched data
    context = {
        'request_sample': request_sample,
        'research_project': research_project,
        'comorbidities': comorbidities,
        'lab_tests': lab_tests,
        'step4': step4_data,
        'step5': step5_data,
        'total_number_of_samples': total_number_of_samples,
    }
    
    return render(request, 'view_request_sample_details.html', context)


def my_requests(request):
    user = request.user

    if not user.is_authenticated:
        return redirect('login')

    # Fetch all the samples requested by the user
    sample_requests = (
        Request_Sample.objects.filter(requested_by=user)
        .select_related('research_project')  # Include related research project for efficiency
    )

    # Fetch all approval records associated with the user's samples
    approval_records = (
        Approve_Reject_Request.objects.filter(request_sample__in=sample_requests)
        .select_related('request_sample', 'create_ack_receipt')  # Optimize related object access
    )

    # Create a mapping for quick lookup of approval records
    approval_mapping = {
        record.request_sample.id: record for record in approval_records
    }

    # Annotate each sample request with its approval record and acknowledgment receipt
    for sample in sample_requests:
        sample.approval_record = approval_mapping.get(sample.id)  # Attach approval record
        if sample.approval_record and sample.approval_record.create_ack_receipt:
            sample.ack_receipt = sample.approval_record.create_ack_receipt
        else:
            sample.ack_receipt = None  # Ensure no invalid reference

    # Render the template with the annotated sample_requests
    return render(request, 'my_requests.html', {'sample_requests': sample_requests})
    

def view_request_sample(request):

    # Fetch all research projects with their related request sample data
    # projects = Research_Project.objects.select_related('request_sample__requested_by').all()
    sample_requests = Request_Sample.objects.select_related('research_project').prefetch_related('approve_reject_request_set').all()
    return render(request, 'view_request_sample.html', {'sample_requests': sample_requests})

@transaction.atomic
def view_details(request, id):
    request_sample = get_object_or_404(Request_Sample, id=id)
    research_project = request_sample.research_project
    comorbidities = RS_Comorbidities.objects.filter(request_sample=request_sample)
    lab_tests = RS_Lab_Test.objects.filter(request_sample=request_sample)
    step4 = RS_Step4.objects.filter(request_sample=request_sample).first()
    step5 = RS_Step5.objects.filter(request_sample=request_sample).first()
    approval_record = Approve_Reject_Request.objects.filter(request_sample=request_sample).first()

    # Calculate the total number of sample requests using the helper function
    total_number_of_samples = calculate_total_samples(step4, step5)
    if request.method == 'POST':
        approval = request.POST.get('approval')
        attach_file = request.FILES.get('attach_file')
        reject_reason = request.POST.get('reject_reason')

        # Create a new acknowledgment receipt only if a file is uploaded
        receipt = None
        if attach_file:
            receipt = Create_Ack_Receipt.objects.create(
                officer_signature=None,  # Or provide a default value if needed
                pdf_file=attach_file
            )

        no_sample = request.POST.get('no_sample')
        approval_record.approve_reject = approval
        approval_record.reject_reason = reject_reason
        approval_record.attach_file = attach_file
        approval_record.no_available_samples = no_sample

        # Default reject reason if no samples are available
        if approval_record.no_available_samples == 'No':
            approval_record.reject_reason = "No available sample/s for now."

        # Associate the new acknowledgment receipt if approved
        if approval == 'approve' and receipt:
            approval_record.create_ack_receipt = receipt

        approval_record.save()

        # Logic to handle the approval or rejection
        if approval == 'approve':
            request_sample.status = 'approved'
        elif approval == 'reject':
            request_sample.status = 'rejected'

        # Update the 'updated_at' field to reflect the approval/rejection time
        request_sample.updated_at = timezone.now()
        request_sample.save()

        # Redirect to a confirmation page or the same page
        return redirect('view_request_sample')

    context = {
        'research_project': research_project,
        'request_sample': request_sample,
        'comorbidities': comorbidities,
        'lab_tests': lab_tests,
        'step4': step4,
        'step5': step5,
        'approval_record': approval_record,
        'total_number_of_samples': total_number_of_samples,
    }
    return render(request, 'view_details.html', context)

@transaction.atomic

def update_view_details(request, id):
    request_sample = get_object_or_404(Request_Sample, id=id)
    research_project = request_sample.research_project
    comorbidities = RS_Comorbidities.objects.filter(request_sample=request_sample)
    lab_tests = RS_Lab_Test.objects.filter(request_sample=request_sample)
    step4 = RS_Step4.objects.filter(request_sample=request_sample).first()
    step5 = RS_Step5.objects.filter(request_sample=request_sample).first()
    approval_record = Approve_Reject_Request.objects.filter(request_sample=request_sample).first()

    # Calculate the total number of sample requests using the helper function
    total_number_of_samples = calculate_total_samples(step4, step5)

    if request.method == 'POST':
        attach_file = request.FILES.get('attach_file')

        if attach_file and isinstance(attach_file, InMemoryUploadedFile):
            # Process the file directly in memory without saving
            file_content = attach_file.read()  # Read the file content
            print(f"Uploaded file content: {file_content[:100]}...")  # Example: Print first 100 bytes

            # Update the acknowledgment receipt if it exists
            if approval_record.create_ack_receipt:
                receipt = approval_record.create_ack_receipt  # Directly access the related object
                receipt.pdf_file = attach_file  # Update the file field with the uploaded file
                receipt.save()
            else:
                # Optionally create a new acknowledgment receipt if it doesn't exist
                receipt = Create_Ack_Receipt.objects.create(pdf_file=attach_file)
                approval_record.create_ack_receipt = receipt

        # Update the approval record with the uploaded file (in memory)
        if attach_file:
            approval_record.attach_file = attach_file
        approval_record.save()

        # Update the 'updated_at' field for the request sample
        request_sample.updated_at = timezone.now()
        request_sample.save()

        # Redirect to the confirmation or listing page
        return redirect('view_request_sample')

    context = {
        'research_project': research_project,
        'request_sample': request_sample,
        'comorbidities': comorbidities,
        'lab_tests': lab_tests,
        'step4': step4,
        'step5': step5,
        'approval_record': approval_record,
        'total_number_of_samples': total_number_of_samples,
    }
    return render(request, 'update_view_details.html', context)

@transaction.atomic
def create_ack_receipt(request, id):
    request_sample = get_object_or_404(Request_Sample, id=id)
    research_project = request_sample.research_project
    researcher = request_sample.requested_by

    # Retrieve the existing Approve_Reject_Request
    try:
        approval_record = Approve_Reject_Request.objects.get(request_sample=request_sample)
    except Approve_Reject_Request.DoesNotExist:
        return HttpResponse("No associated approval record exists.", status=400)

    # Prevent creating duplicate acknowledgment receipts
    if approval_record.create_ack_receipt:
        return HttpResponse("Acknowledgment receipt already exists for this request sample.", status=400)

    user_id = request.session.get("user_id")
    biobank_manager = UserProfile.objects.get(id=user_id) if user_id else None

    step4 = RS_Step4.objects.filter(request_sample=request_sample).first()
    step5 = RS_Step5.objects.filter(request_sample=request_sample).first()
    total_samples = calculate_total_samples(step4, step5)

    request_comorbidities = RS_Comorbidities.objects.filter(request_sample=request_sample).values_list('comorbidity', flat=True)
    request_lab_tests = RS_Lab_Test.objects.filter(request_sample=request_sample).values_list('labtest', flat=True)

    # Assuming `request_sample.age`, `request_sample.age_from`, and `request_sample.age_to` are being passed
    matching_samples = Samples.objects.filter(
        type=request_sample.type,
        # sex=request_sample.sex,
        clinical_diagnosis=request_sample.clinical_diagnosis,
    )

    # Apply the comorbidity filter only if request_comorbidities is not empty
    if request_comorbidities:
        matching_samples = matching_samples.filter(
            Q(comorbidities__comorbidity__in=request_comorbidities) |
            Q(comorbidities__comorbidity__isnull=True)  # This allows samples with no comorbidities
        )
    else:
        matching_samples = matching_samples.filter(
            comorbidities__comorbidity__isnull=True  # Only samples with no comorbidity
        )

    # Apply the lab test filter
    if request_lab_tests:
        matching_samples = matching_samples.filter(
            lab_test__labtest__in=request_lab_tests
        )

    matching_samples = matching_samples.distinct()

    if request_sample.age is not None: 
        matching_samples = matching_samples.filter(age=request_sample.age)
    elif request_sample.age_from is not None and request_sample.age_to is not None:
        matching_samples = matching_samples.filter(age__gte=request_sample.age_from, age__lte=request_sample.age_to)
    else:
        matching_samples = matching_samples.exclude(age__isnull=True)

    if request.method == 'POST':
        officer_signature = request.FILES.get('signature-file')

        # Start a transaction for atomicity
        with transaction.atomic():
            # Create the main acknowledgment receipt record
            ack_receipt = Create_Ack_Receipt(officer_signature=officer_signature)
            ack_receipt.save()

            # Loop through each sample entry and save it in the Ack_Sample model
            for i in range(1, total_samples + 1):
                sample_id = request.POST.get(f'sample_id_{i}')
                sample_type = request.POST.get(f'sample_type_{i}')
                quantity_volume = request.POST.get(f'quantity_volume_{i}')
                container_location = request.POST.get(f'container_location_{i}')

                # Only save the Ack_Sample if a sample ID was selected
                if sample_id:
                    ack_sample = Ack_Sample(
                        create_ack_receipt=ack_receipt,
                        sample_id=sample_id,
                        sample_type=sample_type,
                        quantity_volume=quantity_volume,
                        container_location=container_location
                    )
                    ack_sample.save()

            # Generate the PDF with improved layout
            buffer = BytesIO()
            pdf = canvas.Canvas(buffer, pagesize=letter)

            # Header
            pdf.setFont("Helvetica-Bold", 14)
            pdf.drawString(200, 750, "Acknowledgment Receipt")

            # Request Information
            pdf.setFont("Helvetica", 12)
            pdf.drawString(50, 720, f"Request ID: {id}")
            pdf.drawString(50, 700, f"Researcher Name: {researcher.first_name} {researcher.last_name}")
            pdf.drawString(50, 680, f"Unit: {researcher.unit}")
            pdf.drawString(50, 660, f"Position: {researcher.position}")
            pdf.drawString(50, 640, f"Research Project: {research_project.title}")

            # Sample Table
            sample_data = [["Sample ID", "Sample Type", "Quality Volume", "Container Location"]]
            for sample in Ack_Sample.objects.filter(create_ack_receipt=ack_receipt):
                sample_data.append([sample.sample_id, sample.sample_type, sample.quantity_volume, sample.container_location])

            table = Table(sample_data, colWidths=[100, 150, 120, 150])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))

            table.wrapOn(pdf, 50, 580)
            table.drawOn(pdf, 50, 500)

            # Issuing Officer Information
            pdf.drawString(50, 460, f"Issuing Officer Name: {biobank_manager.first_name} {biobank_manager.last_name}")
            pdf.drawString(50, 440, f"Position: {biobank_manager.position}")

            # Signature
            if ack_receipt.officer_signature:
                pdf.drawString(50, 420, "Signature:")
                signature_path = ack_receipt.officer_signature.path  # Path to the signature image
                pdf.drawImage(signature_path, 120, 380, width=100, height=50)  # Adjust position and size

            pdf.save()

            # Save PDF to the database
            buffer.seek(0)
            ack_receipt.pdf_file.save(f'ack_receipt_{ack_receipt.id}.pdf', ContentFile(buffer.read()))
            buffer.close()

            # Link the acknowledgment receipt to the approval record
            approval_record.create_ack_receipt = ack_receipt
            approval_record.approve_reject = 'approve'
            approval_record.save()

            # Update the status of the associated Request_Sample to 'approved'
            request_sample.status = 'approved'
            request_sample.updated_at = timezone.now()
            request_sample.save()

            # Return the PDF URL in JSON response
            pdf_url = ack_receipt.pdf_file.url
            return JsonResponse({'pdf_url': pdf_url, 'redirect_url': reverse('view_request_sample')})

            # Redirect to a success page or back to the list view
            # return redirect('view_request_sample')

    context = {
        'project': research_project,
        'request_sample': request_sample,
        'sample_range': range(1, total_samples + 1),  # Dynamic row count based on matching samples
        'researcher': researcher,
        'biobank_manager': biobank_manager,
        'matching_samples': matching_samples,
    }
    return render(request, 'create_ack_receipt.html', context)

def download_ack_receipt(request, ack_id):
    try:
        ack_receipt = Create_Ack_Receipt.objects.get(id=ack_id)
        
        if ack_receipt.pdf_file:
            # If the PDF file exists, return it as an attachment
            return FileResponse(ack_receipt.pdf_file.open('rb'), as_attachment=True, filename=f"ack_receipt_{ack_id}.pdf")
        else:
            # If no PDF is found, show a message and redirect back to the same page
            messages.add_message(request, messages.ERROR, "Acknowledgment Receipt PDF not found.")
            return redirect(request.META.get('HTTP_REFERER'))  # Redirect to the previous page
    except Create_Ack_Receipt.DoesNotExist:
        # If the acknowledgment receipt is not found, show a message and redirect back
        messages.add_message(request, messages.ERROR, "Acknowledgment Receipt not found.")
        return redirect(request.META.get('HTTP_REFERER'))  # Redirect to the previous page
    
@transaction.atomic
def sample_detail(request, sample_id):
    sample = get_object_or_404(Samples.objects.prefetch_related('comorbidities_set', 'lab_test_set', 'aliquot_set', 'storage_set'), id=sample_id)
    print(f"Sample fetched: {sample.id}")

    ack_samples = Ack_Sample.objects.filter(sample_id=sample_id)

    request_samples = []

    for ack_sample in ack_samples:
        print(f"Ack_Sample ID: {ack_sample.id}")

        # Get the related Create_Ack_Receipt
        ack_receipt = ack_sample.create_ack_receipt
        if not ack_receipt:
            print(f"No associated Create_Ack_Receipt found for Ack_Sample ID: {ack_sample.id}")
            continue 

        print(f"Create Ack Receipt: {ack_receipt.id}")

        # Get the related Approve_Reject_Request
        approval_record = Approve_Reject_Request.objects.filter(create_ack_receipt=ack_receipt).first()
        if not approval_record:
            print(f"No associated Approve_Reject_Request found for Create_Ack_Receipt ID: {ack_receipt.id}")
            continue  

        print(f"Approval Record: {approval_record.id}")

        # Get the associated Request_Sample
        request_sample = approval_record.request_sample
        if not request_sample:
            print(f"No associated Request_Sample found for Approve_Reject_Request ID: {approval_record.id}")
            continue 

        print(f"Request Sample: {request_sample.id}")

        if request_sample not in request_samples:
            request_samples.append(request_sample)

    print("All Associated Request_Samples:")
    for request_sample in request_samples:
        print(f"Request_Sample ID: {request_sample.id}")

     # Get all related storage details
    first_storage_info = sample.storage_set.first()

    # Get total number of aliquots for the sample
    total_aliquots = sample.aliquot_set.count()

    # Get individual aliquots and their associated storage
    aliquots = sample.aliquot_set.prefetch_related('storage_set').all()

    return render(request, 'sample_detail.html', {
        'sample': sample,
        'ack_samples': ack_samples,
        'request_samples': request_samples, 
        'first_storage_info': first_storage_info,
        'total_aliquots': total_aliquots,
        'aliquots': aliquots,
    })


# Utility function to generate pie charts
def generate_pie_chart(labels, values, title, max_label_length=15):
    # Handle empty or invalid inputs
    if not labels or not values:
        print(f"Skipping pie chart generation for '{title}': No data provided.")
        return None

    if sum(values) == 0:
        print(f"Skipping pie chart generation for '{title}': Values sum to zero.")
        return None

    try:
        # Filter out entries with 0 values
        filtered_data = [(label, value) for label, value in zip(labels, values) if value > 0]
        if not filtered_data:
            print(f"Skipping pie chart generation for '{title}': No non-zero data.")
            return None
        
        filtered_labels, filtered_values = zip(*filtered_data)

        # Wrap labels to a fixed length
        wrapped_labels = [textwrap.fill(label, max_label_length) for label in filtered_labels]

        # Create a fixed-size figure
        fig, ax = plt.subplots(figsize=(8, 8))
        
        # Generate the pie chart
        wedges, texts, autotexts = ax.pie(
            filtered_values,
            labels=wrapped_labels,  # Use wrapped labels
            autopct='%1.1f%%',
            startangle=90,
            textprops={'fontsize': 14},  # Increased font size for better readability
            normalize=True  # Ensure data normalization
        )
        
        # Set consistent font sizes for labels and percentages
        for text in texts:
            text.set_fontsize(14)
        for autotext in autotexts:
            autotext.set_fontsize(12)  # Larger percentage text size
        
        # Remove extra spacing by ensuring explode is 0
        explode = [0 for _ in filtered_values]

        # Set equal aspect ratio
        ax.set_aspect('equal', adjustable='box')
        
        # Add title with larger font size
        plt.title(title, fontsize=18, pad=20)
        
        # Save the plot to a Base64 string
        with BytesIO() as buffer:
            plt.savefig(buffer, format="png", bbox_inches="tight")
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # Clear the plot to free memory
        plt.close(fig)
        
        return f"data:image/png;base64,{image_base64}"
    except Exception as e:
        print(f"Error generating pie chart for '{title}': {e}")
        return None


# Inventory Status View
def inventory_status(request):
    # Fetch all samples
    samples = Samples.objects.prefetch_related('comorbidities_set', 'lab_test_set', 'aliquot_set', 'storage_set')

    # Fetch all research projects
    research_projects = Research_Project.objects.all()

    # Prepare the data for each research project
    projects = []

    for project in research_projects:
        print(f"Project: {project.title}")
        
        # Get all Request_Sample objects linked to this research project
        request_samples = Request_Sample.objects.filter(research_project=project)

        # Collect all sample IDs associated with the research project
        sample_ids = set()  # Use a set to avoid duplicates

        for request_sample in request_samples:
            print(f"Request Sample: {request_sample.id}")

            # Get related Approve_Reject_Request objects
            approval_records = Approve_Reject_Request.objects.filter(request_sample=request_sample)
            for approval_record in approval_records:
                print(f"Approval Record: {approval_record.id}")

                # Get the related Create_Ack_Receipt
                ack_receipt = approval_record.create_ack_receipt
                if not ack_receipt:
                    print(f"No Create_Ack_Receipt found for Approval Request {approval_record.id}")
                    continue

                print(f"Create Ack Receipt: {ack_receipt.id}")

                # Get related Ack_Sample objects
                ack_samples = Ack_Sample.objects.filter(create_ack_receipt=ack_receipt)
                for ack_sample in ack_samples:
                    print(f"Ack Sample: {ack_sample.id}, Sample ID: {ack_sample.sample_id}")
                    if ack_sample.sample_id:  # Ensure sample_id is not None
                        sample_ids.add(ack_sample.sample_id)

        # Append project with its sample data
        projects.append({"name": project.title, "count": len(sample_ids), "sample_ids": list(sample_ids)})

    # Group samples by type
    types_dict = defaultdict(list)
    for sample in samples:
        types_dict[sample.type].append(sample.id)

    # Convert the grouped data to a list of dictionaries
    grouped_samples = [
        {"type": sample_type, "count": len(ids), "ids": ids}
        for sample_type, ids in types_dict.items()
    ]

    # Generate pie charts
    project_labels = [project["name"] for project in projects]
    project_values = [project["count"] for project in projects]
    project_chart = generate_pie_chart(project_labels, project_values, "Samples by Research Project")
    if project_chart is None:
        print("No project chart generated.")

    type_labels = [sample_type["type"] for sample_type in grouped_samples]
    type_values = [sample_type["count"] for sample_type in grouped_samples]
    type_chart = generate_pie_chart(type_labels, type_values, "Samples by Type")
    if type_chart is None:
        print("No type chart generated.")

    # Prepare context for the template
    context = {
        "samples": samples,
        "projects": projects,
        "types": grouped_samples,
        "project_chart": project_chart,
        "type_chart": type_chart,
    }

    return render(request, "inventory_status.html", context)

def generate_pdf(request):
    samples = Samples.objects.prefetch_related('comorbidities_set', 'lab_test_set', 'aliquot_set', 'storage_set')

    # Fetch research projects and their associated samples
    research_projects = Research_Project.objects.prefetch_related(
        'request_samples__sample'  # Prefetch samples through request_samples
    ).all()

    # Prepare the project data
    projects = []
    for project in research_projects:
        # Get all sample IDs linked to the project
        sample_ids = [
            sample.id
            for request_sample in project.request_samples.all()
            for sample in request_sample.sample.all()
        ]
        projects.append({"name": project.title, "count": len(sample_ids), "sample_ids": sample_ids})

    # Group samples by type
    types_dict = defaultdict(list)
    for sample in samples:
        types_dict[sample.type].append(sample.id)

    # Convert the grouped data to a list of dictionaries
    types = [
        {"type": sample_type, "count": len(ids), "ids": ids}
        for sample_type, ids in types_dict.items()
    ]

    # Generate pie charts
    project_labels = [project["name"] for project in projects]
    project_values = [project["count"] for project in projects]
    # project_chart = generate_pie_chart(project_labels, project_values, "Samples by Research Project")

    type_labels = [sample_type["type"] for sample_type in types]
    type_values = [sample_type["count"] for sample_type in types]
    # type_chart = generate_pie_chart(type_labels, type_values, "Samples by Type")

    project_chart = generate_pie_chart(project_labels, project_values, "Samples by Research Project")
    if project_chart is None:
        print("No project chart generated.")

    type_chart = generate_pie_chart(type_labels, type_values, "Samples by Type")
    if type_chart is None:
        print("No type chart generated.")


    local_timezone = pytz.timezone('Asia/Manila')  

    context = {
        "samples": samples,
        "projects": projects,
        "types": types,
        "project_chart": project_chart,
        "type_chart": type_chart,
        "generation_date" : datetime.now(local_timezone).strftime('%B %d, %Y %I:%M:%S %p')
    }

    template_path = "inventory_status_pdf.html"
    response = HttpResponse(content_type="application/pdf")

    current_date = datetime.now(local_timezone).strftime("%Y-%m-%d")
    response["Content-Disposition"] = f'attachment; filename="BIMS-{current_date}.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("Error generating PDF")
    return response