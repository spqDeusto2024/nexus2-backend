import app.models.models as models
import app.models.resident as resident
import app.models.family as family
import app.models.room as room
import app.models.shelter as shelter
import app.mysql.models as mysql_models
import app.mysql.family as familyMysql
import app.mysql.room as roomMysql
import app.mysql.shelter as shelterMysql
import app.mysql.resident as residentMysql
from app.mysql.mysql import DatabaseClient
from app.mysql.resident import Resident
from app.mysql.room import Room
from app.mysql.shelter import Shelter

from datetime import date
import app.utils.vars as gb
from sqlalchemy.orm import Session
from sqlalchemy import func



class Controllers:
  def __init__(self) -> None:
    pass
  
  def healthz(self):
    """
    Checks server status
    """
    return {"status": "ok"}
  
  def create_user(self, body: models.UserRequest):
    """
    Creates new user in  the database
    """
    body_row = mysql_models.User(name=body.name, fullname=body.fullname, age=body.age)
    
    db = DatabaseClient(gb.MYSQL_URL)
    with Session(db.engine) as session:
      session.add(body_row)
      session.commit()
      session.close()
  
    return {"status": "ok"}

  
  def create_resident(self, body: resident.Resident, session=None):
  
    """
    Creates a new resident entry in the database.

    Parameters:
            - `name` (str): First name of the resident.
            - `surname` (str): Last name of the resident.
            - `birthDate` (datetime.date): The resident's date of birth.
            - `gender` (str): Gender of the resident (e.g., "M" for male, "F" for female).
            - `createdBy` (int): ID of the admin or user creating the entry.
            - `idFamily` (Optional[int]): Foreign key linking to the family, if applicable.
            - `idRoom` (int): Foreign key linking to the resident's assigned room.

    Returns:
        dict:
            A dictionary indicating the success of the operation:
            - `{"status": "ok"}` if the resident was successfully created.

    Process:
        1. Convert the `Resident` object into a database-compatible format.
        2. Use the provided session or create a new session.
        3. Add the resident to the database.
        4. Commit the transaction to save the changes.
        5. Return a success status.

    """
    
    if session is None:
        db = DatabaseClient(gb.MYSQL_URL)
        session = Session(db.engine)

    body_row = residentMysql.Resident(
        name=body.name,
        surname=body.surname,
        birthDate=body.birthDate,
        gender=body.gender,
        createdBy=body.createdBy,
        createDate=date.today(),
        idFamily=body.idFamily,
        idRoom=body.idRoom,
    )

    session.add(body_row)
    session.commit()
    return {"status": "ok"}

  
  def delete_resident(self, idResident: int, session=None):
  
    """
    Deletes a resident entry from the database.

    Parameters:
        idResident (int): 
            The unique identifier of the resident to delete.

    Returns:
        dict:
            A dictionary indicating the outcome of the operation:
            - `{"status": "ok"}`: The resident was successfully deleted.
            - `{"status": "not found"}`: No resident was found with the given ID.

    Process:
        1. Check if an existing database session is provided; if not, create a new session.
        2. Query the database for a resident record matching the provided `idResident`.
        3. If the resident exists:
            a. Delete the resident record.
            b. Commit the transaction to save changes.
            c. Return a success status.
        4. If the resident does not exist, return a "not found" status.
    """

    if session is None:
        db = DatabaseClient(gb.MYSQL_URL)
        session = Session(db.engine)

    resident_to_delete = session.query(Resident).filter_by(idResident=idResident).first()
    if resident_to_delete:
        session.delete(resident_to_delete)
        session.commit()
        return {"status": "ok"}
    else:
        return {"status": "not found"}

  def update_resident(self, idResident: int, updates: dict, session=None):

    """
    Updates an existing resident's details in the database.

    Parameters:
        idResident (int): The unique identifier of the resident to update.
        updates (dict): A dictionary containing the fields to update and their new values.
            Example:
                {
                    "name": "Jane",
                    "surname": "Smith",
                    "idRoom": 102,
                    "update": date(2024, 11, 14)
                }

    Returns:
        dict: A status dictionary indicating the result of the update.
            - `{"status": "ok"}` if the update was successful.
            - `{"status": "not found"}` if no resident with the given ID was found.
    """
    if session is None:
        db = DatabaseClient(gb.MYSQL_URL)
        session = Session(db.engine)

    try:
        resident_to_update = session.query(Resident).filter_by(idResident=idResident).first()

        if not resident_to_update:
            return {"status": "not found"}

        for field, value in updates.items():
            if hasattr(resident_to_update, field):
                setattr(resident_to_update, field, value)

        session.commit()
        
        return {"status": "ok"}
    except Exception as e:
        session.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        if session is None:
            session.close()
  
  
  def list_rooms_with_resident_count(self, session=None):
  
    """
    Retrieves a list of all rooms along with the number of residents in each room.

    Parameters:
        session (Session, optional): 
            An active SQLAlchemy database session. If not provided, the method 
            initializes a new database session using the `DatabaseClient`.

    Returns:
        list[dict]: 
            A list of dictionaries, where each dictionary represents a room 
            and contains the following keys:
            - `idRoom` (int): The unique identifier of the room.
            - `roomName` (str): The name of the room.
            - `maxPeople` (int): The maximum capacity of the room.
            - `resident_count` (int): The number of residents currently assigned to the room.

    Process:
        1. If no session is provided, a new session is created using the `DatabaseClient`.
        2. Perform an `outerjoin` between the `Room` and `Resident` tables on the `idRoom` field.
        3. Use SQL aggregation to calculate the number of residents in each room.
        4. Group the results by `Room.idRoom` to ensure one result per room.
        5. Transform the query results into a list of dictionaries, including:
            - Room details (`idRoom`, `roomName`, `maxPeople`).
            - The calculated resident count (`resident_count`).

    """

    if session is None:
        db = DatabaseClient(gb.MYSQL_URL)
        session = Session(db.engine)

    result = (
        session.query(Room, func.count(Resident.idResident).label("resident_count"))
        .outerjoin(Resident, Room.idRoom == Resident.idRoom)
        .group_by(Room.idRoom)
        .all()
    )

    return [
        {
            "idRoom": room.idRoom,
            "roomName": room.roomName,
            "maxPeople": room.maxPeople,
            "resident_count": resident_count,
        }
        for room, resident_count in result
    ]


  def get_shelter_energy_level(self, session=None):

    """
    Retrieves the energy level of the shelter. This method fetches the energy level of the shelter from the database.
    It assumes there is only one shelter entry in the database.

    Parameters:
        session (Session, optional): 
            An active SQLAlchemy database session. 
            If not provided, the method initializes a new session using the default database connection.

    Returns:
        dict: 
            A dictionary containing the energy level of the shelter in the following format:
            ```
            {
                "energyLevel": <int>  # Energy level as an integer (e.g., 75).
            }
            ```

    Process:
        1. If no active database session is provided, initialize a new session.
        2. Query the database to retrieve the first (and only) shelter entry.
        3. If a shelter is found:
            - Extract its energy level.
            - Return the energy level in a dictionary.
        4. If no shelter is found:
            - Raise a `ValueError` indicating the absence of shelter data.
            
    """
    if session is None:
        db = DatabaseClient(gb.MYSQL_URL)
        session = Session(db.engine)

    shelter = session.query(Shelter).first()

    if shelter is None:
        raise ValueError("No shelter found in the database.")

    return {"energyLevel": shelter.energyLevel}


  def get_all(self):
    """
    Gets all users
    """
    db = DatabaseClient(gb.MYSQL_URL)
    response: list = []
    with Session(db.engine) as session:
      response = session.query(mysql_models.User).all()
      session.close()
      
    return response
  
  def delete_user(self, id: int):
    """
    Deletes user by its UID
    """
    db = DatabaseClient(gb.MYSQL_URL)
    with Session(db.engine) as session:
      userToBeDeleted = session.query(mysql_models.User).get(id)
      session.delete(userToBeDeleted)
      session.commit()
      session.close()
      
    return {"status": "ok"}
  
  def update_user(self, body: models.UpdateRequest):
    """
    Updates user by its ID
    """
    db = DatabaseClient(gb.MYSQL_URL)
    with Session(db.engine) as session:
      user: mysql_models.User = session.query(mysql_models.User).get(body.id)
      user.name = body.update.name
      user.fullname = body.update.fullname
      user.age = body.update.age
      session.dirty
      session.commit()
      session.close()
      
    return {"status": "ok"}
  
