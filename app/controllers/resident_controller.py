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

        Parameters:
            idResident (int): 
                The unique identifier of the resident to delete.

        Returns:
            dict:
                A dictionary indicating the outcome of the operation:
                - `{"status": "ok"}`: The resident was successfully deleted.
                - `{"status": "not found"}`: No resident was found with the given ID.

        Process:
            1. Check if an existing database session is provided; if not, create a new session.
            2. Query the database for a resident record matching the provided `idResident`.
            3. If the resident exists:
                a. Delete the resident record.
                b. Commit the transaction to save changes.
                c. Return a success status.
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

        Parameters:
            idResident (int): The unique identifier of the resident to update.
            updates (dict): A dictionary containing the fields to update and their new values.
                Example:
                    {
                        "name": "Jane",
                        "surname": "Smith",
                        "idRoom": 102,
                        "update": date(2024, 11, 14)
                    }

        Returns:
            dict: A status dictionary indicating the result of the update.
                - `{"status": "ok"}` if the update was successful.
                - `{"status": "not found"}` if no resident with the given ID was found.
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
        List all residents in a specific room.

        Args:
            idRoom (int): The ID of the room to list residents for.
            session (Session, optional): SQLAlchemy session for database interaction.

        Returns:
            dict: A dictionary with the list of residents in the room or an error message.
                - {"status": "ok", "residents": [list of residents]}
                - {"status": "error", "message": <error message>}
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
        List all residents in the database.

        Args:
            session (Session, optional): SQLAlchemy session for database interaction.

        Returns:
            dict: A dictionary with the list of all residents or an error message.
                - {"status": "ok", "residents": [list of residents]}
                - {"status": "error", "message": <error message>}
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
        Verifica las credenciales de login usando el nombre y apellido del residente.

        Args:
            name (str): Nombre del residente.
            surname (str): Apellido del residente.
            session (Session, optional): Sesión SQLAlchemy para interacción con la base de datos.

        Returns:
            dict: Resultado del login.
                - {"status": "ok", "user": {id, name, surname}}: Si el login es exitoso.
                - {"status": "error", "message": <error_message>}: Si ocurre algún error.
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
        Actualiza el ID de la habitación (idRoom) de un residente específico.

        Args:
            resident_id (int): El ID del residente cuyo idRoom se actualizará.
            new_room_id (int): El nuevo ID de la habitación que se asignará al residente.
            session (Session, optional): Sesión SQLAlchemy para interacción con la base de datos.

        Returns:
            dict: Resultado de la operación.
                - {"status": "ok", "message": "Room updated successfully."} : Si se actualiza correctamente.
                - {"status": "error", "message": <error_message>} : Si ocurre algún error.
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
        Obtiene un residente por su ID.

        Args:
            idResident (int): El ID del residente que se busca.
            session (Session, optional): Sesión SQLAlchemy para interacción con la base de datos.

        Returns:
            dict: Resultado de la operación.
                - {"status": "ok", "resident": <resident_info>} : Si se encuentra el residente.
                - {"status": "error", "message": <error_message>} : Si ocurre algún error o el residente no se encuentra.
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
        Actualiza el nombre de un residente.

        Args:
            idResident (int): El ID del residente cuyo nombre se va a actualizar.
            new_name (str): El nuevo nombre que se asignará al residente.
            session (Session, optional): Sesión SQLAlchemy para interacción con la base de datos.

        Returns:
            dict: Resultado de la operación.
                - {"status": "ok", "message": "Nombre actualizado exitosamente"} : Si el nombre se actualiza correctamente.
                - {"status": "error", "message": <error_message>} : Si ocurre algún error.
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
        Actualiza el apellido de un residente.

        Args:
            idResident (int): El ID del residente cuyo apellido se va a actualizar.
            new_surname (str): El nuevo apellido que se asignará al residente.
            session (Session, optional): Sesión SQLAlchemy para interacción con la base de datos.

        Returns:
            dict: Resultado de la operación.
                - {"status": "ok", "message": "Apellido actualizado exitosamente"} : Si el apellido se actualiza correctamente.
                - {"status": "error", "message": <error_message>} : Si ocurre algún error.
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
        Actualiza la fecha de nacimiento de un residente.

        Args:
            idResident (int): El ID del residente cuya fecha de nacimiento se va a actualizar.
            new_birthDate (str): La nueva fecha de nacimiento que se asignará al residente (formato 'YYYY-MM-DD').
            session (Session, optional): Sesión SQLAlchemy para interacción con la base de datos.

        Returns:
            dict: Resultado de la operación.
                - {"status": "ok", "message": "Fecha de nacimiento actualizada exitosamente"} : Si la fecha se actualiza correctamente.
                - {"status": "error", "message": <error_message>} : Si ocurre algún error.
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
        Actualiza el género de un residente.

        Args:
            idResident (int): El ID del residente cuyo género se va a actualizar.
            new_gender (str): El nuevo género que se asignará al residente ("M", "F", "Otro").
            session (Session, optional): Sesión SQLAlchemy para interacción con la base de datos.

        Returns:
            dict: Resultado de la operación.
                - {"status": "ok", "message": "Género actualizado exitosamente"} : Si el género se actualiza correctamente.
                - {"status": "error", "message": <error_message>} : Si ocurre algún error.
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
