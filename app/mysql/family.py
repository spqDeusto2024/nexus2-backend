from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.mysql.base import Base  

class Family(Base):

    """
    Represents a family entity in the system.

    This entity links a family to a specific room and shelter, 
    and tracks metadata about its creation.

    Attributes:
        idFamily (int): Unique identifier for the family.
        familyName (str): The name of the family.
        idRoom (int): Foreign key linking the family to a specific room.
        idShelter (int): Foreign key linking the family to a specific shelter.
        createdBy (int): The ID of the admin or user who created the family entry.
        createDate (date): The date when the family entry was created.
    """
    
    __tablename__ = "family"
    idFamily = Column(Integer, primary_key=True)
    familyName = Column(String (40), nullable=False)
    idRoom = Column(Integer, ForeignKey("room.idRoom"))
    idShelter = Column(Integer, ForeignKey("shelter.idShelter"))
    createdBy = Column(Integer)
    createDate = Column(Date)

