from fastapi import FastAPI
from typing import Union
from app.controllers.handler import Controllers
from app.mysql.mysql import DatabaseClient
from datetime import date


import app.utils.vars as gb
import app.models.models as models
import app.models.resident as resident
import app.models.family as family
import app.models.room as room
import app.models.shelter as shelter


def initialize() -> None:
  # initialize database
  dbClient = DatabaseClient(gb.MYSQL_URL)
  dbClient.init_database()
  return


app = FastAPI()
controllers = Controllers()

initialize()


@app.get('/healthz')
async def healthz():
  return controllers.healthz()

@app.post('/user/create')
async def create_user(body: models.UserRequest):
  return controllers.create_user(body)

@app.post('/user/delete')
async def delete_user(body: models.DeleteRequest):
  return controllers.delete_user(body.id)
  
@app.get('/user/get_all')
async def get_all_users():
  return controllers.get_all()

@app.post('/user/update')
async def update_user(body: models.UpdateRequest):
  return controllers.update_user(body)

@app.post('/resident/create')
async def create_resident(body: resident.Resident):
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
  return controllers.list_rooms_with_resident_count()

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



