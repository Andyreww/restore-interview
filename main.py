from fastapi import FastAPI, Depends
from sqlmodel import SQLModel, Field, create_engine, Session, select

app = FastAPI()

engine = create_engine("sqlite:///database.db")

class Therapist(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str

def create_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

@app.on_event("startup")
def on_startup():
    create_tables()

@app.post("/therapists/")
def create_therapist(name: str, session: Session = Depends(get_session)):
    therapist = Therapist(name=name)
    session.add(therapist)
    session.commit()
    session.refresh(therapist)
    return therapist
