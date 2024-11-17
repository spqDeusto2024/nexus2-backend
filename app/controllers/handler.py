import app.models.resident as resident
import app.models.family as family
import app.models.room as room
import app.models.shelter as shelter
import app.mysql.family as familyMysql
import app.mysql.room as roomMysql
import app.mysql.shelter as shelterMysql
import app.mysql.resident as residentMysql
import app.mysql.admin as adminMysql
from app.mysql.mysql import DatabaseClient
from app.mysql.resident import Resident
from app.mysql.room import Room
from app.mysql.shelter import Shelter
from app.mysql.family import Family
from app.mysql.admin import Admin

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
  

  def create_resident(self, body: resident.Resident, session=None):
   
    """
    Creates a new resident entry in the database and ensures that the assigned room has enough capacity
    to accommodate all family members. If the current room cannot accommodate the new resident, it checks
    for an available room in the shelter, and if none is available, a new room is created. Additionally,
    the method checks for the shelter's capacity, prevents duplication of residents in the same room, and
    assigns the correct room to the family.

    Steps:
        1. Verifies if the family exists in the database.
        2. Checks if the family has an assigned room.
        3. Ensures no duplication of residents with the same name, surname, and family in the same room.
        4. Verifies the shelter's capacity is not exceeded.
        5. Checks if the room has enough capacity for the new resident. If not, attempts to reassign the family
           to a different room or create a new room if necessary.
        6. Adds the new resident to the database and associates them with the correct room.

    Arguments:
        body (resident.Resident): The resident data to be added to the database. This includes information such as
                                   the resident's name, surname, birth date, gender, family ID, and room ID.
        session (Session, optional): The database session to use for the transaction. If not provided, a new session
                                     will be created.

    Returns:
        dict: A dictionary indicating the result of the operation.
              - If successful: {"status": "ok"}
              - If there is an error (e.g., family does not exist, no assigned room, shelter full, or resident already exists):
                {"status": "error", "message": "Error message explaining the issue."}
    """
    if session is None:
        db = DatabaseClient(gb.MYSQL_URL)
        session = Session(db.engine)

    family = session.query(familyMysql.Family).filter(familyMysql.Family.idFamily == body.idFamily).first()
    
    if not family:
        return {"status": "error", "message": "The family does not exist."}

    if not family.idRoom:
        return {"status": "error", "message": "The family does not have an assigned room."}

    existing_resident = session.query(residentMysql.Resident).filter(
        residentMysql.Resident.idFamily == body.idFamily,
        residentMysql.Resident.idRoom == family.idRoom,
        residentMysql.Resident.name == body.name,
        residentMysql.Resident.surname == body.surname
    ).first()

    if existing_resident:
        return {"status": "error", "message": "Cannot create resident, the resident already exists in this room."}

    shelter_capacity = session.query(Shelter).filter(Shelter.idShelter == family.idShelter).first()
    if shelter_capacity:
        current_residents_in_shelter = session.query(residentMysql.Resident).filter(residentMysql.Resident.idFamily == body.idFamily).count()
        if current_residents_in_shelter >= shelter_capacity.maxPeople:
            return {"status": "error", "message": "The shelter is full."}

    room = session.query(roomMysql.Room).filter(roomMysql.Room.idRoom == family.idRoom).first()

    if room:
        current_family_residents = session.query(residentMysql.Resident).filter(residentMysql.Resident.idFamily == body.idFamily, residentMysql.Resident.idRoom == family.idRoom).count()

        if current_family_residents + 1 > room.maxPeople:
            new_room = session.query(roomMysql.Room).filter(roomMysql.Room.maxPeople > current_family_residents, roomMysql.Room.idShelter == room.idShelter).first()
            
            if new_room:
                family.idRoom = new_room.idRoom
                session.query(familyMysql.Family).filter(familyMysql.Family.idFamily == body.idFamily).update({"idRoom": new_room.idRoom}, synchronize_session=False)
                session.commit()
                room = new_room
            else:
                new_room = roomMysql.Room(
                    roomName="New Room",  
                    idShelter=family.idShelter,
                    maxPeople=current_family_residents + 1
                )
                session.add(new_room)
                session.commit()
                family.idRoom = new_room.idRoom
                session.query(familyMysql.Family).filter(familyMysql.Family.idFamily == body.idFamily).update({"idRoom": new_room.idRoom}, synchronize_session=False)
                session.commit()
                room = new_room
    
    body_row = residentMysql.Resident(
        name=body.name,
        surname=body.surname,
        birthDate=body.birthDate,
        gender=body.gender,
        createdBy=body.createdBy,
        createDate=date.today(),
        idFamily=body.idFamily,
        idRoom=family.idRoom,
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
  
  def create_room(self, body: room.Room, session=None):

    """

    Creates a new room entry in the database and ensures that the room does not exist.

    Arguments:
        body (room.Room): The room data to be added to the database. This includes information such as
                                   the room's id, name, creation date, who created it, shelter id and max people in it.
        session (Session, optional): The database session to use for the transaction. If not provided, a new session
                                     will be created.

    Returns:
        dict: A dictionary indicating the result of the operation.
              - If successful: {"status": "ok"}
              - If there is an error (e.g., room already exists):
                {"status": "error", "message": "Error message explaining the issue."}
    

    """

    if session is None:
        db = DatabaseClient(gb.MYSQL_URL)
        session = Session(db.engine)
     
    admin = session.query(adminMysql.Admin).filter(adminMysql.Admin.idAdmin == body.createdBy).first()

    if not admin:
       return{"status": "error", "message": "The admin does not exist."}

    shelter = session.query(Shelter).filter(Shelter.idShelter == body.idShelter).first()

    if shelter is None:
       return{"status": "error", "message": "The Shelter does not exist."}

    existing_room = session.query(Room).filter(
       Room.roomName == body.roomName,
       Room.idShelter == body.idShelter
    ).first()

    if existing_room:
       return {"status": "error", "message": "Cannot create room, the room already exists."}
    
    body_row = roomMysql.Room(
       idRoom=body.idRoom,
       roomName=body.roomName,
       createdBy=body.createdBy,
       createDate=body.createDate,
       idShelter=body.idShelter,
       maxPeople=body.maxPeople
    )

    try:
        session.add(body_row)
        session.commit()
        return {"status": "ok"}
    except Exception as e:
        session.rollback()
        return {"status": "error", "message": str(e)}
    finally:
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


  def access_room(self, idResident: int, idRoom: int, session=None):

    """
    Determines whether a resident is allowed to access a specified room.

    Steps:
        1. If the room name does **not** start with "Room" (e.g., a public or common room), 
           the resident is granted access regardless of family association.
        2. If the room name **does** start with "Room" (e.g., a private or restricted room), 
           access is granted only if:
           - The resident is part of a family.
           - The room is assigned to the resident's family.
        3. Returns appropriate error messages if the resident or room does not exist.

    Parameters:
        idResident (int): 
            The unique identifier of the resident attempting to access the room.
        idRoom (int): 
            The unique identifier of the room the resident is trying to access.
        session (Session, optional): 
            An active SQLAlchemy database session. If not provided, the method will 
            create a new session using the application's database configuration.

    Returns:
        str: 
            A message indicating the outcome of the access attempt:
            - `"Access granted. Welcome to the room."`: Resident has permission to access the room.
            - `"Access denied. You are in the wrong room."`: Resident does not have permission.
            - `"Resident not found."`: The specified resident does not exist in the database.
            - `"Room not found."`: The specified room does not exist in the database.
    """

    if session is None:
        db = DatabaseClient(gb.MYSQL_URL)
        session = Session(db.engine)

    resident = session.query(Resident).filter_by(idResident=idResident).first()
    room = session.query(Room).filter_by(idRoom=idRoom).first()

    if resident is None:
        return "Resident not found."

    if room is None:
        return "Room not found."

    if not room.roomName.startswith("Room"):
        return "Access granted. Welcome to the room."

    family = session.query(Family).filter_by(idRoom=room.idRoom).first()
    if family and resident.idFamily == family.idFamily:
        return "Access granted. Welcome to the room."
    else:
        return "Access denied. You are in the wrong room."

  def list_residents_in_room(self, idRoom, session=None):
    
    """
    Retrieves a list of all residents assigned to a specific room.

    Parameters:
        idRoom (int): 
            The unique identifier of the room for which residents should be listed.
        session (Session, optional): 
            An active SQLAlchemy database session. If not provided, the method 
            initializes a new database session using the `DatabaseClient`.

    Returns:
        list[dict]: 
            A list of dictionaries, where each dictionary represents a resident 
            and contains the following keys:
            - `idResident` (int): The unique identifier of the resident.
            - `name` (str): The name of the resident.
            - `surname` (str): The surname of the resident.
            - `idFamily` (int): The family ID associated with the resident.
            - `idRoom` (int): The room ID where the resident is assigned.

    Process:
        1. If no session is provided, a new session is created using the `DatabaseClient`.
        2. Query the `Resident` table to retrieve all residents with the given `idRoom`.
        3. Transform the query results into a list of dictionaries with relevant resident details.
    """
    if session is None:
        db = DatabaseClient(gb.MYSQL_URL)
        session = Session(db.engine)

    residents = (
        session.query(Resident)
        .filter(Resident.idRoom == idRoom)
        .all()
    )

    return [
        {
            "idResident": resident.idResident,
            "name": resident.name,
            "surname": resident.surname,
            "idFamily": resident.idFamily,
            "idRoom": resident.idRoom,
        }
        for resident in residents
    ]

    
