from sqlalchemy import Column, Integer, String
from database import Base  # import Base from your database.py

class StudentModel(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    grade = Column(String, nullable=False)
