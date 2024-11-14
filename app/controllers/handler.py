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

from datetime import date
import app.utils.vars as gb
from sqlalchemy.orm import Session


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
  
