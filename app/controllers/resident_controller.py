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
        self.db_url = db_url or "sqlite:///:memory:"
        self.db_client = DatabaseClient(self.db_url)

    def create_resident(self, body: ResidentModel, session=None) -> dict:
        if session is None:
            session = Session(self.db_client.engine)
        try:
            family = session.query(Family).filter_by(idFamily=body.idFamily).first()
            if not family:
                return {"status": "error", "message": "The family does not exist."}

            if not family.idRoom:
                return {"status": "error", "message": "The family does not have an assigned room."}

            existing_resident = session.query(Resident).filter(
                Resident.idFamily == body.idFamily,
                Resident.idRoom == family.idRoom,
                Resident.name == body.name,
                Resident.surname == body.surname,
            ).first()
            if existing_resident:
                return {"status": "error", "message": "Resident already exists in this room."}

            shelter = session.query(Shelter).filter_by(idShelter=family.idShelter).first()
            if shelter:
                current_shelter_count = session.query(Resident).filter_by(idFamily=body.idFamily).count()
                if current_shelter_count >= shelter.maxPeople:
                    return {"status": "error", "message": "Shelter is full."}

            room = session.query(Room).filter_by(idRoom=family.idRoom).first()
            if room:
                current_room_count = session.query(Resident).filter_by(idRoom=family.idRoom).count()
                if current_room_count >= room.maxPeople:
                    new_room = session.query(Room).filter(
                        Room.maxPeople > current_room_count,
                        Room.idShelter == room.idShelter,
                    ).first()
                    if not new_room:
                        new_room = Room(
                            roomName="New Room",
                            idShelter=family.idShelter,
                            maxPeople=current_room_count + 1,
                        )
                        session.add(new_room)
                        session.commit()

                    family.idRoom = new_room.idRoom
                    session.query(Family).filter_by(idFamily=body.idFamily).update(
                        {"idRoom": new_room.idRoom}, synchronize_session=False
                    )
                    session.commit()

            new_resident = Resident(
                name=body.name,
                surname=body.surname,
                birthDate=body.birthDate,
                gender=body.gender,
                createdBy=body.createdBy,
                createDate=date.today(),
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
