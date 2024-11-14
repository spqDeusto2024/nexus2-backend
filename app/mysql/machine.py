from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.mysql.base import Base 

class Machine(Base):

    """
    Represents a machine entity in the system.

    This entity tracks details about a specific machine, its status, 
    and its association with a room. It also includes metadata for 
    creation and updates.

    Attributes:
        idMachine (int): Unique identifier for the machine.
        machineName (str): The name of the machine.
        on (bool): Indicates whether the machine is currently on (True) or off (False).
        idRoom (int): Foreign key linking the machine to a specific room.
        createdBy (int): The ID of the admin or user who created the machine entry.
        createDate (date): The date when the machine entry was created.
        update (date): The date when the machine entry was last updated.
    """
    
    __tablename__ = "machine"
    idMachine = Column(Integer, primary_key=True)
    machineName = Column(String, nullable=False)
    on = Column(Boolean)
    idRoom = Column(Integer, ForeignKey("room.idRoom"))
    createdBy = Column(Integer)
    createDate = Column(Date)
    update = Column(Date)

