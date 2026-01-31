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
@app.post("/therapists/{therapist_id}/patients/{patient_id}")
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

#------------------------------------------------------------------#
#Step 4:
# Getting Info From the Patients

@app.get("/patients/{patient_id}")
async def get_patient_info(patient_id: int):
    
    #check if it even exists
    if patient_id not in patients_db:
        raise HTTPException(status_code=404, detail=f"Patient with the id: {patient_id} doesn't exist")

    return patients_db[patient_id]


# Getting Info From the Therapists
@app.get("/therapists/{therapist_id}")
async def get_therapist_info(therapist_id: int):
    
    #check if it even exists
    if therapist_id not in therapists_db:
        raise HTTPException(status_code=404, detail=f"Therapist with the id: {therapist_id} doesn't exist")

    return therapists_db[therapist_id]

@app.get("/patients/")
async def get_all_patients():
    if not patients_db: #checking the size of the list
        raise HTTPException(status_code=404, detail=f"Currently No Patients Exist")
    return patients_db

#------------------------------------------------------------------#
#Step 5: Pull all of the Patients from a therapist
@app.get("/therapists/{therapist_id}/patients")
async def get_therapist_patients(therapist_id: int):

    # making sure that the therapist exists
    if therapist_id not in therapists_db:
        raise HTTPException(status_code=404, detail=f"Therapist with the id: {therapist_id} doesn't exist")

    return therapists_db[therapist_id].patients

#------------------------------------------------------------------#
# Recap of where were at right now
# [x] We can create therapists
# [x] We can create patients
# [x] We can retireve information from the specific therapist/patient based on id
# [x] Pull Patients from a therapist

#------------------------------------------------------------------#
# Completed 1/31/2026 
# [x] Deleting a Therapist from a Patient

@app.delete("/therapists/{therapist_id}/patients/{patient_id}")
async def remove_patient_from_therapist(therapist_id: int, patient_id: int):

    # checking first if they exist
    if therapist_id not in therapists_db:
        raise HTTPException(status_code=404, detail=f"Therapist with the id: {therapist_id} doesn't exist")
    
    if patient_id not in patients_db:
        raise HTTPException(status_code=404, detail=f"Patient with the id: {patient_id} doesn't exist")
    
    # basic info
    therapist_info = therapists_db[therapist_id] #Only giving us a specific amount of info not all of it
    patient_info = patients_db[patient_id]

    # check if the therapist has 0 patients
    if not therapist_info.patients: #checking the size of the list
        raise HTTPException(status_code=404, detail=f"Therapist with the id: {therapist_id} doesn't have any patients")
    
    therapist_info.patients = [p for p in therapist_info.patients if p["id"] != patient_id]
    patient_info.therapists = [t for t in patient_info.therapists if t["id"] != therapist_id]

    return therapist_info

#------------------------------------------------------------------#
# What needs to be done:
# [x] Deleting a Patient from a Therapist


@app.delete("/patients/{patient_id}/therapists/{therapist_id}")
async def remove_therapist_from_patient(therapist_id: int, patient_id: int):

    # checking first if they exist
    if therapist_id not in therapists_db:
        raise HTTPException(status_code=404, detail=f"Therapist with the id: {therapist_id} doesn't exist")
    
    if patient_id not in patients_db:
        raise HTTPException(status_code=404, detail=f"Patient with the id: {patient_id} doesn't exist")
    
    # basic info
    therapist_info = therapists_db[therapist_id] #Only giving us a specific amount of info not all of it
    patient_info = patients_db[patient_id]

    # check if the patient has 0 therapists
    if not patient_info.therapists: #checking the size of the list
        raise HTTPException(status_code=404, detail=f"Patient with the id: {patient_id} doesn't have any therapists")
    
    therapist_info.patients = [p for p in therapist_info.patients if p["id"] != patient_id]
    patient_info.therapists = [t for t in patient_info.therapists if t["id"] != therapist_id]

    return patient_info

    
