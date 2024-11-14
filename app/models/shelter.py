from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class Shelter(BaseModel):

    """
    Represents a shelter with capacity and contact information.

    Attributes:
        idShelter (int): Unique identifier for the shelter.
        shelterName (str): Name of the shelter.
        address (str): Physical address of the shelter.
        phone (Optional[str]): Contact phone number for the shelter.
        email (Optional[str]): Contact email address for the shelter.
        maxPeople (int): Maximum number of people the shelter can accommodate.
        energyLevel (int): Energy level of the shelter.
        waterLevel (int): Water level of the shelter.
        radiationLevel (int): Water level of the shelter.
    """

    idShelter: int
    shelterName: str
    address: str
    phone: Optional[str]
    email: Optional[str]
    maxPeople: int
    energyLevel: int
    waterLevel: int
    radiationLevel: int