from sqlalchemy import Column, Integer, VARCHAR, TEXT
from model.base import Base


class Permission(Base):
    __tablename__ = "permission"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(VARCHAR(200), nullable=False)
    name = Column(VARCHAR(200), nullable=False)
    description = Column(TEXT, nullable=False)
