from app.mysql.mysql import DatabaseClient
from app.mysql.alarm import Alarm  # SQLAlchemy model for database
from app.mysql.room import Room  # SQLAlchemy model
from app.mysql.resident import Resident  # SQLAlchemy model
from app.mysql.admin import Admin  # SQLAlchemy model
from sqlalchemy.orm import Session
from app.models.alarm import Alarm as AlarmModel  # Pydantic model for validation
import app.utils.vars as gb
from datetime import datetime
import uuid

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
from sqlalchemy.exc import SQLAlchemyError

class AlarmController:

    def __init__(self, db_url=None):
        # Usa MYSQL_URL de la variable de entorno si no se pasa db_url
        self.db_url = db_url or os.getenv("MYSQL_URL")
        if not self.db_url:
            raise ValueError("MYSQL_URL environment variable is not set.")
        self.db_client = DatabaseClient(self.db_url)

    def create_alarm(self, body: AlarmModel, session=None):
        """
        Creates a new alarm in the database.

        This method validates the existence of a room and ensures that no duplicate 
        alarms exist in the same room before creating a new alarm.

        Args:
            body (AlarmModel): An object containing the details of the alarm to be created, including:
                - idAlarm (int): The unique identifier of the alarm.
                - start (datetime): The start time of the alarm.
                - end (datetime): The end time of the alarm.
                - idRoom (int): The unique identifier of the room where the alarm is created.
                - createDate (datetime): The date when the alarm is created.
            session (Session, optional): SQLAlchemy session object for database interaction.
                If not provided, a new session will be created.

        Returns:
            dict: Result of the operation.
                - {"status": "ok"}:
                If the alarm is created successfully.
                - {"status": "error", "message": <error_message>}:
                If an error occurs, such as the room not existing or a duplicate alarm.

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

            # Verificar duplicados de alarma en la misma habitación
            existing_alarm = session.query(Alarm).filter(
                Alarm.idAlarm == body.idAlarm,
                Alarm.idRoom == body.idRoom
            ).first()
            if existing_alarm:
                return {"status": "error", "message": "Cannot create alarm, the alarm already exists in this room."}

            # Crear y agregar la nueva alarma
            new_alarm = Alarm(
                idAlarm=body.idAlarm,
                start=body.start,
                end=body.end,
                idRoom=body.idRoom,
                createDate=body.createDate
            )
            session.add(new_alarm)
            session.commit()
            return {"status": "ok"}
        except SQLAlchemyError as e:
            session.rollback()
            return {"status": "error", "message": str(e)}
        finally:
            session.close()


    def create_alarmLevel(self, body: AlarmModel, session=None):
        """
        Creates a new alarm with an automatically generated `idAlarm`.

        This method assigns the alarm to room 3 and validates its existence before creating the alarm. 
        The `idAlarm` is generated automatically by the database if the column is set as auto-increment.

        Args:
            body (AlarmModel): An object containing the details of the alarm to be created, including:
                - start (datetime): The start time of the alarm.
                - end (datetime, optional): The end time of the alarm (can be None initially).
                - createDate (datetime): The date when the alarm is created.
            session (Session, optional): SQLAlchemy session object for database interaction.
                If not provided, a new session will be created.

        Returns:
            dict: Result of the operation.
                - {"status": "ok", "message": "Alarm <idAlarm> created successfully in room 3.", "idAlarm": <idAlarm>}:
                If the alarm is created successfully. Includes the generated `idAlarm`.
                - {"status": "error", "message": <error_message>}:
                If an error occurs, such as room 3 not existing or a database issue.

        Raises:
            SQLAlchemyError: If a database-related error occurs.
            Exception: If an unexpected error occurs during the operation.
        """
        if session is None:
            session = Session(self.db_client.engine)

        try:
            # Validar si la habitación con idRoom=3 existe
            room = session.query(Room).filter(Room.idRoom == 3).first()
            if not room:
                return {"status": "error", "message": "Room with idRoom=3 does not exist."}

            # Crear la nueva alarma
            new_alarm = Alarm(
                start=body.start,
                end=body.end,  # Puede ser None inicialmente
                idRoom=3,  # Siempre se asigna a la habitación 3
                createDate=body.createDate
            )
            
            # Agregar y guardar la alarma en la base de datos
            session.add(new_alarm)
            session.commit()  # Aquí el idAlarm se genera automáticamente si es auto-incremento
            
            # Obtener el idAlarm generado
            return {"status": "ok", "message": f"Alarm {new_alarm.idAlarm} created successfully in room 3.", "idAlarm": new_alarm.idAlarm}
        
        except SQLAlchemyError as e:
            session.rollback()
            return {"status": "error", "message": str(e)}
        finally:
            session.close()


    def updateAlarmEndDate(self, idAlarm: int, new_enddate: datetime, session=None):

        """
        Updates the end date of an alarm.

        This method searches for an alarm by its ID and updates its `enddate` field 
        to the specified new value.

        Args:
            idAlarm (int): The unique identifier of the alarm to update.
            new_enddate (datetime): The new end date to assign to the alarm.
            session (Session, optional): SQLAlchemy session object for database interaction.
                If not provided, a new session will be created.

        Returns:
            dict: Result of the operation.
                - {"status": "ok", "message": "Alarm end date updated successfully"}:
                If the end date is updated successfully.
                - {"status": "error", "message": <error_message>}:
                If an error occurs or the alarm is not found.

        Raises:
            SQLAlchemyError: If a database-related error occurs.
            Exception: If an unexpected error occurs during the operation.
        """

        if session is None:
            session = Session(self.db_client.engine)

        try:
            # Buscar la alarma con el id especificado
            alarm = session.query(Alarm).filter(Alarm.idAlarm == idAlarm).first()

            if alarm is None:
                return {"status": "error", "message": "Alarma no encontrada"}

            # Actualizamos el campo enddate
            alarm.enddate = new_enddate

            # Guardamos los cambios
            session.commit()

            return {"status": "ok", "message": "Fecha de fin de alarma actualizada exitosamente"}

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
    

    def list_alarms(self, session=None):
        """
        Lists all alarms in the database.

        This method retrieves all alarms from the database and returns their details 
        as a list of dictionaries.

        Args:
            session (Session, optional): SQLAlchemy session object for database interaction.
                If not provided, a new session will be created.

        Returns:
            dict: Result of the operation.
                - {"status": "ok", "alarms": [<list_of_alarms>]}:
                If the alarms are successfully retrieved. Each alarm in the list contains:
                    - idAlarm (int): The unique identifier of the alarm.
                    - start (str, optional): The start time of the alarm in ISO 8601 format.
                    - end (str, optional): The end time of the alarm in ISO 8601 format.
                    - idRoom (int): The unique identifier of the room associated with the alarm.
                    - createDate (str, optional): The creation date of the alarm in ISO 8601 format.
                - {"status": "ok", "alarms": []}:
                If no alarms are found in the database.
                - {"status": "error", "message": <error_message>}:
                If an error occurs during the operation.

        Raises:
            Exception: If an unexpected error occurs while querying the database.
        """
        if session is None:
            session = Session(self.db_client.engine)

        try:
            # Obtener todas las alarmas de la base de datos
            alarms = session.query(Alarm).all()
            
            if not alarms:
                return {"status": "ok", "alarms": []}

            alarms_data = [
                {
                    "idAlarm": alarm.idAlarm,
                    "start": alarm.start.isoformat() if alarm.start else None,
                    "end": alarm.end.isoformat() if alarm.end else None,
                    "idRoom": alarm.idRoom,
                    "createDate": alarm.createDate.isoformat() if alarm.createDate else None
                }
                for alarm in alarms
            ]
            
            return {"status": "ok", "alarms": alarms_data}

        except Exception as e:
            return {"status": "error", "message": str(e)}

        finally:
            if session:
                session.close()
