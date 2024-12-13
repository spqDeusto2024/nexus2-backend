from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.mysql.base import Base  



class Room(Base):

    """
    Represents a room entity in the system.

    This entity stores information about a room, including its name, 
    the shelter it belongs to, and its capacity. It also includes 
    metadata for creation and tracking purposes.

    Attributes:
        idRoom (int): Unique identifier for the room.
        roomName (str): The name of the room.
        createdBy (int): The ID of the admin or user who created the room entry.
        createDate (date): The date when the room entry was created.
        idShelter (int): Foreign key linking the room to a specific shelter.
        maxPeople (int): The maximum number of people the room can accommodate.
    """
    
    __tablename__ = "room"
    idRoom = Column(Integer, primary_key=True)
    roomName = Column(String (40), nullable=False)
    createdBy = Column(Integer)
    createDate = Column(Date)
    idShelter = Column(Integer, ForeignKey("shelter.idShelter"))
    maxPeople = Column(Integer)
