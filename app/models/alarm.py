from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class Alarm(BaseModel):

    """
    Represents an alarm event within the shelter system, logging the start and end times, 
    and associating the alarm with specific room, resident, and admin IDs.

    Attributes:
        idAlarm (int): Unique identifier for the alarm.
        start (datetime): The timestamp when the alarm started.
        end (datetime): The timestamp when the alarm ended.
        idRoom (int): Foreign key referring to the room associated with the alarm.
        idResident (int): Foreign key referring to the resident associated with the alarm.
        idAdmin (int): Foreign key referring to the admin responsible for the alarm.
        createDate (datetime): The timestamp when the alarm record was created.
    """
    
    idAlarm: int
    start: datetime
    end: datetime
    idRoom: int
    idResident: int
    idAdmin: int
    createDate: datetime