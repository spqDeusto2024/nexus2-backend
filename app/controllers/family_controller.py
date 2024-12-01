from app.mysql.mysql import DatabaseClient
from app.mysql.family import Family  # SQLAlchemy model
from app.mysql.room import Room  # SQLAlchemy model
from app.mysql.shelter import Shelter  # SQLAlchemy model
from app.mysql.admin import Admin  # SQLAlchemy model
from app.models.family import Family as FamilyModel  # Pydantic model
from sqlalchemy.orm import Session
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
import os

from datetime import date
import app.utils.vars as gb
from sqlalchemy.orm import Session
from sqlalchemy import func

class FamilyController:

    def __init__(self, db_url=None):
        # Usa MYSQL_URL de la variable de entorno si no se pasa db_url
        self.db_url = db_url or os.getenv("MYSQL_URL")
        if not self.db_url:
            raise ValueError("MYSQL_URL environment variable is not set.")
        self.db_client = DatabaseClient(self.db_url)

    def create_family(self, body: FamilyModel, session=None):
        """
        Crea una nueva familia en la base de datos y verifica las condiciones previas.
        """
        if session is None:
            session = Session(self.db_client.engine)

        try:
            # Validar la existencia de la habitación
            room = session.query(Room).filter(Room.idRoom == body.idRoom).first()
            if not room:
                return {"status": "error", "message": "The room does not exist."}

            # Validar la existencia del refugio
            shelter = session.query(Shelter).filter(Shelter.idShelter == body.idShelter).first()
            if not shelter:
                return {"status": "error", "message": "The shelter does not exist."}

            # Validar la existencia del administrador
            admin = session.query(Admin).filter(Admin.idAdmin == body.createdBy).first()
            if not admin:
                return {"status": "error", "message": "The admin does not exist."}

            # Verificar duplicados de familia en la misma habitación
            existing_family = session.query(Family).filter(
                Family.familyName == body.familyName,
                Family.idRoom == body.idRoom
            ).first()
            if existing_family:
                return {"status": "error", "message": "A family with the same name already exists in this room."}

            # Crear y agregar la nueva familia
            new_family = Family(
                idFamily=body.idFamily,
                familyName=body.familyName,
                idRoom=body.idRoom,
                idShelter=body.idShelter,
                createdBy=body.createdBy,
                createDate=body.createDate
            )
            session.add(new_family)
            session.commit()
            return {"status": "ok"}
        except SQLAlchemyError as e:
            session.rollback()
            return {"status": "error", "message": str(e)}
        finally:
            session.close()

    def deleteFamily(self, family_id: int, session=None):
        """
        Elimina una familia de la base de datos usando su ID, si no tiene miembros asociados.

        Args:
            family_id (int): ID de la familia que se desea eliminar.
            session (Session, optional): Sesión SQLAlchemy para interacción con la base de datos.

        Returns:
            dict: Resultado de la operación.
                - {"status": "ok", "message": "Family deleted successfully"}: Si la eliminación es exitosa.
                - {"status": "error", "message": <error_message>}: Si ocurre algún error.
        """
        if session is None:
            session = Session(self.db_client.engine)

        try:
            # Buscar la familia en la base de datos por ID
            family = session.query(Family).filter(Family.idFamily == family_id).first()

            # Verificamos si no se encontró la familia
            if not family:
                return {"status": "error", "message": "Family not found"}

            # Verificamos si hay miembros asociados a esta familia
            members = session.query(Resident).filter(Resident.idFamily == family_id).all()

            # Si hay miembros asociados, no permitimos eliminar la familia
            if members:
                return {"status": "error", "message": "Cannot delete family, there are members associated with it"}

            # Si no hay miembros, procedemos a eliminar la familia
            session.delete(family)
            session.commit()

            return {"status": "ok", "message": "Family deleted successfully"}

        except Exception as e:
            # Capturamos cualquier excepción y deshacemos los cambios en caso de error
            session.rollback()
            return {"status": "error", "message": str(e)}

        finally:
            # Aseguramos cerrar la sesión para evitar problemas con conexiones abiertas
            if session:
                session.close()
    
    def listFamilies(self, session=None):
        """
        Lista todas las familias registradas en la base de datos.

        Args:
            session (Session, optional): Sesión SQLAlchemy para interacción con la base de datos.

        Returns:
            dict: Resultado de la operación.
                - {"status": "ok", "families": [<listado_de_familias>]}: Si se encuentran familias.
                - {"status": "error", "message": <error_message>}: Si ocurre algún error.
        """
        if session is None:
            session = Session(self.db_client.engine)

        try:
            # Consulta todas las familias
            families = session.query(Family).all()

            # Convertimos el resultado en una lista de diccionarios con los atributos deseados
            families_list = [
                {
                    "idFamily": family.idFamily,
                    "familyName": family.familyName,
                    "idRoom": family.idRoom,
                    "idShelter": family.idShelter,
                    "createdBy": family.createdBy,
                    "createDate": family.createDate.isoformat() if family.createDate else None
                }
                for family in families
            ]

            return {"status": "ok", "families": families_list}

        except Exception as e:
            # Captura cualquier excepción
            return {"status": "error", "message": str(e)}

        finally:
            # Cerramos la sesión
            if session:
                session.close()

