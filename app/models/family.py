from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class Family(BaseModel):

    """
    Represents a family residing in the shelter, with information about 
    their assigned room and shelter.

    Attributes:
        idFamily (int): Unique identifier for the family.
        familyName (str): The name or identifier of the family.
        idRoom (int): Foreign key to the room assigned to the family.
        idShelter (int): Foreign key to the shelter where the family resides.
        createdBy (int): ID of the admin who created this family record.
        createDate (date): The date when the family record was created.
    """

    idFamily: int
    familyName: str
    idRoom: int
    idShelter: int
    createdBy: int
    createDate: date

