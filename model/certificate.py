from sqlalchemy import Column, Integer, VARCHAR, ForeignKey, DATETIME, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from model.base import Base


class Certificate(Base):
    __tablename__ = "certificate"

    id = Column(Integer, primary_key=True, autoincrement=True)
    certificate_number = Column(VARCHAR(255), unique=True, nullable=False)
    start_date = Column(DATETIME, nullable=False)
    end_date = Column(DATETIME, nullable=False)
    batch = Column(VARCHAR(5), nullable=True)
    given_date = Column(DATETIME, nullable=True)

    course_id = Column(Integer, ForeignKey("course.id"), nullable=False)
    course = relationship("Course")

    student_id = Column(Integer, ForeignKey("student.id"), nullable=False)
    student = relationship("Student")
    archived = Column(Boolean, default=False)

    def generate_certificate_number(self):
        now = datetime.now()
        yy = now.strftime("%Y")
        mm = now.strftime("%m")

        find = Certificate().filter(filters=[("certificate_number", "ilike", f"{yy}{mm}%")])
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

        values["certificate_number"] = self.generate_certificate_number()
        return super().create(values)
