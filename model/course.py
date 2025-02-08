from sqlalchemy import Column, Integer, VARCHAR
from model.base import Base


class Course(Base):
    __tablename__ = "course"

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_code = Column(VARCHAR(200), nullable=False)
    name_th = Column(VARCHAR(200), nullable=False)
    name_en = Column(VARCHAR(200), nullable=False)
