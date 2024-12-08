from app.mysql.mysql import DatabaseClient
from app.mysql.resident import Resident
from app.mysql.room import Room
from app.mysql.shelter import Shelter
from app.mysql.family import Family as familyMysql
from sqlalchemy.orm import Session
from datetime import date
from sqlalchemy import func
from app.models.resident import Resident as ResidentModel  # Import Pydantic model
import app.utils.vars as gb
import os
from datetime import datetime
from datetime import date
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


class ResidentController:
    def __init__(self, db_url=None):
        # Usa MYSQL_URL de la variable de entorno si no se pasa db_url
        self.db_url = db_url or os.getenv("MYSQL_URL")
        if not self.db_url:
            raise ValueError("MYSQL_URL environment variable is not set.")
        self.db_client = DatabaseClient(self.db_url)

    def create_resident(self, body: ResidentModel, session=None) -> dict:

        """
        Creates a new resident in the database.

        This method verifies that the associated family, room, and shelter exist 
        and have sufficient capacity before creating a new resident. If the room is full, 
        a new room is created automatically and assigned to the family.

        Args:
            body (ResidentModel): The resident data to be added, including:
                - name (str): The first name of the resident.
                - surname (str): The last name of the resident.
                - birthDate (date): The birthdate of the resident.
                - gender (str): The gender of the resident.
                - createdBy (int): The ID of the admin who created the resident record.
                - idFamily (int): The ID of the family the resident belongs to.
            session (Session, optional): SQLAlchemy session object for database interaction.
                If not provided, a new session will be created.

        Returns:
            dict: Result of the operation.
                - {"status": "ok"}:
                If the resident is successfully created.
                - {"status": "error", "message": <error_message>}:
                If an error occurs, such as missing entities, room or shelter capacity issues, 
                or duplicate residents.

        Raises:
            Exception: If an unexpected error occurs during the operation.

        Notes:
            - If the family does not have an assigned room or the room is full, a new room is created 
            and assigned to the family.
            - The shelter and room capacities are validated to prevent exceeding their maximum limits.
        """

        if session is None:
            session = Session(self.db_client.engine)
        try:
            # Verificar si la familia existe
            family = session.query(Family).filter_by(idFamily=body.idFamily).first()
            if not family:
                return {"status": "error", "message": "The family does not exist."}

            # Verificar si la familia tiene una habitación asignada
            if not family.idRoom:
                return {"status": "error", "message": "The family does not have an assigned room."}

            # Verificar si ya existe un residente con los mismos datos
            existing_resident = session.query(Resident).filter(
                Resident.idFamily == body.idFamily,
                Resident.idRoom == family.idRoom,
                Resident.name == body.name,
                Resident.surname == body.surname,
            ).first()
            if existing_resident:
                return {"status": "error", "message": "Resident already exists in this room."}

            # Verificar si el refugio está lleno
            shelter = session.query(Shelter).filter_by(idShelter=family.idShelter).first()
            if shelter:
                current_shelter_count = session.query(Resident).filter_by(idFamily=body.idFamily).count()
                if current_shelter_count >= shelter.maxPeople:
                    return {"status": "error", "message": "Shelter is full."}

            # Verificar si la habitación está llena
            room = session.query(Room).filter_by(idRoom=family.idRoom).first()
            if room:
                current_room_count = session.query(Resident).filter_by(idRoom=family.idRoom).count()
                if current_room_count >= room.maxPeople:
                    # Buscar la última habitación cuyo nombre empieza con "Room"
                    last_room = session.query(Room).filter(Room.roomName.like("Room%")).order_by(Room.idRoom.desc()).first()

                    # Si existe alguna habitación, incrementamos el número
                    if last_room:
                        # Extraemos el número del último nombre de habitación "Room{número}"
                        last_room_number = int(last_room.roomName.replace("Room", ""))
                        new_room_number = last_room_number + 1
                    else:
                        # Si no hay habitaciones con ese nombre, empezamos con Room1
                        new_room_number = 1

                    # Crear la nueva habitación con el nombre "Room{nuevo número}" y con fecha de creación
                    new_room_name = f"Room{new_room_number}"
                    new_room = Room(
                        roomName=new_room_name,  # Nombre con el formato "Room{nuevo número}"
                        idShelter=family.idShelter,
                        maxPeople=current_room_count + 4,  # Ajusta la capacidad según sea necesario
                        createDate=date.today()  # Asignar la fecha de creación
                    )
                    session.add(new_room)
                    session.commit()  # Commit para obtener el idRoom asignado

                    # Ahora que tenemos el idRoom, podemos actualizar la familia con el nuevo idRoom
                    family.idRoom = new_room.idRoom
                    session.query(Family).filter_by(idFamily=body.idFamily).update(
                        {"idRoom": new_room.idRoom}, synchronize_session=False
                    )
                    session.commit()

            # Crear un nuevo residente
            new_resident = Resident(
                name=body.name,
                surname=body.surname,
                birthDate=body.birthDate,
                gender=body.gender,
                createdBy=body.createdBy,
                createDate=date.today(),  # Fecha de creación del residente
                idFamily=body.idFamily,
                idRoom=family.idRoom,
            )
            session.add(new_resident)
            session.commit()
            return {"status": "ok"}
        except Exception as e:
            session.rollback()
            return {"status": "error", "message": str(e)}
        finally:
            session.close()





    def delete_resident(self, idResident: int, session=None):
    
        """
        Deletes a resident entry from the database.

        This method searches for a resident by their unique ID and deletes the record if found.

        Args:
            idResident (int): The unique identifier of the resident to delete.
            session (Session, optional): SQLAlchemy session object for database interaction.
                If not provided, a new session will be created.

        Returns:
            dict: Result of the operation.
                - {"status": "ok"}:
                If the resident is successfully deleted.
                - {"status": "not found"}:
                If no resident is found with the provided ID.

        Raises:
            Exception: If an unexpected error occurs during the operation.

        Process:
            1. Check if a database session is provided; if not, create a new session.
            2. Query the database for a resident matching the provided `idResident`.
            3. If the resident exists:
                - Delete the resident record.
                - Commit the transaction to save changes.
                - Return a success status.
            4. If the resident does not exist, return a "not found" status.
        """

        if session is None:
            db = DatabaseClient(gb.MYSQL_URL)
            session = Session(db.engine)

        resident_to_delete = session.query(Resident).filter_by(idResident=idResident).first()
        if resident_to_delete:
            session.delete(resident_to_delete)
            session.commit()
            return {"status": "ok"}
        else:
            return {"status": "not found"}

    def update_resident(self, idResident: int, updates: dict, session=None):

        """
        Updates an existing resident's details in the database.

        This method searches for a resident by their unique ID and applies the specified updates 
        to the resident's record.

        Args:
            idResident (int): The unique identifier of the resident to update.
            updates (dict): A dictionary containing the fields to update and their new values.
                Example:
                    {
                        "name": "Jane",
                        "surname": "Smith",
                        "idRoom": 102,
                        "update": date(2024, 11, 14)
                    }
            session (Session, optional): SQLAlchemy session object for database interaction.
                If not provided, a new session will be created.

        Returns:
            dict: Result of the operation.
                - {"status": "ok"}:
                If the update is successful.
                - {"status": "not found"}:
                If no resident with the given ID is found.
                - {"status": "error", "message": <error_message>}:
                If an error occurs during the operation.

        Raises:
            Exception: If an unexpected error occurs during the update.

        Process:
            1. Check if a database session is provided; if not, create a new session.
            2. Query the database for a resident matching the provided `idResident`.
            3. If the resident is found:
                - Update the specified fields with the provided values.
                - Commit the changes to the database.
                - Return a success status.
            4. If the resident is not found, return a "not found" status.
        """
        if session is None:
            db = DatabaseClient(gb.MYSQL_URL)
            session = Session(db.engine)

        try:
            resident_to_update = session.query(Resident).filter_by(idResident=idResident).first()

            if not resident_to_update:
                return {"status": "not found"}

            for field, value in updates.items():
                if hasattr(resident_to_update, field):
                    setattr(resident_to_update, field, value)

            session.commit()
            
            return {"status": "ok"}
        except Exception as e:
            session.rollback()
            return {"status": "error", "message": str(e)}
        finally:
            if session is None:
                session.close()

    def list_residents_in_room(self, idRoom, session=None):
    
        """
        Lists all residents in a specific room.

        This method retrieves all residents assigned to a given room and returns their details 
        in a structured format.

        Args:
            idRoom (int): The unique identifier of the room to list residents for.
            session (Session, optional): SQLAlchemy session object for database interaction.
                If not provided, a new session will be created.

        Returns:
            dict: Result of the operation.
                - {"status": "ok", "residents": [<list_of_residents>]}:
                If residents are successfully retrieved. Each resident in the list contains:
                    - idResident (int): The unique identifier of the resident.
                    - name (str): The first name of the resident.
                    - surname (str): The last name of the resident.
                    - birthDate (str, optional): The birthdate of the resident in ISO 8601 format.
                    - gender (str): The gender of the resident.
                    - idFamily (int): The ID of the family the resident belongs to.
                    - idRoom (int): The ID of the room the resident is assigned to.
                - {"status": "ok", "residents": []}:
                If no residents are found in the specified room.
                - {"status": "error", "message": <error_message>}:
                If an error occurs during the operation.

        Raises:
            Exception: If an unexpected error occurs while querying the database.

        """
        if session is None:
            session = Session(self.db_client.engine)

        try:
            residents = session.query(Resident).filter(Resident.idRoom == idRoom).all()
            if not residents:
                return {"status": "ok", "residents": []}

            residents_data = [
                {
                    "idResident": r.idResident,
                    "name": r.name,
                    "surname": r.surname,
                    "birthDate": r.birthDate.isoformat() if r.birthDate else None,
                    "gender": r.gender,
                    "idFamily": r.idFamily,
                    "idRoom": r.idRoom
                }
                for r in residents
            ]
            return {"status": "ok", "residents": residents_data}

        except Exception as e:
            return {"status": "error", "message": str(e)}

        finally:
            if session:
                session.close()



    def list_residents(self, session=None):
        """
        Lists all residents in the database.

        This method retrieves all residents from the database and returns their details 
        in a structured format.

        Args:
            session (Session, optional): SQLAlchemy session object for database interaction.
                If not provided, a new session will be created.

        Returns:
            dict: Result of the operation.
                - {"status": "ok", "residents": [<list_of_residents>]}:
                If residents are successfully retrieved. Each resident in the list contains:
                    - idResident (int): The unique identifier of the resident.
                    - name (str): The first name of the resident.
                    - surname (str): The last name of the resident.
                    - birthDate (str, optional): The birthdate of the resident in ISO 8601 format.
                    - gender (str): The gender of the resident.
                    - idFamily (int): The ID of the family the resident belongs to.
                    - idRoom (int): The ID of the room the resident is assigned to.
                - {"status": "ok", "residents": []}:
                If no residents are found in the database.
                - {"status": "error", "message": <error_message>}:
                If an error occurs during the operation.

        Raises:
            Exception: If an unexpected error occurs while querying the database.

        """
        if session is None:
            session = Session(self.db_client.engine)

        try:
            residents = session.query(Resident).all()
            if not residents:
                return {"status": "ok", "residents": []}

            residents_data = [
                {
                    "idResident": r.idResident,
                    "name": r.name,
                    "surname": r.surname,
                    "birthDate": r.birthDate.isoformat() if r.birthDate else None,
                    "gender": r.gender,
                    "idFamily": r.idFamily,
                    "idRoom": r.idRoom
                }
                for r in residents
            ]
            return {"status": "ok", "residents": residents_data}

        except Exception as e:
            return {"status": "error", "message": str(e)}

        finally:
            if session:
                session.close()

    def login(self, name: str, surname: str, session=None):
        """
        Verifies the login credentials using the resident's name and surname.

        This method checks if a resident with the provided name and surname exists 
        in the database and returns their details if the login is successful.

        Args:
            name (str): The first name of the resident.
            surname (str): The last name of the resident.
            session (Session, optional): SQLAlchemy session object for database interaction.
                If not provided, a new session will be created.

        Returns:
            dict: Result of the operation.
                - {"status": "ok", "user": {"idResident": <id>, "name": <name>, "surname": <surname>}}:
                If the login is successful. Contains the resident's ID, name, and surname.
                - {"status": "error", "message": "Invalid credentials"}:
                If the provided credentials do not match any resident in the database.
                - {"status": "error", "message": <error_message>}:
                If an unexpected error occurs.

        Raises:
            Exception: If an unexpected error occurs during the operation.

        """
        if session is None:
            session = Session(self.db_client.engine)

        try:
            # Busca al residente en la base de datos
            user = session.query(Resident).filter(
                Resident.name == name,
                Resident.surname == surname
            ).first()

            if not user:
                return {"status": "error", "message": "Invalid credentials"}

            return {
                "status": "ok",
                "user": {
                    "idResident": user.idResident,
                    "name": user.name,
                    "surname": user.surname,
                },
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            if session:
                session.close()
    

    def updateResidentRoom(self, resident_id: int, new_room_id: int, session=None):
        """
        Updates the room ID (`idRoom`) of a specific resident.

        This method searches for a resident by their ID and assigns them to a new room 
        by updating their `idRoom` field.

        Args:
            resident_id (int): The unique identifier of the resident whose room will be updated.
            new_room_id (int): The ID of the new room to assign to the resident.
            session (Session, optional): SQLAlchemy session object for database interaction.
                If not provided, a new session will be created.

        Returns:
            dict: Result of the operation.
                - {"status": "ok", "message": "Room updated successfully."}:
                If the room is updated successfully.
                - {"status": "error", "message": <error_message>}:
                If an error occurs, such as the resident not being found or a database issue.

        Raises:
            SQLAlchemyError: If a database-related error occurs.
            Exception: If an unexpected error occurs during the operation.

        """
        if session is None:
            session = Session(self.db_client.engine)

        try:
            # Buscar el residente por su ID
            resident = session.query(Resident).filter(Resident.idResident == resident_id).first()

            if resident is None:
                return {"status": "error", "message": f"Residente con ID '{resident_id}' no encontrado"}

            # Actualizar el ID de la habitación
            resident.idRoom = new_room_id

            # Guardar los cambios
            session.commit()

            return {"status": "ok", "message": "Room updated successfully."}  # Mensaje modificado aquí

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

    def getResidentById(self, idResident: int, session=None):
        """
        Retrieves a resident by their ID.

        This method searches for a resident using their unique ID and returns their details 
        if found.

        Args:
            idResident (int): The unique identifier of the resident to retrieve.
            session (Session, optional): SQLAlchemy session object for database interaction.
                If not provided, a new session will be created.

        Returns:
            dict: Result of the operation.
                - {"status": "ok", "resident": <resident_info>}:
                If the resident is found. `resident_info` contains:
                    - idResident (int): The unique identifier of the resident.
                    - name (str): The first name of the resident.
                    - surname (str): The last name of the resident.
                    - birthDate (date): The birth date of the resident.
                    - gender (str): The gender of the resident.
                    - idFamily (int): The ID of the family the resident belongs to.
                - {"status": "error", "message": <error_message>}:
                If an error occurs or the resident is not found.

        Raises:
            Exception: If an unexpected error occurs during the operation.

        """
        if session is None:
            session = Session(self.db_client.engine)

        try:
            # Busca el residente por su idResident
            resident = session.query(Resident).filter(Resident.idResident == idResident).first()

            if resident is None:
                return {"status": "error", "message": "Residente no encontrado"}

            # Convertimos el resultado en un diccionario
            resident_info = {
                "idResident": resident.idResident,
                "name": resident.name,
                "surname": resident.surname,
                "birthDate": resident.birthDate,
                "gender": resident.gender,
                "idFamily": resident.idFamily
            }

            return {"status": "ok", "resident": resident_info}

        except Exception as e:
            # Captura cualquier excepción
            return {"status": "error", "message": str(e)}

        finally:
            # Cerramos la sesión
            if session:
                session.close()

    def updateResidentName(self, idResident: int, new_name: str, session=None):
        """
        Updates the name of a specific resident.

        This method searches for a resident by their unique ID and updates their `name` field 
        with the provided new name.

        Args:
            idResident (int): The unique identifier of the resident whose name will be updated.
            new_name (str): The new name to assign to the resident.
            session (Session, optional): SQLAlchemy session object for database interaction.
                If not provided, a new session will be created.

        Returns:
            dict: Result of the operation.
                - {"status": "ok", "message": "Name updated successfully"}:
                If the name is successfully updated.
                - {"status": "error", "message": <error_message>}:
                If an error occurs, such as the resident not being found or a database issue.

        Raises:
            SQLAlchemyError: If a database-related error occurs.
            Exception: If an unexpected error occurs during the operation.

        """
        if session is None:
            session = Session(self.db_client.engine)

        try:
            # Buscar al residente por idResident
            resident = session.query(Resident).filter(Resident.idResident == idResident).first()

            if resident is None:
                return {"status": "error", "message": "Residente no encontrado"}

            # Actualizamos el nombre del residente
            resident.name = new_name

            # Guardamos los cambios
            session.commit()

            return {"status": "ok", "message": "Nombre actualizado exitosamente"}

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




    def updateResidentSurname(self, idResident: int, new_surname: str, session=None):
        """
        Updates the surname of a specific resident.

        This method searches for a resident by their unique ID and updates their `surname` field 
        with the provided new surname.

        Args:
            idResident (int): The unique identifier of the resident whose surname will be updated.
            new_surname (str): The new surname to assign to the resident.
            session (Session, optional): SQLAlchemy session object for database interaction.
                If not provided, a new session will be created.

        Returns:
            dict: Result of the operation.
                - {"status": "ok", "message": "Surname updated successfully"}:
                If the surname is successfully updated.
                - {"status": "error", "message": <error_message>}:
                If an error occurs, such as the resident not being found or a database issue.

        Raises:
            SQLAlchemyError: If a database-related error occurs.
            Exception: If an unexpected error occurs during the operation.

        """
        if session is None:
            session = Session(self.db_client.engine)

        try:
            # Buscar al residente por idResident
            resident = session.query(Resident).filter(Resident.idResident == idResident).first()

            if resident is None:
                return {"status": "error", "message": "Residente no encontrado"}

            # Actualizamos el apellido del residente
            resident.surname = new_surname

            # Guardamos los cambios
            session.commit()

            return {"status": "ok", "message": "Apellido actualizado exitosamente"}

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


    def updateResidentBirthDate(self, idResident: int, new_birthDate: str, session=None):
        """
        Updates the birth date of a specific resident.

        This method searches for a resident by their unique ID and updates their `birthDate` field 
        with the provided new birth date.

        Args:
            idResident (int): The unique identifier of the resident whose birth date will be updated.
            new_birthDate (str): The new birth date to assign to the resident in the format 'YYYY-MM-DD'.
            session (Session, optional): SQLAlchemy session object for database interaction.
                If not provided, a new session will be created.

        Returns:
            dict: Result of the operation.
                - {"status": "ok", "message": "Birth date updated successfully"}:
                If the birth date is successfully updated.
                - {"status": "error", "message": <error_message>}:
                If an error occurs, such as the resident not being found or a database issue.

        Raises:
            SQLAlchemyError: If a database-related error occurs.
            Exception: If an unexpected error occurs during the operation.

        Notes:
            - The method automatically converts the `new_birthDate` string into a `date` object if required.
            - Ensure the `new_birthDate` is in the format 'YYYY-MM-DD' to avoid conversion errors.

        """
        if session is None:
            session = Session(self.db_client.engine)

        try:
            # Convertir el string new_birthDate a un objeto de tipo date (solo si es un string)
            if isinstance(new_birthDate, str):
                new_birthDate = datetime.strptime(new_birthDate, "%Y-%m-%d").date()

            # Buscar al residente por idResident
            resident = session.query(Resident).filter(Resident.idResident == idResident).first()

            if resident is None:
                return {"status": "error", "message": "Residente no encontrado"}

            # Actualizamos la fecha de nacimiento del residente
            resident.birthDate = new_birthDate

            # Guardamos los cambios
            session.commit()

            return {"status": "ok", "message": "Fecha de nacimiento actualizada exitosamente"}

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



    def updateResidentGender(self, idResident: int, new_gender: str, session=None):
        """
        Updates the gender of a specific resident.

        This method searches for a resident by their unique ID and updates their `gender` field 
        with the provided new gender. It validates that the new gender is one of the allowed values.

        Args:
            idResident (int): The unique identifier of the resident whose gender will be updated.
            new_gender (str): The new gender to assign to the resident. Accepted values are "M", "F", or "Otro".
            session (Session, optional): SQLAlchemy session object for database interaction.
                If not provided, a new session will be created.

        Returns:
            dict: Result of the operation.
                - {"status": "ok", "message": "Gender updated successfully"}:
                If the gender is successfully updated.
                - {"status": "error", "message": "Invalid gender. Allowed values are 'M', 'F', or 'Otro'"}:
                If the provided gender is not valid.
                - {"status": "error", "message": <error_message>}:
                If an error occurs, such as the resident not being found or a database issue.

        Raises:
            SQLAlchemyError: If a database-related error occurs.
            Exception: If an unexpected error occurs during the operation.

        Notes:
            - Valid gender values are "M", "F", or "Otro". Any other value will result in an error.
            - Ensure that the new gender conforms to these accepted values to avoid validation errors.

        """
        if session is None:
            session = Session(self.db_client.engine)

        try:
            # Verificar que el nuevo género sea válido
            if new_gender not in ["M", "F", "Otro"]:
                return {"status": "error", "message": "Género no válido. Los valores válidos son 'M', 'F' o 'Otro'."}

            # Buscar al residente por idResident
            resident = session.query(Resident).filter(Resident.idResident == idResident).first()

            if resident is None:
                return {"status": "error", "message": "Residente no encontrado"}

            # Actualizamos el género del residente
            resident.gender = new_gender

            # Guardamos los cambios
            session.commit()

            return {"status": "ok", "message": "Género actualizado exitosamente"}

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




    def getResidentRoomByNameAndSurname(self, name: str, surname: str, session=None):
        """
        Retrieves the room where a resident is located based on their name and surname.

        This method searches for a resident using their name and surname, then retrieves 
        the details of the room they are assigned to, if available.

        Args:
            name (str): The first name of the resident to search for.
            surname (str): The last name of the resident to search for.
            session (Session, optional): SQLAlchemy session object for database interaction.
                If not provided, a new session will be created.

        Returns:
            dict: Result of the operation.
                - {"status": "ok", "room": <room_info>}:
                If the resident and their room are successfully found. `room_info` contains:
                    - roomName (str): The name of the room.
                    - maxPeople (int): The maximum capacity of the room.
                    - idShelter (int): The ID of the shelter the room belongs to.
                    - createDate (datetime): The creation date of the room.
                    - createdBy (int): The ID of the admin who created the room.
                - {"status": "error", "message": "Resident not found"}:
                If the resident is not found in the database.
                - {"status": "error", "message": "Resident has no assigned room"}:
                If the resident does not have a room assigned.
                - {"status": "error", "message": "Room not found"}:
                If the room assigned to the resident does not exist in the database.
                - {"status": "error", "message": <error_message>}:
                If any other error occurs during the operation.

        Raises:
            Exception: If an unexpected error occurs during the operation.

        """
        if session is None:
            session = Session(self.db_client.engine)

        try:
            # Busca el residente por su nombre y apellido
            resident = session.query(Resident).filter(
                Resident.name == name, 
                Resident.surname == surname
            ).first()

            if resident is None:
                return {"status": "error", "message": "Residente no encontrado"}

            # Verifica si el residente tiene asignada una habitación
            if not resident.idRoom:
                return {"status": "error", "message": "Residente no tiene habitación asignada"}

            # Obtener información de la habitación
            room = session.query(Room).filter(Room.idRoom == resident.idRoom).first()

            if room is None:
                return {"status": "error", "message": "Habitación no encontrada"}

            # Convertir la información de la habitación en un diccionario
            room_info = {
                "roomName": room.roomName,
                "maxPeople": room.maxPeople,
                "idShelter": room.idShelter,
                "createDate": room.createDate,
                "createdBy": room.createdBy
            }

            return {"status": "ok", "room": room_info}

        except Exception as e:
            # Captura cualquier excepción
            return {"status": "error", "message": str(e)}

        finally:
            # Cerramos la sesión
            if session:
                session.close()

