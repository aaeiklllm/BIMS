from django.db import models

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
class Request_Sample(models.Model):
    erb_approval = models.FileField(blank=True, null=True)
    type = models.CharField(max_length=300, null=True, blank=False)
    sex = models.CharField(max_length=100, null=True, blank=False)
    age = models.IntegerField(null=True, blank=True)
    clinical_diagnosis = models.CharField(max_length=300, null=True, blank=False)
    amount = models.IntegerField(null=True, blank=True)
    unit = models.CharField(max_length=100, null=True, blank=True)
    desired_start_date = models.DateField(null=True, blank=False) 

class Research_Project(models.Model):
    request_sample = models.ForeignKey(Request_Sample, on_delete=models.CASCADE)

    title = models.CharField(max_length=300, null=True, blank=False)
    principal_investigator = models.CharField(max_length=300, null=True, blank=False)
    description = models.CharField(max_length=300, null=True, blank=False)
    anticipated_initiation_date = models.DateField(null=True, blank=False) 
    anticipated_completion_date = models.DateField(null=True, blank=False) 
    erb_number = models.CharField(max_length=300, null=True, blank=False)
    funding_source = models.CharField(max_length=300, null=True, blank=False)

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

    multiple_samples = models.CharField(null=True, blank=False)
    time_points = models.IntegerField(null=True, blank=True)
    interval = models.IntegerField(null=True, blank=True)
    interval_unit = models.CharField(max_length=100, blank=True)
    start_date_ddmmyyyy = models.DateField(null=True, blank=False) 
    start_date_mmyyyy = models.CharField(max_length=7, blank=True, null=True)  # e.g., "2024-10"
    start_date_yyyy = models.IntegerField(blank=True, null=True)  # Store only the year as an integer

class RS_Step5(models.Model):
    # Parent
    request_sample = models.ForeignKey(Request_Sample, on_delete=models.CASCADE)

    different_sources = models.CharField(null=True, blank=False)
    num_participants = models.IntegerField(null=True, blank=True)
    multiple_timepoints_each = models.CharField(null=True, blank=False)
    time_points = models.IntegerField(null=True, blank=True)
    interval = models.IntegerField(null=True, blank=True)
    interval_unit = models.CharField(max_length=100, blank=True)
    start_date_ddmmyyyy = models.DateField(null=True, blank=False) 
    start_date_mmyyyy = models.CharField(max_length=7, blank=True, null=True)  # e.g., "2024-10"
    start_date_yyyy = models.IntegerField(blank=True, null=True)  # Store only the year as an integer
    collection_date_ddmmyyyy = models.DateField(null=True, blank=False) 
    collection_date_mmyyyy = models.CharField(max_length=7, blank=True, null=True)  # e.g., "2024-10"
    collection_date_yyyy = models.IntegerField(blank=True, null=True)  # Store only the year as an integer

class Approve_Reject_Request(models.Model):
    # Parent
    request_sample = models.ForeignKey(Request_Sample, on_delete=models.CASCADE)

    attach_file = models.FileField(blank=True, null=True)
    reject_reason = models.CharField(max_length=300, null=True, blank=False)
    no_available_samples = models.BooleanField(default=False, null=True, blank=False)

class Acknowledgement_Receipt(models.Model):
    # Parent
    approve = models.ForeignKey(Approve_Reject_Request, on_delete=models.CASCADE)

    name = models.CharField(max_length=300, null=True, blank=False)
    ack_unit = models.CharField(max_length=100, null=True, blank=False)
    ack_position = models.CharField(max_length=300, null=True, blank=False)
    ack_sample_id = models.IntegerField(null=True, blank=True)
    sample_type = models.CharField(max_length=300, null=True, blank=False)
    ack_quantity_volume = models.IntegerField(null=True, blank=True)
    officer_name = models.CharField(max_length=300, null=True, blank=False)
    officer_position = models.CharField(max_length=300, null=True, blank=False)
    officer_signature = models.FileField(blank=True, null=True)

class Acknowledgement_Storage(models.Model):
    # Parent
    acknowledgement_receipt = models.ForeignKey(Acknowledgement_Receipt, on_delete=models.CASCADE)

    ack_box_num = models.IntegerField(null=True, blank=True)
    ack_container_num = models.IntegerField(null=True, blank=True)

