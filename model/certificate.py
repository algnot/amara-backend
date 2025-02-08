from sqlalchemy import Column, Integer, VARCHAR, ForeignKey, DATETIME
from sqlalchemy.orm import relationship

from model.base import Base


class Certificate(Base):
    __tablename__ = "certificate"

    id = Column(Integer, primary_key=True, autoincrement=True)
    certificate_number = Column(VARCHAR(255), unique=True, nullable=False)
    start_date = Column(DATETIME, nullable=False)
    end_date = Column(DATETIME, nullable=False)
    batch = Column(VARCHAR(5))
    given_date = Column(DATETIME)

    course_id = Column(VARCHAR(200), ForeignKey("course.id"), nullable=False)
    course = relationship("Course")

    student_id = Column(Integer, ForeignKey("student.id"), nullable=False)
    student = relationship("Student")
