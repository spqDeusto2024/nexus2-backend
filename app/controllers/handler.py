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

  def create_resident(self, body: resident.Resident):

      """
    Creates a new resident entry in the database.

    Purpose:
        This method is responsible for creating a new resident record 
        in the database using the provided resident details.

    Parameters:
        body (resident.Resident): 
            An instance of the `Resident` model containing the resident's details:
            - `name` (str): First name of the resident.
            - `surname` (str): Last name of the resident.
            - `birthDate` (datetime.date): Date of birth of the resident.
            - `gender` (str): Gender of the resident (e.g., "M" for male, "F" for female).
            - `createdBy` (int): ID of the user or admin who is creating this entry.
            - `idFamily` (int, optional): Foreign key linking the resident to a specific family.
            - `idRoom` (int): Foreign key linking the resident to a specific room.

    Process:
        1. A `Resident` instance is transformed into a database-compatible object.
        2. The `DatabaseClient` establishes a connection to the database.
        3. The new resident is added to the database session.
        4. The session is committed to save the changes.
        5. The session is closed to free up resources.

    Returns:
        dict: A status dictionary indicating success, e.g., `{"status": "ok"}`.

    """

    body_row = residentMysql.Resident(
        name=body.name,
        surname=body.surname,
        birthDate=body.birthDate,
        gender=body.gender,
        createdBy=body.createdBy,
        createDate=date.today(),
        idFamily=body.idFamily,
        idRoom=body.idRoom
    )
    
    db = DatabaseClient(gb.MYSQL_URL)
    with Session(db.engine) as session:
        session.add(body_row)
        session.commit()
        session.close()
    
    return {"status": "ok"}
  
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
  
