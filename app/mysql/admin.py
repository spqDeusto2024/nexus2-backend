from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.mysql.base import Base 

class Admin(Base):

    """
    Represents an Admin entity in the system.

    Attributes:
        idAdmin (int): The unique identifier for the Admin.
        email (str): The email of the Admin.
        name (str): The name of the Admin.
        password (str): The hashed password of the Admin.
    """
    __tablename__ = "admin"
    idAdmin = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)
    name = Column(String, nullable=False)
    password = Column(String, nullable=False)