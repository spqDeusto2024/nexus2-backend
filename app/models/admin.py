from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
    
class Admin(BaseModel):

    """
    Represents an admin within the shelter system, including credentials and contact information.

    Attributes:
        idAdmin (int): Unique identifier for the admin.
        email (str): Contact email of the admin.
        name (str): Name of the admin.
        password (str): Password for admin authentication.
    """
    
    idAdmin: int
    email: str
    name: str
    password: str
