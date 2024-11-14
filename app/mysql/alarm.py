from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.mysql.base import Base  

class Alarm(Base):

    """
    Represents an alarm entity in the system.

    The alarm tracks events occurring within a room and associates them 
    with a resident and an admin. It includes a start and end time for 
    the event, as well as metadata for auditing.

    Attributes:
        idAlarm (int): Unique identifier for the alarm.
        start (datetime): Timestamp indicating when the alarm starts.
        end (datetime): Timestamp indicating when the alarm ends.
        idRoom (int): Foreign key linking the alarm to a specific room.
        idResident (int): Foreign key linking the alarm to a specific resident.
        idAdmin (int): Foreign key linking the alarm to the admin responsible.
        createDate (datetime): Timestamp indicating when the alarm was created.
    """
    
    __tablename__ = "alarm"
    idAlarm = Column(Integer, primary_key=True)
    start = Column(DateTime)
    end = Column(DateTime)
    idRoom = Column(Integer, ForeignKey("room.idRoom"))
    idResident = Column(Integer, ForeignKey("resident.idResident"))
    idAdmin = Column(Integer, ForeignKey("admin.idAdmin"))
    createDate = Column(DateTime)

