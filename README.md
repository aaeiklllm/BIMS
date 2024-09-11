# Innovative Healthcare

Patient prescription creation and storing medical history using Postgresql, Django and Bootstrap
Github: https://github.com/Its-Puja-Singh/HackathonBackend

## Prerequisites
* Install Python3 and Django and PostgreSQL
* Any Editor (Preferably VS Code or Sublime Text)
* Any web browser with latest version

## Languages and Technologies used
* HTML5/CSS3
* JavaScript (to create dynamically updating content)
* Bootstrap (An HTML, CSS, and JS library)
* PostgreSQL (An RDBMS that uses SQL)
* Python and Django

## Installation

To get started with DjangoEHR, follow these installation steps:

1. Clone the repository to your local machine:

    ```bash
    git clone https://github.com/yourusername/djangoehr.git
    ```

2. Create a virtual environment and activate it:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. Install project dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Configure your database settings in the `settings.py` file.

5. Apply database migrations:

    ```bash
    python manage.py migrate
    ```

6. Create a superuser account:

    ```bash
    python manage.py createsuperuser
    ```

7. Start the development server:

    ```bash
    python manage.py runserver
    ```

## Steps to run the project in your machine
* Clone or download the repository.
* Create a database named hackfest in postgresql.
* Make migrations using the following command:
    * `python manage.py makemigrations`
    * `python manage.py migrate`


* The accounts_role table is being used as master table so enter data in the same using:

```
INSERT INTO public.accounts_role (role)
VALUES
    ('BiobankManager'),
    ('Researcher'),
    ('Admin');
```
* Then run `python manage.py createsuperuser` to create an admin or superuser.
And then inside the accounts_userrolemap insert data for the admin you created:
```
INSERT INTO public.accounts_userrolemap  (user_id_id,role_id_id)
VALUES
    (1,3);
```
6. Run `python manage.py runserver` to run the server on localhost.


```
class Medicine(models.Model):
    name 
    form    
    category 
    strength     
    concentration 
    unitOfPreparation 
    manufacturer 
    expiryDate 
    amount 
    role 
    description 
```
```

class Diagnosis(models.Model):
    diagnosisName 
    diagnosisBodySite     
    dateOfOnset 
    severity 
    dateOfAbatement 
    diagnosisCertainity
    diagnosisDescription  
    createdDate  
```
```

class MedicalDevice(models.Model):
    deviceName 
    deviceBodySite 
    deviceUse 
    deviceDscription 
```
```

class LaboratoryTest(models.Model):
    testName 
    testSpecimen 
    testBodySite 
    testUse 
    testDescription 
```
```

class LabTestPrescriptionMap(models.Model):
    laboratoryTestId     
    prescriptionId 

```
```
class Prescription(models.Model):
    patientId 
    diagnosisId 
    medicalDevice 

```
```
class MedicineDirection(models.Model):
    medicineId 
    doseUnit
    duration     
    doseTiming 
    additionalInstruction 
    reason 
```
```
class MedicineDirPrescriptionMap(models.Model):
    prescriptionId     
    medicineDirectionId
```
