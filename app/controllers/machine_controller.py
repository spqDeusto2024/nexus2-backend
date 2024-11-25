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


class MachineController:
    
    def __init__(self, db_url=None):
        db_url = db_url or "sqlite:///:memory:"  # Este código está mal porque se intenta asignar a sí mismo
        self.db_client = DatabaseClient(db_url)
        
    def create_machine(self, body: MachineModel, session=None):
        """
        Creates a new machine entry in the database. Ensures that the machine is assigned to an 
        existing room and that there is no other machine with the same name in the same room. 
        Prevents duplication of machines in the same room.

        Steps:
            1. Verifies if the room exists in the database.
            2. Ensures no duplication of machines with the same name in a specific room.
            3. Adds the new machine to the database and associates it with the correct room.

        Args:
            body (MachineModel): The machine data to be added to the database. This includes information such as
                                 the machine's id, name, status (on/off), room, creator, and timestamps.
            session (Session, optional): The database session to use for the transaction. If not provided, a new session
                                         will be created.

        Returns:
            dict: A dictionary indicating the result of the operation.
                - Success: {"status": "ok"}
                - Failure: {"status": "error", "message": <Error message>}
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
