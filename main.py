from fastapi import FastAPI, HTTPException #FastAPI
from pydantic import BaseModel #Allow us to create classes for Therapist/Patients
from enum import Enum


#------------------------------------------------------------------#
#CRUD mindset
#When we create data we want to be able to:
#1. Create
#2. Read
#3. Update
#4. Delete
#------------------------------------------------------------------#

#Temporary in-memory db
#This is here for primarily testing logic
therapists_db = {} #Keys: id, values: name
patients_db = {} #Keys: id, values: name

#------------------------------------------------------------------#
#Big Idea We want Data Stored in a Database (PostgreSQL)
#Endpoints of Therapist and Patients
#Therapists:
# - name : str
# - id : int
# - Assign a therapist to a patient : list[dict[str, int]] | None 
# - Pull all patients for a given therapist when we retrieve them : str | None

#Patients:
# - Patients Name : str
# - id : int
# - Pull the therapist assigned to the patients : str | None
# - Description of the possible patient? : str | None
# - age? : int
#------------------------------------------------------------------#
#Step 1: What Are Therapists and Patients?
class Therapists(BaseModel):
    name: str
    therapist_id: int
    patients: list[dict[str, int]] | None = None

class Patients(BaseModel):
    name: str
    patient_id: int
    descriptions: str | None = None
    age: int
    therapists: list[dict[str, int]] | None = None
#------------------------------------------------------------------#
app = FastAPI()

# Step 2:
# Simple Creating New Therapist & Patients
@app.post("/therapists/")
async def create_therapist(therapist: Therapists):
    if therapist.therapist_id not in therapists_db:
        therapists_db[therapist.therapist_id] = therapist
    return therapists_db

@app.post("/patients/")
async def create_patient(patient: Patients):
    patients_db[patient.patient_id] = patient
    return patients_db
#------------------------------------------------------------------#
#Step 3:
# Assigning Therapist to Patients
@app.post("/therapists/{therapist_id}/assign/{patient_id}")
async def assign_patient(therapist_id: int, patient_id: int): #the parameters to look up the therapist

    if therapist_id not in therapists_db: #Therapist does't exist
        raise HTTPException(status_code=404, detail=f"Therapist with the id: {therapist_id} doesn't exist")
    
    if patient_id not in patients_db: #therapist does exist in our system
        raise HTTPException(status_code=404, detail=f"Patient with the id: {patient_id} doesn't exist")
    
    #getting the names from the temp db if the user does exist -> returns dict of their info based on their id
    patient_temp = patients_db[patient_id]
    therapist_temp = therapists_db[therapist_id]
    print(f"Debug: Patient_temp:{patient_temp}")
    print(f"Debug: Therapist_temp:{therapist_temp}")


    # checking first to see if their assigned to anyone
    # if they have no patients/therapists then we assign them an empty list
    if therapist_temp.patients is None: therapist_temp.patients = []
    if patient_temp.therapists is None: patient_temp.therapists = []
    
    # grabbing the info from the specific patient/therapist
    patient_info = {"id": patient_id, "name": patient_temp.name}
    therapist_info = {"id": therapist_id, "name": therapist_temp.name}
    
    # adding it to the temp db
    therapist_temp.patients.append(patient_info)
    patient_temp.therapists.append(therapist_info)
    print("Checking Cross Check with Patient:", patient_temp.therapists)

    return therapist_temp
