from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.mysql.base import Base  

class Shelter(Base):

    """
    Represents a shelter entity in the system.

    This entity stores information about a shelter, including its name, 
    address, contact information, and maximum capacity.

    Attributes:
        idShelter (int): Unique identifier for the shelter.
        shelterName (str): The name of the shelter.
        address (str): The address of the shelter.
        phone (str): Contact phone number for the shelter.
        email (str): Contact email for the shelter.
        maxPeople (int): The maximum number of people the shelter can accommodate.
        energyLevel (int): The energy leverl of the shelter. 
        waterLevel (int): The water level of the shelter. 
        radiationLevel (int): The radiation level of the shelter.
    """
    
    __tablename__ = "shelter"
    idShelter = Column(Integer, primary_key=True)
    shelterName = Column(String (40), nullable=False)
    address = Column(String (255))
    phone = Column(String (20))
    email = Column(String (40))
    maxPeople = Column(Integer)
    energyLevel = Column(Integer)
    waterLevel = Column(Integer)
    radiationLevel = Column(Integer)
