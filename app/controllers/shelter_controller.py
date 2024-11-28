from app.mysql.mysql import DatabaseClient
from app.mysql.shelter import Shelter
from sqlalchemy.orm import Session
from datetime import date
import app.utils.vars as gb
import os

class ShelterController:
    def __init__(self, db_url=None):
        # Usa MYSQL_URL de la variable de entorno si no se pasa db_url
        self.db_url = db_url or os.getenv("MYSQL_URL")
        if not self.db_url:
            raise ValueError("MYSQL_URL environment variable is not set.")
        self.db_client = DatabaseClient(self.db_url)

    def get_shelter_energy_level(self, session=None):
        if session is None:
            session = Session(self.db_client.engine)
        try:
            shelter = session.query(Shelter).first()
            if not shelter:
                raise ValueError("No shelter found in the database.")
            return {"energyLevel": shelter.energyLevel}
        finally:
            session.close()

    def get_shelter_water_level(self, session=None):
        if session is None:
            session = Session(self.db_client.engine)
        try:
            shelter = session.query(Shelter).first()
            if not shelter:
                raise ValueError("No shelter found in the database.")
            return {"waterLevel": shelter.waterLevel}
        finally:
            session.close()

    def get_shelter_radiation_level(self, session=None):
        if session is None:
            session = Session(self.db_client.engine)
        try:
            shelter = session.query(Shelter).first()
            if not shelter:
                raise ValueError("No shelter found in the database.")
            return {"radiationLevel": shelter.radiationLevel}
        finally:
            session.close()
