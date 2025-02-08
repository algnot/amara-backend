from sqlalchemy import Column, Integer, VARCHAR
from model.base import Base


class SalePerson(Base):
    __tablename__ = "sale_person"
    __encrypted_field__ = ["firstname", "lastname"]

    id = Column(Integer, primary_key=True, autoincrement=True)
    firstname = Column(VARCHAR(200), nullable=False)
    lastname = Column(VARCHAR(200), nullable=False)
    reference_code = Column(VARCHAR(200), nullable=False)
