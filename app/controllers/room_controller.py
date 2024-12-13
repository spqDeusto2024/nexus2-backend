from app.mysql.mysql import DatabaseClient
from app.mysql.room import Room  # SQLAlchemy model
from app.mysql.resident import Resident  # SQLAlchemy model
from app.mysql.admin import Admin  # SQLAlchemy model
from app.mysql.family import Family  # SQLAlchemy model
from app.mysql.shelter import Shelter  # SQLAlchemy model
from app.models.room import Room as RoomModel  # Pydantic model
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
import app.utils.vars as gb

import app.models.resident as resident
import app.models.family as family
import app.models.room as room
import app.models.shelter as shelter
import app.models.machine as machine
import app.mysql.family as familyMysql
import app.mysql.room as roomMysql
import app.mysql.shelter as shelterMysql
import app.mysql.resident as residentMysql
import app.mysql.admin as adminMysql
import app.mysql.machine as machineMysql
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
import os

class RoomController:

    def __init__(self, db_url=None):
        # Usa MYSQL_URL de la variable de entorno si no se pasa db_url
        self.db_url = db_url or os.getenv("MYSQL_URL")
        if not self.db_url:
            raise ValueError("MYSQL_URL environment variable is not set.")
        self.db_client = DatabaseClient(self.db_url)

    def create_room(self, body: RoomModel, session=None):
        """
        Creates a new room in the database.

        This method validates the existence of the admin and shelter before creating a room. 
        It also ensures that no duplicate rooms exist in the specified shelter.

        Args:
            body (RoomModel): The data of the room to be created, including:
                - idRoom (int, optional): The unique identifier for the room.
                - roomName (str): The name of the room.
                - createdBy (int): The ID of the admin who creates the room.
                - createDate (date): The date the room is created.
                - idShelter (int): The ID of the shelter where the room belongs.
                - maxPeople (int): The maximum capacity of the room.
            session (Session, optional): SQLAlchemy session object for database interaction.
                If not provided, a new session will be created.

        Returns:
            dict: Result of the operation.
                - {"status": "ok"}:
                If the room is successfully created.
                - {"status": "error", "message": "The admin does not exist"}:
                If the provided admin ID does not exist in the database.
                - {"status": "error", "message": "The shelter does not exist"}:
                If the provided shelter ID does not exist in the database.
                - {"status": "error", "message": "The room already exists in this shelter"}:
                If a room with the same name already exists in the specified shelter.
                - {"status": "error", "message": <error_message>}:
                If any other error occurs during the operation.

        Raises:
            Exception: If an unexpected error occurs during the operation.

        Notes:
            - Ensure the provided `roomName` is unique within the specified shelter.
            - The `createdBy` field must correspond to an existing admin, and `idShelter` must correspond to an existing shelter.

        """

        if session is None:
            session = Session(self.db_client.engine)
        try:
            admin = session.query(Admin).filter(Admin.idAdmin == body.createdBy).first()
            if not admin:
                return {"status": "error", "message": "The admin does not exist."}

            shelter = session.query(Shelter).filter(Shelter.idShelter == body.idShelter).first()
            if not shelter:
                return {"status": "error", "message": "The shelter does not exist."}

            existing_room = session.query(Room).filter(
                Room.roomName == body.roomName,
                Room.idShelter == body.idShelter
            ).first()
            if existing_room:
                return {"status": "error", "message": "The room already exists in this shelter."}

            new_room = Room(
                idRoom=body.idRoom,
                roomName=body.roomName,
                createdBy=body.createdBy,
                createDate=body.createDate,
                idShelter=body.idShelter,
                maxPeople=body.maxPeople
            )
            session.add(new_room)
            session.commit()
            return {"status": "ok"}
        except Exception as e:
            session.rollback()
            return {"status": "error", "message": str(e)}
        finally:
            session.close()

    def list_rooms_with_resident_count(self, session=None):

        """
        Lists all rooms along with the count of residents in each room.

        This method retrieves a list of all rooms in the database, including their details 
        and the number of residents currently assigned to each room.

        Args:
            session (Session, optional): SQLAlchemy session object for database interaction.
                If not provided, a new session will be created.

        Returns:
            list: A list of dictionaries, each representing a room and its resident count. 
                Each dictionary contains:
                    - idRoom (int): The unique identifier of the room.
                    - roomName (str): The name of the room.
                    - maxPeople (int): The maximum capacity of the room.
                    - resident_count (int): The number of residents currently in the room.
            dict: If an error occurs, a dictionary with:
                    - {"status": "error", "message": <error_message>}

        Raises:
            Exception: If an unexpected error occurs during the operation.

        Example Response:
            [
                {
                    "idRoom": 1,
                    "roomName": "Room A",
                    "maxPeople": 10,
                    "resident_count": 5
                },
                {
                    "idRoom": 2,
                    "roomName": "Room B",
                    "maxPeople": 8,
                    "resident_count": 0
                }
            ]

        Notes:
            - Rooms without residents will still appear in the list with a `resident_count` of 0.
            - The method uses an `outerjoin` to include rooms without any assigned residents.
        """


        if session is None:
            session = Session(self.db_client.engine)
        try:
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
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            session.close()

    def access_room(self, idResident: int, idRoom: int, session=None):
        """
        Determines if a resident can access a specific room based on the room's capacity, 
        type, and family assignment.

        This method checks the access rules for a resident attempting to enter a room:
        - Verifies if the resident and room exist.
        - Denies access to restricted rooms like "Maintenance."
        - Ensures the room is not over capacity.
        - Allows access to public or common rooms.
        - Grants access if the room belongs to the resident's family.
        - Denies access otherwise.

        Args:
            idResident (int): The unique identifier of the resident attempting to access the room.
            idRoom (int): The unique identifier of the room the resident is trying to access.
            session (Session, optional): SQLAlchemy session object for database interaction.
                If not provided, a new session will be created.

        Returns:
            str: A message indicating the result of the access attempt:
                - "Resident not found.": If the resident does not exist.
                - "Room not found.": If the room does not exist.
                - "Access denied. No puedes entrar a la sala de mantenimiento.": If the room is restricted (e.g., Maintenance).
                - "Access denied. La sala está llena.": If the room is at maximum capacity.
                - "Access granted. Welcome to the room.": If access is granted to public or family-assigned rooms.
                - "Access denied. You are in the wrong room.": If the resident is not assigned to the room.

        Raises:
            Exception: If an unexpected error occurs during the operation.

        Notes:
            - Public or common rooms (not starting with "Room") are accessible to all residents.
            - Family-assigned rooms are only accessible to members of the assigned family.
            - The room's current occupancy is checked against its maximum capacity.

        """
        if session is None:
            db = DatabaseClient(gb.MYSQL_URL)
            session = Session(db.engine)

        # Obtener los datos del residente y de la sala
        resident = session.query(Resident).filter_by(idResident=idResident).first()
        room = session.query(Room).filter_by(idRoom=idRoom).first()

        # Validar si el residente existe
        if resident is None:
            return "Resident not found."

        # Validar si la sala existe
        if room is None:
            return "Room not found."

        # Bloquear acceso a la sala de mantenimiento
        if room.roomName.lower() == "mantenimiento":  # Comparamos en minúsculas por seguridad
            return "Access denied. No puedes entrar a la sala de mantenimiento."

        # Verificar la ocupación actual de la sala
        currentOccupancy = (
            session.query(Resident)
            .filter(Resident.idRoom == idRoom)  # Filtrar a los residentes en esta sala
            .count()
        )

        if currentOccupancy >= room.maxPeople:
            return "Access denied. La sala está llena."

        # Acceso permitido a salas públicas o comunes
        if not room.roomName.startswith("Room"):
            return "Access granted. Welcome to the room."

        # Verificar si la sala pertenece a la familia del residente
        family = session.query(Family).filter_by(idRoom=room.idRoom).first()
        if family and resident.idFamily == family.idFamily:
            return "Access granted. Welcome to the room."

        # Acceso denegado por no pertenecer a la familia asignada
        return "Access denied. You are in the wrong room."


    def list_rooms(self, session=None):

        """
        Lists all rooms with basic information.

        This method retrieves a list of all rooms in the database, including their 
        basic details such as ID, name, capacity, associated shelter, and creation date.

        Args:
            session (Session, optional): SQLAlchemy session object for database interaction.
                If not provided, a new session will be created.

        Returns:
            list: A list of dictionaries, each representing a room with the following details:
                - idRoom (int): The unique identifier of the room.
                - roomName (str): The name of the room.
                - maxPeople (int): The maximum capacity of the room.
                - idShelter (int): The ID of the shelter the room belongs to.
                - createDate (str, optional): The creation date of the room in ISO 8601 format.
            dict: If an error occurs, a dictionary with:
                - {"status": "error", "message": <error_message>}

        Raises:
            Exception: If an unexpected error occurs during the operation.

        Example Response:
            [
                {
                    "idRoom": 1,
                    "roomName": "Room A",
                    "maxPeople": 10,
                    "idShelter": 1,
                    "createDate": "2024-12-01"
                },
                {
                    "idRoom": 2,
                    "roomName": "Room B",
                    "maxPeople": 8,
                    "idShelter": 2,
                    "createDate": "2024-12-02"
                }
            ]

        Notes:
            - The creation date (`createDate`) will be formatted in ISO 8601. If not available, it will be `None`.
        """

        if session is None:
            session = Session(self.db_client.engine)
        try:
            rooms = session.query(Room).all()
            return [
                {
                    "idRoom": room.idRoom,
                    "roomName": room.roomName,
                    "maxPeople": room.maxPeople,
                    "idShelter": room.idShelter,
                    "createDate": room.createDate.isoformat() if room.createDate else None,
                }
                for room in rooms
            ]
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            session.close()


    def updateRoomName(self, idRoom: int, new_name: str, session=None):
        """
        Updates the name of a specific room.

        This method searches for a room by its unique ID and updates its `roomName` field 
        with the provided new name.

        Args:
            idRoom (int): The unique identifier of the room whose name will be updated.
            new_name (str): The new name to assign to the room.
            session (Session, optional): SQLAlchemy session object for database interaction.
                If not provided, a new session will be created.

        Returns:
            dict: Result of the operation.
                - {"status": "ok", "message": "Room name updated successfully"}:
                If the room name is successfully updated.
                - {"status": "error", "message": "Room not found"}:
                If no room with the given ID is found in the database.
                - {"status": "error", "message": <error_message>}:
                If an error occurs during the operation.

        Raises:
            SQLAlchemyError: If a database-related error occurs.
            Exception: If an unexpected error occurs during the operation.

        """
        if session is None:
            session = Session(self.db_client.engine)

        try:
            # Buscar la habitación por idRoom
            room = session.query(Room).filter(Room.idRoom == idRoom).first()

            if room is None:
                return {"status": "error", "message": "Habitación no encontrada"}

            # Actualizamos el nombre de la habitación
            room.roomName = new_name

            # Guardamos los cambios
            session.commit()

            return {"status": "ok", "message": "Nombre de la habitación actualizado exitosamente"}

        except SQLAlchemyError as e:
            # Captura errores de la base de datos
            session.rollback()  # Revertir cualquier cambio en caso de error
            return {"status": "error", "message": f"Error de base de datos: {str(e)}"}

        except Exception as e:
            # Captura cualquier otro tipo de error
            return {"status": "error", "message": str(e)}

        finally:
            # Cerramos la sesión
            if session:
                session.close()
    

    def list_rooms_Room(self, session=None):

        """
        Lists all rooms whose names start with "Room".

        This method retrieves a list of rooms from the database where the `roomName` field 
        begins with the string "Room".

        Args:
            session (Session, optional): SQLAlchemy session object for database interaction.
                If not provided, a new session will be created.

        Returns:
            list: A list of dictionaries, each representing a room with the following details:
                - idRoom (int): The unique identifier of the room.
                - roomName (str): The name of the room.
                - maxPeople (int): The maximum capacity of the room.
                - idShelter (int): The ID of the shelter the room belongs to.
                - createDate (str, optional): The creation date of the room in ISO 8601 format.
            dict: If an error occurs, a dictionary with:
                - {"status": "error", "message": <error_message>}

        Raises:
            Exception: If an unexpected error occurs during the operation.

        Example Response:
            [
                {
                    "idRoom": 1,
                    "roomName": "Room A",
                    "maxPeople": 10,
                    "idShelter": 1,
                    "createDate": "2024-12-01"
                },
                {
                    "idRoom": 2,
                    "roomName": "Room B",
                    "maxPeople": 8,
                    "idShelter": 1,
                    "createDate": "2024-12-02"
                }
            ]

        Notes:
            - Only rooms whose `roomName` starts with "Room" will be included in the response.
            - The creation date (`createDate`) will be formatted in ISO 8601. If not available, it will be `None`.

        """
        if session is None:
            session = Session(self.db_client.engine)
        try:
            # Filtramos las habitaciones cuyo nombre empieza con "Room"
            rooms = session.query(Room).filter(Room.roomName.like('Room%')).all()
            
            # Retornamos la lista con los datos de las habitaciones
            return [
                {
                    "idRoom": room.idRoom,
                    "roomName": room.roomName,
                    "maxPeople": room.maxPeople,
                    "idShelter": room.idShelter,
                    "createDate": room.createDate.isoformat() if room.createDate else None,
                }
                for room in rooms
            ]
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            session.close()

def test_list_rooms_room_success(setup_database):
    """
    Test: Successfully retrieve a list of rooms whose names start with "Room".

    Expected Outcome:
        - Returns a list of rooms starting with "Room".
    """
    session = setup_database
    controller = RoomController()

    # Add test rooms to the database
    room1 = Room(
        idRoom=1,
        roomName="Room A",
        maxPeople=10,
        idShelter=1,
        createDate=datetime(2024, 12, 1)
    )
    room2 = Room(
        idRoom=2,
        roomName="Room B",
        maxPeople=8,
        idShelter=1,
        createDate=datetime(2024, 12, 2)
    )
    room3 = Room(
        idRoom=3,
        roomName="Office A",  # Should be excluded
        maxPeople=5,
        idShelter=2,
        createDate=datetime(2024, 12, 3)
    )
    session.add_all([room1, room2, room3])
    session.commit()

    # Call the method
    response = controller.list_rooms_Room(session=session)

    # Assert the response
    assert len(response) == 2
    assert response[0]["roomName"] == "Room A"
    assert response[1]["roomName"] == "Room B"


def test_list_rooms_room_no_rooms(setup_database):
    """
    Test: No rooms whose names start with "Room" are found.

    Expected Outcome:
        - Returns an empty list.
    """
    session = setup_database
    controller = RoomController()

    # Add a room that doesn't start with "Room"
    room = Room(
        idRoom=1,
        roomName="Office A",
        maxPeople=5,
        idShelter=1,
        createDate=datetime(2024, 12, 1)
    )
    session.add(room)
    session.commit()

    # Call the method
    response = controller.list_rooms_Room(session=session)

    # Assert the response
    assert len(response) == 0

def test_list_rooms_room_unexpected_error(setup_database, mocker):
    """
    Test: Simulate an unexpected error during the retrieval of rooms.

    Expected Outcome:
        - Returns an error message.
    """
    session = setup_database
    controller = RoomController()

    # Mock session.query to raise an exception
    mocker.patch("sqlalchemy.orm.Session.query", side_effect=Exception("Unexpected error"))

    # Call the method
    response = controller.list_rooms_Room(session=session)

    # Assert the response
    assert response["status"] == "error"
    assert "Unexpected error" in response["message"]