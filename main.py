"""
Imports: Fast API, HTTPException, Depends

- FastAPI: Allows us to create our Backend API
- HTTPEXception: This allows us to return errors if we encounter issues
- Depends: Allows our API queries to talk to the databse

"""
from fastapi import FastAPI, HTTPException, Depends 

"""
Imports: Pydantic

- This allow us to create classes that can have their uniqye
traits base on their goal
"""
from pydantic import BaseModel


"""
Imports: create_engine, Column, Integer, String, ForeignKey
- Creatine Engine: Allows us to talk with the PostgreSQL databse (establishing a connection)
- Column, Integer, String, ForeginKey: Creating the mapping tools within our database
"""
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker, declarative_base

#------------------------------------------------------------------------------------------------------#
# Step 1: Initialize/Create our Database
db_user: str = 'postgres'
db_port: int = 5432
db_host: str = 'localhost'
db_password: str = '052003'

uri: str = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/RESTORE-API'

engine = create_engine(uri)

"""
Bind: This connects to our database
autoFlush: This doesn't push changes, instead it waits for me to declare when
autocommit: Control when things get saved
"""
session_local = sessionmaker(autocommit = False, bind=engine, autoflush=True)

BASE = declarative_base()

# Connecting to our database
def get_db():
    db = session_local() # Open the door
    try:
        yield db # Let the endpoint do the work
    finally:
        db.close() # Close the door

#------------------------------------------------------------------------------------------------------#
#Step 2: Creating schemas within our database

class Therapist(BASE):
    __tablename__ = 'therapists'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

class Patients(BASE):
    __tablename__ = 'patients'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    age = Column(Integer)

    # Allows us to have that "relationship" with therapists and patients
    therapist_id = Column(Integer, ForeignKey("therapists.id"), nullable=True)

BASE.metadata.create_all(bind=engine) # This sends our schema to the database

#------------------------------------------------------------------------------------------------------#
#Step 3: Creating Classes for Fast API
class therapistSchema(BaseModel):
    name: str


class patientSchema(BaseModel):
    age: int
    name: str

#------------------------------------------------------------------------------------------------------#
# Step 4: Initilaize Our App
app = FastAPI()

#---------------#
#Step 5: POST a therapist/patients to the API
#C: Create <--
#R
#U: 
#D

# Create a Therapist
@app.post("/therapists/")
async def create_therapist(therapist: therapistSchema, db: Session = Depends(get_db)):
    new_therapist = Therapist(name=therapist.name)
    db.add(new_therapist) # Adds it to the database
    db.commit()
    db.refresh(new_therapist)
    return new_therapist

# Create a Patient
@app.post("/patients/")
async def create_patient(patient: patientSchema, db: Session = Depends(get_db)):
    new_patient = Patients(
        name = patient.name,
        age = patient.age
    )
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    return new_patient

#---------------#
#Step 5.1: Read the therapists/patients that we created
#C
#R: Read <--
#U: 
#D

@app.get("/therapists/{therapist_id}")
async def get_therapist_info(therapist_id: int, db: Session = Depends(get_db)):
    """
    Retrieves information for a specific therapist by their ID.
    """
    # Query the database for the therapist with the given ID
    therapist = db.query(Therapist).filter(Therapist.id == therapist_id).first()

    # Check if the therapist exists
    if therapist is None:
        # Return a 404 error if the therapist is not found
        raise HTTPException(status_code=404, detail="Therapist not found")

    # Return the therapist's information
    return therapist

@app.get("/patients/{patient_id}")
async def get_patient_info(patient_id: int, db: Session = Depends(get_db)):
    """
    Retrieve the information for the patient based on their ID
    """
    patient = db.query(Patients).filter(Patients.id == patient_id).first()

    # check if the patient even exists
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")

    db.refresh(patient)
    return patient

@app.get("/therapists/{therapist_id}/patients")
async def get_patients_assigned_to_therapist(therapist_id: int, db: Session = Depends(get_db)):
    """
    Retrieves all of the therapists for a given patient
    """
    therapist = db.query(Therapist).filter(Therapist.id == therapist_id).first()
    patients = db.query(Patients).filter(Patients.therapist_id == therapist_id).all()

    # check if the patient even exists
    if therapist is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    return {"patients": [{"id": p.id, "name": p.name, "age": p.age} for p in patients]}


#Step 5.2: Assing Therapist <-> Patients
#C
#R
#U: Update <--
#D


@app.post("/therapists/{therapist_id}/patients/{patient_id}")
async def assign_patient_to_therapist(therapist_id: int, patient_id: int, db: Session = Depends(get_db)):
    """
    Assingning a Therapist to a Patient
    """
    therapist = db.query(Therapist).filter(Therapist.id == therapist_id).first()
    patient = db.query(Patients).filter(Patients.id == patient_id).first()
    if(therapist is None or patient is None):
        raise HTTPException(status_code=404, detail="Insufficent Information")
    
    patient.therapist_id = therapist_id

    db.commit()
    db.refresh(patient)
    return {"message": f"Patient {patient.name} is now assigned to Therapist {therapist.name}"}

@app.patch("/therapist/{therapist_id}/{name}")
async def update_therapist_name(therapist_id: int, name: str, db: Session = Depends(get_db)):
    """
    Update the therapists name
    """
    therapist = db.query(Therapist).filter(Therapist.id == therapist_id).first()

    if therapist is None:
        raise HTTPException(status_code=404, detail="Therapist not found")

    therapist.name = name
    db.commit()
    db.refresh(therapist)
    return therapist

@app.patch("/patients/{patient_id}/{name}")
async def update_patient_name(patient_id: int, name: str, db: Session = Depends(get_db)):
    """
    Updating the patients name
    """
    patient = db.query(Patients).filter(Patients.id == patient_id).first()

    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    patient.name = name
    db.commit()
    db.refresh(patient)
    return patient

#Step 5.3: Delete Patients/Therapists
#C
#R
#U 
#D: Delete <--

@app.delete("/patients/{patient_id}/{therapist_id}")
async def delete_therapist_from_patient(patient_id: int, db: Session = Depends(get_db)):
    """
    Removing Therapists from Patients
    """

    patient = db.query(Patients).filter(Patients.id == patient_id).first()

    if patient is None:
        raise HTTPException(status_code=404, detail="Patient doesnt exists")
    
    patient.therapist_id = None
    db.commit()
    db.refresh(patient)
    return patient

@app.delete("/patients/{patient_id}")
async def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    """
    Remove Patients database
    """
    patient = db.query(Patients).filter(Patients.id == patient_id).first()
    
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient doesn't exist")
    
    db.delete(patient)
    db.commit()
    db.refresh(patient)
    return {"message": f"{patient.id},{patient.name} has been removed"}

@app.delete("/therapists/{therapist_id}")
async def delete_therapist(therapist_id: int, db: Session = Depends(get_db)):
    """
    Remove Therapist from database
    """
    therapist = db.query(Therapist).filter(Therapist.id == therapist_id).first()

    if therapist is None:
        raise HTTPException(status_code=404, detail="Therapist doesn't exist")
    
    db.delete(therapist)
    db.commit()
    db.refresh(therapist)
    return {"message": f"{therapist.id}, {therapist.name} has been removed"}