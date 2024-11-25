from app.mysql.mysql import DatabaseClient
from app.mysql.alarm import Alarm  # SQLAlchemy model for database
from app.mysql.room import Room  # SQLAlchemy model
from app.mysql.resident import Resident  # SQLAlchemy model
from app.mysql.admin import Admin  # SQLAlchemy model
from sqlalchemy.orm import Session
from app.models.alarm import Alarm as AlarmModel  # Pydantic model for validation
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

class AlarmController:

    def __init__(self, db_url=None):
        self.db_url = db_url or "sqlite:///:memory:"  # Asegurar que db_url se asigne correctamente
        self.db_client = DatabaseClient(self.db_url)

    def create_alarm(self, body: AlarmModel, session=None):
        """
        Crea una nueva alarma en la base de datos.
        """
        if session is None:
            session = Session(self.db_client.engine)

        try:
            # Validar la existencia de la habitación
            room = session.query(Room).filter(Room.idRoom == body.idRoom).first()
            if not room:
                return {"status": "error", "message": "The room does not exist."}

            # Validar la existencia del administrador
            admin = session.query(Admin).filter(Admin.idAdmin == body.idAdmin).first()
            if not admin:
                return {"status": "error", "message": "The admin does not exist."}

            # Validar la existencia del residente
            resident = session.query(Resident).filter(Resident.idResident == body.idResident).first()
            if not resident:
                return {"status": "error", "message": "The resident does not exist."}

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
                idResident=body.idResident,
                idAdmin=body.idAdmin,
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
