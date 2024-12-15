from app.mysql.mysql import DatabaseClient
from app.mysql.machine import Machine  # SQLAlchemy model
from app.mysql.room import Room  # SQLAlchemy model
from app.mysql.admin import Admin  # SQLAlchemy model
from app.models.machine import Machine as MachineModel  # Pydantic model
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


from datetime import date
import app.utils.vars as gb
from sqlalchemy.orm import Session
from sqlalchemy import func
import os

class MachineController:
    
    def __init__(self, db_url=None):
        # Usa MYSQL_URL de la variable de entorno si no se pasa db_url
        self.db_url = db_url or os.getenv("MYSQL_URL")
        if not self.db_url:
            raise ValueError("MYSQL_URL environment variable is not set.")
        self.db_client = DatabaseClient(self.db_url)
    
    
    def create_machine(self, body: MachineModel, session=None):
        """
        Creates a new machine entry in the database.

        This method ensures the following:
        - The machine is assigned to an existing room.
        - No other machine with the same name exists in the same room.
        - Prevents duplication of machines within the same room.

        Args:
            body (MachineModel): The data of the machine to be added, including:
                - idMachine (int): The unique identifier of the machine.
                - machineName (str): The name of the machine.
                - on (bool): The initial status of the machine (on/off).
                - idRoom (int): The ID of the room where the machine is located.
                - createdBy (int): The ID of the admin who created the machine.
                - createDate (datetime): The creation timestamp of the machine.
                - update (datetime): The last update timestamp of the machine.
            session (Session, optional): SQLAlchemy session object for database interaction.
                If not provided, a new session will be created.

        Returns:
            dict: Result of the operation.
                - {"status": "ok"}:
                If the machine is created successfully.
                - {"status": "error", "message": <error_message>}:
                If an error occurs, such as the room or admin not existing, 
                or a duplicate machine name in the same room.

        Raises:
            SQLAlchemyError: If a database-related error occurs.
            Exception: If an unexpected error occurs during the operation.
        """
        if session is None:
            db = DatabaseClient(gb.MYSQL_URL)
            session = Session(db.engine)

        try:
            # Check if the room exists
            room = session.query(Room).filter(Room.idRoom == body.idRoom).first()
            if not room:
                return {"status": "error", "message": "The room does not exist."}

            # Check if the admin exists
            admin = session.query(Admin).filter(Admin.idAdmin == body.createdBy).first()
            if not admin:
                return {"status": "error", "message": "The admin does not exist."}

            # Check for duplicate machine in the same room
            existing_machine = session.query(Machine).filter(
                Machine.machineName == body.machineName,
                Machine.idRoom == body.idRoom
            ).first()
            if existing_machine:
                return {"status": "error", "message": "A machine with the same name already exists in this room."}

            # Create and add the new machine
            new_machine = Machine(
                idMachine=body.idMachine,
                machineName=body.machineName,
                on=True,
                idRoom=body.idRoom,
                createdBy=body.createdBy,
                createDate=body.createDate,
                update=body.update
            )

            session.add(new_machine)
            session.commit()

            return {"status": "ok"}
        except SQLAlchemyError as e:
            session.rollback()
            return {"status": "error", "message": str(e)}
        finally:
            if session is None:
                session.close()

    def updateMachineStatus(self, machine_name: str, session=None):
        """
        Updates the status of a specific machine to `False`.

        This method searches for a machine by its name and sets its `on` status to `False` 
        to indicate that the machine is turned off.

        Args:
            machine_name (str): The name of the machine to update.
            session (Session, optional): SQLAlchemy session object for database interaction.
                If not provided, a new session will be created.

        Returns:
            dict: Result of the operation.
                - {"status": "ok", "message": "Machine status updated successfully"}:
                If the machine's status is updated successfully.
                - {"status": "error", "message": <error_message>}:
                If an error occurs, such as the machine not being found or a database issue.

        Raises:
            SQLAlchemyError: If a database-related error occurs.
            Exception: If an unexpected error occurs during the operation.
        """
        if session is None:
            session = Session(self.db_client.engine)

        try:
            # Buscar la máquina por su nombre
            machine = session.query(Machine).filter(Machine.machineName == machine_name).first()

            if machine is None:
                return {"status": "error", "message": f"Máquina '{machine_name}' no encontrada"}

            # Actualizar el estado de 'on' a False
            machine.on = False

            # Guardar los cambios
            session.commit()

            return {"status": "ok", "message": f"Estado de la máquina '{machine_name}' actualizado a False"}

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
    
    def updateMachineStatusOn(self, machine_name: str, session=None):
        """
        Updates the status of a machine to "on" (True).

        This method searches for a machine by its name in the database, updates its `on` 
        status to `True`, and commits the change. If the machine is not found or if an error 
        occurs during the operation, an appropriate error message is returned.

        Args:
            machine_name (str): The name of the machine to update.
            session (Session, optional): SQLAlchemy session object for database interaction.
                If not provided, a new session will be created.

        Returns:
            dict: Result of the operation.
                - {"status": "ok", "message": <success_message>}:
                    If the machine's status is successfully updated. For example:
                    {"status": "ok", "message": "Machine 'MachineName' status updated to True"}.
                - {"status": "error", "message": "Machine '<machine_name>' not found"}:
                    If the specified machine does not exist in the database.
                - {"status": "error", "message": "Database error: <error_message>"}:
                    If an SQLAlchemy error occurs during the operation.
                - {"status": "error", "message": <error_message>}:
                    If any other unexpected error occurs during the operation.

        Raises:
            SQLAlchemyError: If a database-specific error occurs.
            Exception: For any other unexpected errors during execution.

        Notes:
            - The `machine_name` must match exactly with the `machineName` field in the database.
            - If the machine is not found, no changes will be made, and an error message will be returned.
            - The session is closed automatically after the operation, regardless of success or failure.
        """
        if session is None:
            session = Session(self.db_client.engine)

        try:
            # Buscar la máquina por su nombre
            machine = session.query(Machine).filter(Machine.machineName == machine_name).first()

            if machine is None:
                return {"status": "error", "message": f"Máquina '{machine_name}' no encontrada"}

            # Actualizar el estado de 'on' a False
            machine.on = True

            # Guardar los cambios
            session.commit()

            return {"status": "ok", "message": f"Estado de la máquina '{machine_name}' actualizado a True"}

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
            
    def list_machines(self, session=None):
        """
        Lists all machines in the database.

        This method retrieves all machines from the database and formats their details 
        into a list of dictionaries.

        Args:
            session (Session, optional): SQLAlchemy session object for database interaction.
                If not provided, a new session will be created.

        Returns:
            dict: Result of the operation.
                - {"status": "ok", "machines": [<list_of_machines>]}:
                If the machines are successfully retrieved. Each machine in the list contains:
                    - idMachine (int): The unique identifier of the machine.
                    - machineName (str): The name of the machine.
                    - on (bool): The current status of the machine (True for on, False for off).
                    - idRoom (int): The unique identifier of the room where the machine is located.
                    - createdBy (int): The ID of the admin who created the machine.
                    - createDate (str, optional): The creation date of the machine, in ISO 8601 format.
                    - update (str, optional): The last update timestamp of the machine, in ISO 8601 format.
                - {"status": "ok", "machines": []}:
                If no machines are found in the database.
                - {"status": "error", "message": <error_message>}:
                If an error occurs during the operation.

        Raises:
            Exception: If an unexpected error occurs while querying the database.
        """
        if session is None:
            session = Session(self.db_client.engine)

        try:
            # Obtener todas las máquinas de la base de datos
            machines = session.query(Machine).all()

            if not machines:
                return {"status": "ok", "machines": []}

            machines_data = [
                {
                    "idMachine": machine.idMachine,
                    "machineName": machine.machineName,
                    "on": machine.on,
                    "idRoom": machine.idRoom,
                    "createdBy": machine.createdBy,
                    "createDate": machine.createDate.isoformat() if machine.createDate else None,
                    "update": machine.update.isoformat() if machine.update else None
                }
                for machine in machines
            ]
            
            return {"status": "ok", "machines": machines_data}

        except Exception as e:
            return {"status": "error", "message": str(e)}

        finally:
            if session:
                session.close()


  
    def deleteMachine(self, machine_id: int, session=None):
        """
        Deletes a machine from the database using its ID.

        This method searches for a machine by its unique ID and deletes it if found.

        Args:
            machine_id (int): The unique identifier of the machine to delete.
            session (Session, optional): SQLAlchemy session object for database interaction.
                If not provided, a new session will be created.

        Returns:
            dict: Result of the operation.
                - {"status": "ok", "message": "Machine deleted successfully"}:
                If the machine is successfully deleted.
                - {"status": "error", "message": <error_message>}:
                If an error occurs, such as the machine not being found.

        Raises:
            Exception: If an unexpected error occurs during the operation.
        """
        if session is None:
            session = Session(self.db_client.engine)

        try:
            # Busca la máquina en la base de datos por ID
            machine = session.query(Machine).filter(Machine.idMachine == machine_id).first()

            # Verificamos si no se encontró la máquina
            if not machine:
                return {"status": "error", "message": "Machine not found"}

            # Eliminamos la máquina
            session.delete(machine)
            session.commit()

            return {"status": "ok", "message": "Machine deleted successfully"}

        except Exception as e:
            # Aquí se captura cualquier otra excepción que pueda ocurrir
            session.rollback()  # Deshacemos cualquier cambio en caso de error
            return {"status": "error", "message": str(e)}

        finally:
            # Asegúrate de cerrar la sesión para evitar problemas de conexiones abiertas
            if session:
                session.close()


    def updateMachineDate(self, machine_name: str, session=None):
        """
        Updates the `update` field of a specific machine with the current date.

        This method searches for a machine by its name and updates its `update` field 
        to the current date.

        Args:
            machine_name (str): The name of the machine to update.
            session (Session, optional): SQLAlchemy session object for database interaction.
                If not provided, a new session will be created.

        Returns:
            dict: Result of the operation.
                - {"status": "ok", "message": "Machine date updated successfully"}:
                If the machine's date is updated successfully.
                - {"status": "error", "message": <error_message>}:
                If an error occurs, such as the machine not being found.

        Raises:
            SQLAlchemyError: If a database-related error occurs.
            Exception: If an unexpected error occurs during the operation.
        """
        if session is None:
            session = Session(self.db_client.engine)

        try:
            # Buscar la máquina por su nombre
            machine = session.query(Machine).filter(Machine.machineName == machine_name).first()

            if machine is None:
                return {"status": "error", "message": f"Máquina '{machine_name}' no encontrada"}

            # Actualizar el campo 'update' con la fecha actual
            machine.update = date.today()  # Utiliza 'date.today()' para obtener solo la fecha actual

            # Guardar los cambios
            session.commit()

            return {"status": "ok", "message": f"Fecha de la máquina '{machine_name}' actualizada exitosamente"}

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
