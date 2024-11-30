from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class Room(BaseModel):

    """
    Represents a room within a shelter, with information about capacity and creation.

    Attributes:
        idRoom (int): Unique identifier for the room.
        roomName (str): Name or identifier of the room.
        createdBy (int): ID of the admin who created this room record.
        createDate (date): The date when the room record was created.
        idShelter (int): Foreign key to the shelter where the room is located.
        maxPeople (int): Maximum number of people that can occupy the room.
    """
    
    idRoom: Optional[int]
    roomName: str
    createdBy: int
    createDate: date
    idShelter: int
    maxPeople: int