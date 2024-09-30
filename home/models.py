from django.db import models

class Samples(models.Model):
    type = models.CharField(max_length=150, null=True, blank=False )
    sex = models.CharField(max_length=1, null=True, blank=False)
    age = models.IntegerField(null=True, blank=True)
    clinical_diagnosis = models.CharField(max_length=150, null=True, blank=False )
    amount = models.FloatField(null=True, blank=True)
    unit = models.CharField(max_length=20, blank=True)
    date_collected = models.DateField(null=True, blank=False) 
    consent_form = models.FileField(blank=True, null=True)

class Comorbidities(models.Model):
    # Parent
    sample_id = models.ForeignKey(Samples, on_delete=models.CASCADE)

    comorbidity = models.CharField(max_length=150, blank=True)
class Lab_Test(models.Model):
    # Parent
    sample_id = models.ForeignKey(Samples, on_delete=models.CASCADE)

    labtest = models.CharField(max_length=150, blank=True)
class Aliquot(models.Model):
    # Parent
    sample_id = models.ForeignKey(Samples, on_delete=models.CASCADE)

    amount = models.FloatField(null=True, blank=True)
    unit = models.CharField(max_length=20, blank=True)
class Storage(models.Model):
    # Parents
    aliquot_id = models.ForeignKey(Aliquot, on_delete=models.CASCADE)
    sample_id = models.ForeignKey(Samples, on_delete=models.CASCADE)

    freezer_num = models.IntegerField(null=True, blank=True)
    shelf_num = models.IntegerField(null=True, blank=True)
    rack_num = models.IntegerField(null=True, blank=True)
    box_num = models.IntegerField(null=True, blank=True)
    container = models.CharField(max_length=20, blank=True)


