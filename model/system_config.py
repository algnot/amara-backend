from sqlalchemy import Column, Integer, VARCHAR
from model.base import Base


class SystemConfig(Base):
    __tablename__ = "system_config"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(VARCHAR(200), unique=True, nullable=False)
    value = Column(VARCHAR(200), nullable=False)
