from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.mysql.base import Base  

class Resident(Base):

    """
    Represents a resident entity in the system.

    This entity stores information about a resident, including personal 
    details, family association, and metadata for auditing purposes.

    Attributes:
        idResident (int): Unique identifier for the resident.
        name (str): First name of the resident.
        surname (str): Last name of the resident.
        birthDate (date): The birthdate of the resident.
        gender (str): The gender of the resident.
        createdBy (int): The ID of the admin or user who created the resident entry.
        createDate (date): The date when the resident entry was created.
        update (date): The date when the resident entry was last updated.
        idFamily (int): Foreign key linking the resident to a specific family.
        idRoom (int): Foreign key linking the resident to a specific room.
    """

    __tablename__ = "resident"
    idResident = Column(Integer, primary_key=True)
    name = Column(String (40), nullable=False)
    surname = Column(String (100), nullable=False)
    birthDate = Column(Date)
    gender = Column(String (1))
    createdBy = Column(Integer)
    createDate = Column(Date)
    update = Column(Date)
    idFamily = Column(Integer, ForeignKey("family.idFamily"))
    idRoom = Column(Integer, ForeignKey("room.idRoom"))

