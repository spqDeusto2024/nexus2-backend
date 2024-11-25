from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class Resident(BaseModel):

    """
    Represents a resident within the shelter system, including personal information 
    and family association.

    Attributes:
        idResident (int): Unique identifier for the resident.
        name (str): First name of the resident.
        surname (str): Surname of the resident.
        birthDate (date): Date of birth of the resident.
        gender (str): Gender of the resident.
        createdBy (int): ID of the admin who created this resident record.
        createDate (date): The date when the resident record was created.
        update (Optional[date]): The date when the resident record was last updated.
        idFamily (Optional[int]): Foreign key to the family the resident is associated with.
        idRoom: Foreign key to the room the resident is.
    """
    
    idResident: Optional[int]
    name: str
    surname: str
    birthDate: date
    gender: str
    createdBy: int
    createDate: date
    update: Optional[date]
    idFamily: Optional[int]
    idRoom: Optional[int]