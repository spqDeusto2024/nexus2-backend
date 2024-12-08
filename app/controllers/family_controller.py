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
        Creates a new family in the database and validates preconditions.

        This method verifies that the room, shelter, and admin associated with the family exist, 
        and ensures no duplicate family with the same name exists in the specified room before 
        creating a new family.

        Args:
            body (FamilyModel): An object containing the details of the family to be created, including:
                - idFamily (int): The unique identifier of the family.
                - familyName (str): The name of the family.
                - idRoom (int): The unique identifier of the room where the family resides.
                - idShelter (int): The unique identifier of the shelter associated with the family.
                - createdBy (int): The ID of the admin who creates the family record.
                - createDate (datetime): The date when the family record is created.
            session (Session, optional): SQLAlchemy session object for database interaction.
                If not provided, a new session will be created.

        Returns:
            dict: Result of the operation.
                - {"status": "ok"}:
                If the family is created successfully.
                - {"status": "error", "message": <error_message>}:
                If an error occurs, such as missing entities (room, shelter, admin) 
                or duplicate family names in the same room.

        Raises:
            SQLAlchemyError: If a database-related error occurs.
            Exception: If an unexpected error occurs during the operation.
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
        Deletes a family from the database using its ID, if no members are associated with it.

        This method first verifies that the family exists and that no residents are linked 
        to the family. If there are associated members, the deletion is not allowed.

        Args:
            family_id (int): The unique identifier of the family to delete.
            session (Session, optional): SQLAlchemy session object for database interaction.
                If not provided, a new session will be created.

        Returns:
            dict: Result of the operation.
                - {"status": "ok", "message": "Family deleted successfully"}:
                If the family is successfully deleted.
                - {"status": "error", "message": <error_message>}:
                If an error occurs, such as the family not being found or members being associated with it.

        Raises:
            Exception: If an unexpected error occurs during the operation.
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
        Lists all families registered in the database.

        This method retrieves all families from the database and formats their details 
        into a list of dictionaries.

        Args:
            session (Session, optional): SQLAlchemy session object for database interaction.
                If not provided, a new session will be created.

        Returns:
            dict: Result of the operation.
                - {"status": "ok", "families": [<list_of_families>]}:
                If the families are successfully retrieved. Each family in the list contains:
                    - idFamily (int): The unique identifier of the family.
                    - familyName (str): The name of the family.
                    - idRoom (int): The unique identifier of the room associated with the family.
                    - idShelter (int): The unique identifier of the shelter associated with the family.
                    - createdBy (int): The ID of the admin who created the family.
                    - createDate (str, optional): The date the family was created, in ISO 8601 format.
                - {"status": "error", "message": <error_message>}:
                If an error occurs during the operation.

        Raises:
            Exception: If an unexpected error occurs while querying the database.
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

