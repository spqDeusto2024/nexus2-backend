from fastapi import FastAPI, HTTPException
from app.controllers.handler import Controllers
from app.mysql.mysql import DatabaseClient
from app.mysql.base import Base
from app.mysql.initializeData import initialize_database
from app.models import resident, room, family, machine, admin, alarm
from datetime import date
import app.utils.vars as gb
from app.models.resident import Resident as ResidentModel
from app.controllers import resident_controller
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # gePermitir solicitudes desde localhost:3000
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos HTTP (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todos los headers
)

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


@app.get("/room/residents")
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


@app.get("/room/access")
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

@app.get("/login")
async def login(name: str, surname: str):
    """
    Login endpoint to verify resident credentials.

    Args:
        name (str): Resident's first name.
        surname (str): Resident's surname.

    Returns:
        dict: Status of the login attempt and user details if successful.
    """
    # Llamada al controlador para realizar el login, pasando name y surname
    result = controllers.login(name, surname)
    
    if result["status"] == "error":
        raise HTTPException(status_code=401, detail=result["message"])
    
    return result

@app.get("/loginAdmin")
async def loginAdmin(email: str, password: str):
    """
    Login endpoint to verify resident credentials.

    Args:
        name (str): Resident's first name.
        surname (str): Resident's surname.

    Returns:
        dict: Status of the login attempt and user details if successful.
    """
    # Llamada al controlador para realizar el login, pasando name y surname
    result = controllers.loginAdmin(email, password)
    
    if result["status"] == "error":
        raise HTTPException(status_code=401, detail=result["message"])
    
    return result

@app.get("/listRooms")
async def list_rooms():
    result = controllers.list_rooms()
    
    # Verifica si el resultado es un diccionario y contiene "status"
    if isinstance(result, dict) and result.get("status") == "error":
        raise HTTPException(status_code=401, detail=result["message"])
    
    # Si no es un diccionario, asumimos que es una lista de habitaciones
    return {"status": "ok", "rooms": result}

@app.get("/listRooms/Room")
async def list_rooms_Room():
    result = controllers.list_rooms_Room()
    
    # Verifica si el resultado es un diccionario y contiene "status"
    if isinstance(result, dict) and result.get("status") == "error":
        raise HTTPException(status_code=401, detail=result["message"])
    
    # Si no es un diccionario, asumimos que es una lista de habitaciones
    return {"status": "ok", "rooms": result}

@app.delete("/admin/delete")
async def delete_admin(admin_id: int):
    """
    Deletes an admin user by ID.

    Args:
        admin_id (int): ID of the admin to be deleted.

    Returns:
        dict: Operation status and a message.
    """
    return controllers.deleteAdmin(admin_id)

@app.get("/admin/list")
async def list_admins():
    """
    Lists all admin users.

    Returns:
        dict: List of admins with their information.
    """
    return controllers.listAdmins()

@app.get("/admin/get")
async def get_admin(admin_id: int):
    """
    Obtiene los datos de un administrador por su ID.

    Args:
        admin_id (int): ID del administrador que se desea consultar.

    Returns:
        dict: Datos del administrador.
    """
    return controllers.getAdminById(admin_id)

@app.put("/admin/password")
async def update_admin_password(idAdmin: int, new_password: str):
    """
    Actualiza la contraseña de un administrador por su ID.

    Args:
        idAdmin (int): El ID del administrador cuyo password se va a actualizar.
        new_password (str): La nueva contraseña del administrador.

    Returns:
        dict: Estado de la operación y un mensaje.
    """
    return controllers.updateAdminPassword(idAdmin, new_password)

@app.put("/admin/email")
async def update_admin_email(idAdmin: int, new_email: str):
    """
    Actualiza la contraseña de un administrador por su ID.

    Args:
        idAdmin (int): El ID del administrador cuyo password se va a actualizar.
        new_password (str): La nueva contraseña del administrador.

    Returns:
        dict: Estado de la operación y un mensaje.
    """
    return controllers.updateAdminEmail(idAdmin, new_email)

@app.put("/admin/name")
async def update_admin_name(idAdmin: int, new_name: str):
    """
    Actualiza la contraseña de un administrador por su ID.

    Args:
        idAdmin (int): El ID del administrador cuyo password se va a actualizar.
        new_password (str): La nueva contraseña del administrador.

    Returns:
        dict: Estado de la operación y un mensaje.
    """
    return controllers.updateAdminName(idAdmin, new_name)

@app.put("/shelter/energyLevel")
async def update_energy_level(new_energy_level: int):
    return controllers.updateShelterEnergyLevel(new_energy_level)

@app.put("/shelter/waterLevel")
async def update_water_level(new_water_level: int):
    return controllers.updateShelterWaterLevel(new_water_level)

@app.put("/shelter/radiationLevel")
async def update_radiation_level(new_radiation_level: int):
    return controllers.updateShelterRadiationLevel(new_radiation_level)

@app.put("/machine/off")
async def off_machine (machine_name: str):
    return controllers.updateMachineStatus(machine_name)

@app.put("/machine/on")
async def on_machine (machine_name: str):
    return controllers.updateMachineStatusOn(machine_name)

@app.put("/resident/idRoom")
async def new_idRoom (resident_id: int, new_room_id: int):
    return controllers.updateResidentRoom(resident_id, new_room_id)

@app.get("/resident/get")
async def get_admin(idResident: int):
    return controllers.getResidentById(idResident)

@app.post("/alarmLevel/create")
async def create_alarm_level(body: alarm.Alarm):
    """
    Creates a new alarm.

    Args:
        body (alarm.Alarm): Alarm data.

    Returns:
        dict: Operation status and a message.
    """
    return controllers.create_alarmLevel(body)

@app.put("/alarm/putEnd")
async def alarm_endDate (idAlarm: int, new_enddate: datetime):
    return controllers.updateAlarmEndDate(idAlarm, new_enddate)

@app.get("/alarm/list")
async def list_alarms():
    """
    Retrieves a list of all residents.

    Returns:
        list[dict]: List of residents.
    """
    return controllers.list_alarms()

@app.get("/machine/list")
async def list_machines():
    """
    Retrieves a list of all machines.
    """
    return controllers.list_machines()

@app.delete("/machine/delete")
async def delete_machine(machine_id: int):
    return controllers.deleteMachine(machine_id)

@app.put("/machine/update")
async def update_machine (machine_name: str):
    return controllers.updateMachineDate(machine_name)

@app.put("/room/name")
async def update_Room_Name(idRoom: int, new_name: str):
    return controllers.updateRoomName(idRoom, new_name)

@app.delete("/family/delete")
async def delete_family(family_id: int):
    return controllers.deleteFamily(family_id)

@app.get("/family/list")
async def list_family():
    return controllers.listFamilies()