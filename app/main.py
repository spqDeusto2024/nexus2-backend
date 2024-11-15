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

from app.mysql.initializeData import initialize_database
from app.mysql.base import Base
from app.mysql.alarm import Alarm 
from app.mysql.admin import Admin 
from app.mysql.family import Family
from app.mysql.machine import Machine 
from app.mysql.resident import Resident
from app.mysql.room import Room
from app.mysql.shelter import Shelter    

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



