from app.mysql.mysql import DatabaseClient
from app.mysql.admin import Admin  # SQLAlchemy model for the database
from app.models.admin import Admin as AdminModel  # Pydantic model for request validation
from sqlalchemy.orm import Session
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


class AdminController:

    def __init__(self, db_url=None):
        self.db_url = db_url or "sqlite:///:memory:"  # Asignar a un atributo de instancia
        self.db_client = DatabaseClient(self.db_url)

    def create_admin(self, admin_data: AdminModel, session=None):
        if session is None:
            session = Session(self.db_client.engine)
        try:
            existing_admin = session.query(Admin).filter_by(email=admin_data.email).first()
            if existing_admin:
                return {"status": "error", "message": "An admin with this email already exists."}

            new_admin = Admin(
                email=admin_data.email,
                name=admin_data.name,
                password=admin_data.password,
            )
            session.add(new_admin)
            session.commit()
            return {"status": "ok", "message": "Admin created successfully."}
        except Exception as e:
            session.rollback()
            return {"status": "error", "message": str(e)}
        finally:
            session.close()

