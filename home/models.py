from django.db import models
from accounts.models import UserProfile  # Import the UserProfile model

# Biobank Manager -------------------------------------------------------------------------
class Samples(models.Model):
    type = models.CharField(max_length=300, null=True, blank=False )
    sex = models.CharField(max_length=100, null=True, blank=False)
    age = models.IntegerField(null=True, blank=True)
    clinical_diagnosis = models.CharField(max_length=300, null=True, blank=False )
    amount = models.FloatField(null=True, blank=True)
    unit = models.CharField(max_length=300, blank=True)
    date_collected = models.DateField(null=True, blank=False) 
    consent_form = models.FileField(blank=True, null=True)
    last_modified = models.DateTimeField(auto_now=True)

class Comorbidities(models.Model):
    # Parent
    sample_id = models.ForeignKey(Samples, on_delete=models.CASCADE)

    comorbidity = models.CharField(max_length=300, blank=True)
class Lab_Test(models.Model):
    # Parent
    sample_id = models.ForeignKey(Samples, on_delete=models.CASCADE)

    labtest = models.CharField(max_length=300, blank=True)
class Aliquot(models.Model):
    # Parent
    sample_id = models.ForeignKey(Samples, on_delete=models.CASCADE)

    amount = models.FloatField(null=True, blank=True)
    unit = models.CharField(max_length=100, blank=True)
class Storage(models.Model):
    # Parents
    aliquot_id = models.ForeignKey(Aliquot, on_delete=models.CASCADE, null=True, blank=True)
    sample_id = models.ForeignKey(Samples, on_delete=models.CASCADE)

    freezer_num = models.CharField(max_length=300, blank=True, null=True)
    shelf_num = models.IntegerField(null=True, blank=True)
    rack_num = models.IntegerField(null=True, blank=True)
    box_num = models.IntegerField(null=True, blank=True)
    container = models.CharField(max_length=100, blank=True)


# Researcher ----------------------------------------------------------------------------------
class Research_Project(models.Model):
    title = models.CharField(max_length=300, null=True, blank=False)
    principal_investigator = models.CharField(max_length=300, null=True, blank=False)
    description = models.CharField(max_length=300, null=True, blank=False)
    anticipated_initiation_date = models.DateField(null=True, blank=False) 
    anticipated_completion_date = models.DateField(null=True, blank=False) 
    erb_number = models.CharField(max_length=300, null=True, blank=False)
    funding_source = models.CharField(max_length=300, null=True, blank=False)
    
class Request_Sample(models.Model):
    #Parent
    sample = models.ManyToManyField(Samples, related_name="request_of_sample", blank=True)
    research_project = models.ForeignKey(Research_Project, on_delete=models.CASCADE, related_name='request_samples', null=True, blank=True)

    erb_approval = models.FileField(blank=True, null=True)
    type = models.CharField(max_length=300, null=True, blank=False)
    sex = models.CharField(max_length=100, null=True, blank=False)
    age = models.IntegerField(null=True, blank=True)
    age_from = models.IntegerField(null=True, blank=True)
    age_to = models.IntegerField(null=True, blank=True)
    clinical_diagnosis = models.CharField(max_length=300, null=True, blank=False)
    amount = models.FloatField(null=True, blank=True)
    unit = models.CharField(max_length=100, null=True, blank=True)
    desired_start_date = models.DateField(null=True, blank=False) 
    requested_by = models.ForeignKey(UserProfile, on_delete=models.CASCADE)  # Add the requested_by field
    created_at = models.DateTimeField(auto_now_add=True)  # Captures request date automatically
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')
    updated_at = models.DateTimeField(auto_now=True)  # Automatically updates on modification

class RS_Comorbidities(models.Model):
    # Parent
    request_sample = models.ForeignKey(Request_Sample, on_delete=models.CASCADE)

    comorbidity = models.CharField(max_length=300, blank=True)

class RS_Lab_Test(models.Model):
    # Parent
    request_sample = models.ForeignKey(Request_Sample, on_delete=models.CASCADE)

    labtest = models.CharField(max_length=300, blank=True)

class RS_Step4(models.Model):
    # Parent
    request_sample = models.ForeignKey(Request_Sample, on_delete=models.CASCADE)

    multiple_samples = models.CharField(max_length=255, null=True, blank=False)
    time_points1 = models.IntegerField(null=True, blank=True)
    interval = models.IntegerField(null=True, blank=True)
    interval_unit = models.CharField(max_length=100, blank=True)
    start_date_ddmmyyyy = models.DateField(null=True, blank=False) 
    start_date_mmyyyy = models.CharField(max_length=7, blank=True, null=True)  # e.g., "2024-10"
    start_date_yyyy = models.IntegerField(blank=True, null=True)  # Store only the year as an integer

class RS_Step5(models.Model):
    # Parent
    request_sample = models.ForeignKey(Request_Sample, on_delete=models.CASCADE)

    different_sources = models.CharField(max_length=255, null=True, blank=False)
    num_participants = models.IntegerField(null=True, blank=True)
    multiple_timepoints_each = models.CharField(max_length=255, null=True, blank=False)
    time_points2 = models.IntegerField(null=True, blank=True)
    interval = models.IntegerField(null=True, blank=True)
    interval_unit = models.CharField(max_length=100, blank=True)
    start_date_ddmmyyyy = models.DateField(null=True, blank=False) 
    start_date_mmyyyy = models.CharField(max_length=7, blank=True, null=True)  # e.g., "2024-10"
    start_date_yyyy = models.IntegerField(blank=True, null=True)  # Store only the year as an integer
    collection_date_ddmmyyyy = models.DateField(null=True, blank=False) 
    collection_date_mmyyyy = models.CharField(max_length=7, blank=True, null=True)  # e.g., "2024-10"
    collection_date_yyyy = models.IntegerField(blank=True, null=True)  # Store only the year as an integer

class Create_Ack_Receipt(models.Model):
    officer_signature = models.FileField(blank=True, null=True)
    pdf_file = models.FileField(upload_to='ack_receipts/', blank=True, null=True)

class Approve_Reject_Request(models.Model):
    # Parent
    request_sample = models.ForeignKey(Request_Sample, on_delete=models.CASCADE, null=True, blank=True)
    create_ack_receipt = models.ForeignKey(Create_Ack_Receipt, on_delete=models.CASCADE, null=True, blank=True)

    approve_reject = models.CharField(max_length=100, null=True, blank=False)
    attach_file = models.FileField(blank=True, null=True)
    reject_reason = models.CharField(max_length=300, null=True, blank=False)
    no_available_samples = models.CharField(max_length=100, null=True, blank=False)

class Ack_Sample(models.Model):
    # Parent
    create_ack_receipt = models.ForeignKey(Create_Ack_Receipt, on_delete=models.CASCADE, null=True, blank=True)

    sample_id = models.IntegerField(null=True, blank=True)
    sample_type = models.CharField(max_length=100, null=True, blank=False)
    quantity_volume = models.CharField(max_length=100, null=True, blank=False)
    container_location = models.CharField(max_length=100, null=True, blank=False)
