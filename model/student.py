from sqlalchemy import Column, Integer, VARCHAR, ForeignKey
from sqlalchemy.orm import relationship
from model.base import Base
from datetime import datetime


class Student(Base):
    __tablename__ = "student"
    __encrypted_field__ = ["firstname_th", "lastname_th", "firstname_en", "lastname_en"]

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(VARCHAR(200), nullable=False)
    firstname_th = Column(VARCHAR(200), nullable=False)
    lastname_th = Column(VARCHAR(200), nullable=False)
    firstname_en = Column(VARCHAR(200), nullable=False)
    lastname_en = Column(VARCHAR(200), nullable=False)

    sale_person_id = Column(Integer, ForeignKey("sale_person.id"), nullable=False)
    sale_person = relationship("SalePerson")

    def generate_student_id(self):
        now = datetime.now()
        yy = now.strftime("%y")
        mm = now.strftime("%m")

        find = Student().filter(filters=[("student_id", "ilike", f"{yy}{mm}%")])
        if isinstance(find, list):
            count = len(find)
        elif find:
            count = 1
        else:
            count = 0

        return f"{yy}{mm}{count+1:05d}"

    def create(self, values=None):
        if values is None:
            values = {}

        values["student_id"] = self.generate_student_id()
        return super().create(values)
