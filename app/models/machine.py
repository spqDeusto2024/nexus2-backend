from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
    
class Machine(BaseModel):

    """
    Represents a machine in the shelter, including its operational status and location.

    Attributes:
        idMachine (int): Unique identifier for the machine.
        machineName (str): Name or identifier of the machine.
        on (bool): Operational status of the machine (True if on, False if off).
        idRoom (int): Foreign key to the room where the machine is located.
        createdBy (int): ID of the admin who created this machine record.
        createDate (date): The date when the machine record was created.
        update (Optional[date]): The date when the machine record was last updated.
    """

    idMachine: int
    machineName: str
    on: bool
    idRoom: int
    createdBy: int
    createDate: date
    update: Optional[date]

