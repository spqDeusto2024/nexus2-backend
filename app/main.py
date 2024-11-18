from fastapi import FastAPI
from typing import Union
from app.controllers.handler import Controllers
from app.mysql.mysql import DatabaseClient
from datetime import date


import app.utils.vars as gb
import app.models.resident as resident
import app.models.family as family
import app.models.room as room
import app.models.shelter as shelter
import app.models.machine as machine
import app.models.admin as admin

from app.mysql.initializeData import initialize_database
from app.mysql.base import Base
from app.mysql.alarm import Alarm 
from app.mysql.admin import Admin
from app.mysql.family import Family
from app.mysql.machine import Machine 
from app.mysql.resident import Resident
from app.mysql.room import Room
from app.mysql.shelter import Shelter    
from app.mysql.admin import Admin

def initialize() -> None:
    """
    Initializes the database by:
    - Creating the database schema from the SQLAlchemy models.
    - Running the database initialization logic (e.g., seeding initial data).
    """
    dbClient = DatabaseClient(gb.MYSQL_URL)
    Base.metadata.create_all(dbClient.engine) 
    dbClient.init_database()  
    initialize_database()  
    return


app = FastAPI()
controllers = Controllers()

initialize()


@app.get('/healthz')
async def healthz():
  return controllers.healthz()

@app.post('/resident/create')
async def create_resident(body: resident.Resident):
    """
    Creates a new resident in the system. This endpoint ensures that the resident is added to an existing family and room, 
    or a new room is created if necessary. The function also checks that there are no duplicate residents, that the shelter's 
    capacity is not exceeded, and that the family has an assigned room.

    This endpoint expects the following data structure in the request body:
    - `name`: The first name of the resident.
    - `surname`: The last name of the resident.
    - `birthDate`: The birthdate of the resident.
    - `gender`: The gender of the resident.
    - `idFamily`: The ID of the family to which the resident belongs.
    - `idRoom`: The ID of the room the resident will be assigned to. If the family does not have a room assigned, a new room will be created.

    Arguments:
        body (resident.Resident): The resident data to be added to the database, which includes personal information and family details.

    Returns:
        dict: A response containing the status of the operation and a message.
              - Success: `{"status": "ok"}`
              - Error: `{"status": "error", "message": "Error message explaining the issue."}`

    """
    return controllers.create_resident(body)

@app.delete('/resident/delete')
async def delete_resident(idResident: int):
  
    """
    Endpoint to delete a resident by their ID.

    Parameters:
        idResident (int): The unique ID of the resident to delete.

    Returns:
        dict: A response indicating the success or failure of the deletion.
    """
    return controllers.delete_resident(idResident)

@app.post('/resident/update')
async def update_resident(
    idResident: int, 
    name: str = None, 
    surname: str = None, 
    birthDate: date = None, 
    gender: str = None, 
    idFamily: int = None, 
    idRoom: int = None
):
    """
    Endpoint to update a resident's details by their ID.

    Parameters:
        idResident (int): The unique ID of the resident to update.
        name (str, optional): Updated first name of the resident.
        surname (str, optional): Updated last name of the resident.
        birthDate (date, optional): Updated birth date of the resident.
        gender (str, optional): Updated gender of the resident.
        idFamily (int, optional): Updated family ID of the resident.
        idRoom (int, optional): Updated room ID of the resident.

    Returns:
        dict: A response indicating the success or failure of the update.
    """
    updated_fields = {
        "name": name,
        "surname": surname,
        "birthDate": birthDate,
        "gender": gender,
        "idFamily": idFamily,
        "idRoom": idRoom,
    }
    updated_fields = {key: value for key, value in updated_fields.items() if value is not None}

    return controllers.update_resident(idResident, **updated_fields)

@app.post('/rooms/create_room')
async def create_room(body: room.Room):
    """
    Creates a new room in the system. The function also checks that there are no duplicate rooms.

    This endpoint expects the following data structure in the request body:
    - `idRoom`: The ID of the room.
    - `roomName`: The name of the room.
    - `createdBy`: The creator of the room.
    - `createDate`: The date of the creation of the room.
    - `idShelter`: The ID of the shelter to which the room belongs.
    - `maxPeople`: The maximum capacity of the room.

    Arguments:
        body (room.Room): The room data to be added to the database.

    Returns:
        dict: A response containing the status of the operation and a message.
              - Success: `{"status": "ok"}`
              - Error: `{"status": "error", "message": "Error message explaining the issue."}`

    """
    return controllers.create_room(body)


@app.get('/rooms/list_with_counts')
async def list_rooms_with_counts():

  """
  Endpoint to list all rooms with the number of residents in each.

  Returns:
      list[dict]: A list of dictionaries containing room details and resident count.
  """
  try:
        return controllers.list_rooms_with_resident_count()
  except Exception as e:
        return {"error": str(e)}

@app.get('/shelter/energy-level')
async def get_shelter_energy_level():
  """
  Endpoint to retrieve the energy level of the shelter.

  Returns:
      dict: A response containing the energy level of the shelter, e.g., `{"energyLevel": 75}`.
  """
  try:
      return controllers.get_shelter_energy_level()
  except ValueError as e:
      return {"error": str(e)}

@app.get('/shelter/water-level')
async def get_shelter_water_level():
    """
    Endopoints to retrieve the water level of the shelter.

    Returns:
        dict: A response containing the water level of the shelter, e.g., `{"waterLevel": 50}`.
    """
    try:
        return controllers.get_shelter_water_level()
    except ValueError as e:
        return {"error": str(e)}

@app.get('/shelter/radiation-level')
async def get_shelter_radiation_level():
    
    """
    Endpoint to retrieve the radiation level of the shelter.

    Returns:
        dict: A response containing the radiation level of the shelter, e.g., `{"radiationLevel": 15}`.
    """
    try:
        return controllers.get_shelter_radiation_level()
    except ValueError as e:
        return {"error": str(e)}

@app.post('/room/access')
async def access_room(idResident: int, idRoom: int):
    """
    Endpoint to determine if a resident can access a specified room.

    Parameters:
        idResident (int): The unique ID of the resident attempting access.
        idRoom (int): The unique ID of the room being accessed.

    Returns:
        dict: A dictionary containing the result of the access attempt:
              - "message": A message indicating the access result.
    """
    try:
        message = controllers.access_room(idResident, idRoom)
        return {"message": message}
    except Exception as e:
        return {"error": str(e)}

@app.get('/rooms/{idRoom}/residents')
async def list_residents_in_room(idRoom: int):
    """
    Endpoint to list all residents in a specific room.

    Args:
        idRoom (int): The unique identifier of the room.

    Returns:
        list[dict]: A list of dictionaries containing details of the residents in the room.
    """
    try:
        return controllers.list_residents_in_room(idRoom)
    except Exception as e:
        return {"error": str(e)}

@app.post('/machine/create_machine')
async def create_machine(body: machine.Machine):
    """
    Creates a new machine in the system. The function also checks that there are no duplicate machines
    in the same room and that the machine is assigned to an existing room.

    This endpoint expects the following data structure in the request body:
    - `idMachine`: Unique identifier for the machine.
    - `machineName`: Name or identifier of the machine.
    - `on`: Operational status of the machine (True if on, False if off).
    - `idRoom`: Foreign key to the room where the machine is located.
    - `createdBy`: ID of the admin who created this machine record.
    - `createDate`: The date when the machine record was created.
    - `update`: The date when the machine record was last updated.

    Arguments:
        body (machine.Machine): The room data to be added to the database.

    Returns:
        dict: A response containing the status of the operation and a message.
              - Success: `{"status": "ok"}`
              - Error: `{"status": "error", "message": "Error message explaining the issue."}`

    """
    return controllers.create_machine(body)


@app.post('/admin/create')
async def create_admin(body: admin.Admin):
    """
    Endpoint to create a new admin.

    Parameters:
        body (admin.Admin): The admin details provided for creating the admin.

    Returns:
        dict: A dictionary indicating the result of the admin creation:
              - "status": "ok" or "error".
              - "message": Success or error message.
    """
    try:
        return controllers.create_admin(body)
    except Exception as e:
        return {"error": str(e)}
    
@app.post('/family/create')
async def create_family(body: family.Family):
    """
    Creates a new family in the system. Ensures the family is assigned to an 
    existing room and shelter, and that the admin who created the family exists. 
    Prevents duplicate families in the same room.

    This endpoint expects the following data structure in the request body:
    - `idFamily`: The unique identifier for the family.
    - `familyName`: The name or identifier of the family.
    - `idRoom`: The ID of the room the family will be assigned to.
    - `idShelter`: The ID of the shelter where the family resides.
    - `createdBy`: The ID of the admin who created the family record.
    - `createDate`: The date when the family record was created.

    Arguments:
        body (family.Family): The family data to be added to the database.

    Returns:
        dict: A response containing the status of the operation and a message.
              - Success: `{"status": "ok"}`
              - Error: `{"status": "error", "message": "Error message explaining the issue."}`
    """
    db_client = DatabaseClient(gb.MYSQL_URL)
    session = db_client.get_session()
    try:
        response = Controllers.create_family(body, session=session)
        if response["status"] == "error":
            raise HTTPException(status_code=400, detail=response["message"])
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


