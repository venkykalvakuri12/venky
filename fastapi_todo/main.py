from fastapi import FastAPI, HTTPException, Request, status, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

app = FastAPI()

# --------------------
# DATABASE SETUP
# --------------------
DATABASE_URL = "sqlite:///./students.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class StudentModel(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    grade = Column(String, nullable=False)


Base.metadata.create_all(bind=engine)

# --------------------
# Pydantic MODELS
# --------------------
class Student(BaseModel):
    name: str
    age: int
    grade: str


class UpdateStudent(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    grade: Optional[str] = None


class StudentOut(Student):
    id: int

    class Config:
        orm_mode = True

# --------------------
# DEPENDENCY
# --------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --------------------
# EXCEPTION
# --------------------
class StudentNotFound(Exception):
    def __init__(self, student_id: int):
        self.student_id = student_id


@app.exception_handler(StudentNotFound)
def student_not_found_handler(request: Request, exc: StudentNotFound):
    return JSONResponse(
        status_code=404,
        content={"message": f"Student with ID {exc.student_id} not found."},
    )


# --------------------
# ROUTES
# --------------------

# POST - Add a new student
@app.post("/students", response_model=StudentOut, status_code=status.HTTP_201_CREATED)
def create_student(student: Student, db: Session = Depends(get_db)):
    new_student = StudentModel(**student.dict())
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student


# PATCH - Update student partially
@app.patch("/students/{student_id}", response_model=StudentOut)
def partial_update_student(student_id: int, student: UpdateStudent, db: Session = Depends(get_db)):
    student_db = db.query(StudentModel).filter(StudentModel.id == student_id).first()
    if not student_db:
        raise StudentNotFound(student_id)

    for key, value in student.dict(exclude_unset=True).items():
        setattr(student_db, key, value)

    db.commit()
    db.refresh(student_db)
    return student_db


# GET - Retrieve all students
@app.get("/students", response_model=List[StudentOut])
def get_all_students(db: Session = Depends(get_db)):
    return db.query(StudentModel).all()