from fastapi import FastAPI, HTTPException
from app.controllers.handler import Controllers
from app.mysql.mysql import DatabaseClient
from app.mysql.base import Base
from app.mysql.initializeData import initialize_database
from app.models import resident, room, family, machine, admin, alarm
from datetime import date
import app.utils.vars as gb

# Database initialization
def initialize() -> None:
    """
    Initializes the database by creating the schema and populating it with initial data.
    """
    db_client = DatabaseClient(gb.MYSQL_URL)
    Base.metadata.create_all(db_client.engine)
    initialize_database()

# Initialize FastAPI and controllers
app = FastAPI()
controllers = Controllers()

# Execute database initialization
initialize()


# API Routes
@app.get("/healthz")
async def healthz():
    """
    Health check endpoint to verify the server's status.

    Returns:
        dict: Status message indicating that the server is running.
    """
    return controllers.healthz()


# Resident
@app.post("/resident/create")
async def create_resident(body: resident.Resident):
    """
    Creates a new resident.

    Args:
        body (resident.Resident): Resident data.

    Returns:
        dict: Operation status and a message.
    """
    return controllers.create_resident(body)


@app.delete("/resident/delete/{idResident}")
async def delete_resident(idResident: int):
    """
    Deletes a resident by their ID.

    Args:
        idResident (int): Resident ID.

    Returns:
        dict: Operation status and a message.
    """
    return controllers.delete_resident(idResident)


@app.put("/resident/update/{idResident}")
async def update_resident(
    idResident: int,
    name: str = None,
    surname: str = None,
    birthDate: date = None,
    gender: str = None,
    idFamily: int = None,
    idRoom: int = None,
):
    """
    Updates a resident's information by their ID.

    Args:
        idResident (int): Resident ID.
        name (str, optional): New first name.
        surname (str, optional): New last name.
        birthDate (date, optional): New birth date.
        gender (str, optional): New gender.
        idFamily (int, optional): New family ID.
        idRoom (int, optional): New room ID.

    Returns:
        dict: Operation status and a message.
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
    return controllers.update_resident(idResident, updated_fields)


@app.get("/resident/list")
async def list_residents():
    """
    Retrieves a list of all residents.

    Returns:
        list[dict]: List of residents.
    """
    return controllers.list_residents()


@app.get("/room/{idRoom}/residents")
async def list_residents_in_room(idRoom: int):
    """
    Retrieves a list of all residents in a specific room.

    Args:
        idRoom (int): Room ID.

    Returns:
        list[dict]: List of residents in the specified room.
    """
    return controllers.list_residents_in_room(idRoom)


# Room
@app.post("/room/create")
async def create_room(body: room.Room):
    """
    Creates a new room.

    Args:
        body (room.Room): Room data.

    Returns:
        dict: Operation status and a message.
    """
    return controllers.create_room(body)


@app.get("/room/list_with_counts")
async def list_rooms_with_resident_count():
    """
    Retrieves a list of all rooms with the count of residents in each room.

    Returns:
        list[dict]: List of rooms with resident counts.
    """
    return controllers.list_rooms_with_resident_count()


@app.post("/room/access")
async def access_room(idResident: int, idRoom: int):
    """
    Verifies whether a resident can access a specified room.

    Args:
        idResident (int): Resident ID.
        idRoom (int): Room ID.

    Returns:
        dict: Access result message.
    """
    try:
        message = controllers.access_room(idResident, idRoom)
        return {"message": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Shelter
@app.get("/shelter/energy")
async def get_shelter_energy_level():
    """
    Retrieves the energy level of the shelter.

    Returns:
        dict: Shelter energy level.
    """
    try:
        return controllers.get_shelter_energy_level()
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/shelter/water")
async def get_shelter_water_level():
    """
    Retrieves the water level of the shelter.

    Returns:
        dict: Shelter water level.
    """
    try:
        return controllers.get_shelter_water_level()
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/shelter/radiation")
async def get_shelter_radiation_level():
    """
    Retrieves the radiation level of the shelter.

    Returns:
        dict: Shelter radiation level.
    """
    try:
        return controllers.get_shelter_radiation_level()
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))


# Family
@app.post("/family/create")
async def create_family(body: family.Family):
    """
    Creates a new family.

    Args:
        body (family.Family): Family data.

    Returns:
        dict: Operation status and a message.
    """
    return controllers.create_family(body)


# Machine
@app.post("/machine/create")
async def create_machine(body: machine.Machine):
    """
    Creates a new machine.

    Args:
        body (machine.Machine): Machine data.

    Returns:
        dict: Operation status and a message.
    """
    return controllers.create_machine(body)


# Alarm
@app.post("/alarm/create")
async def create_alarm(body: alarm.Alarm):
    """
    Creates a new alarm.

    Args:
        body (alarm.Alarm): Alarm data.

    Returns:
        dict: Operation status and a message.
    """
    return controllers.create_alarm(body)


# Admin
@app.post("/admin/create")
async def create_admin(body: admin.Admin):
    """
    Creates a new admin user.

    Args:
        body (admin.Admin): Admin data.

    Returns:
        dict: Operation status and a message.
    """
    return controllers.create_admin(body)
