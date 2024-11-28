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
        Determines whether a resident is allowed to access a specified room and updates the room for the resident.
        """
        if session is None:
            db = DatabaseClient(gb.MYSQL_URL)
            session = Session(db.engine)

        try:
            # Obtener el residente y la habitación
            resident = session.query(Resident).filter_by(idResident=idResident).first()
            room = session.query(Room).filter_by(idRoom=idRoom).first()

            # Verificar si el residente existe
            if resident is None:
                print(f"Resident {idResident} not found.")
                return "Resident not found."

            # Verificar si la habitación existe
            if room is None:
                print(f"Room {idRoom} not found.")
                return "Room not found."

            # Verificar si la habitación es pública o común (ej: Kitchen)
            public_rooms = ["Kitchen", "Bathroom", "Lobby"]
            if room.roomName in public_rooms:
                print(f"Access granted to public room {room.roomName}.")
                return "Access granted. Welcome to the room."

            # Si la habitación no comienza con "Room", acceso concedido
            if not room.roomName.startswith("Room"):
                print(f"Access granted without family check, room {room.roomName} is not restricted.")
                return "Access granted. Welcome to the room."

            # Verificar si el residente es parte de una familia y si la habitación es asignada a esa familia
            family = session.query(Family).filter_by(idRoom=room.idRoom).first()
            if family and resident.idFamily == family.idFamily:
                print(f"Resident {resident.idResident} is allowed to access room {room.idRoom}.")

                # Actualizar el idRoom del residente
                resident.idRoom = room.idRoom
                session.flush()  # Escribir los cambios en la base de datos
                session.commit()

                # Verificar si la actualización fue exitosa
                session.refresh(resident)  # Vuelve a cargar el objeto residente desde la base de datos
                print(f"Updated resident idRoom: {resident.idRoom}")

                if resident.idRoom == room.idRoom:
                    return "Access granted. Welcome to the room."
                else:
                    print("Error: Resident idRoom update failed.")
                    return "Error updating resident's room."

            else:
                print(f"Resident {resident.idResident} is not allowed to access room {room.idRoom}.")
                return "Access denied. You are in the wrong room."

        except SQLAlchemyError as e:
            session.rollback()
            print(f"SQLAlchemy error: {str(e)}")
            return {"status": "error", "message": str(e)}

        except Exception as e:
            session.rollback()
            print(f"Error: {str(e)}")
            return {"status": "error", "message": str(e)}

        finally:
            session.close()  # Asegurarse de cerrar la sesión después de la operación

        
    def list_rooms(self, session=None):
        """
        Lista las habitaciones con información básica: id, nombre, capacidad, y shelter asociado.

        Returns:
            list[dict]: Una lista de habitaciones con id, nombre, capacidad, y shelter.
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