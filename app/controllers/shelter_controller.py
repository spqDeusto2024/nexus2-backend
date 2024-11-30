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

    def updateShelterEnergyLevel(self, new_energy_level: int, session=None):
        """
        Actualiza el nivel de energía del único refugio disponible.

        Args:
            new_energy_level (int): El nuevo nivel de energía que se asignará al refugio.
            session (Session, optional): Sesión SQLAlchemy para interacción con la base de datos.

        Returns:
            dict: Resultado de la operación.
                - {"status": "ok", "message": "Nivel de energía actualizado exitosamente"} : Si el nivel de energía se actualiza correctamente.
                - {"status": "error", "message": <error_message>} : Si ocurre algún error.
        """
        if session is None:
            session = Session(self.db_client.engine)

        try:
            # Obtener el único refugio disponible (idShelter siempre es 1)
            shelter = session.query(Shelter).filter(Shelter.idShelter == 1).first()

            if shelter is None:
                return {"status": "error", "message": "Refugio no encontrado"}

            # Actualizamos el nivel de energía
            shelter.energyLevel = new_energy_level

            # Guardamos los cambios
            session.commit()

            return {"status": "ok", "message": "Nivel de energía actualizado exitosamente"}

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

    def updateShelterWaterLevel(self, new_water_level: int, session=None):
        if session is None:
            session = Session(self.db_client.engine)

        try:
            # Obtener el único refugio disponible (idShelter siempre es 1)
            shelter = session.query(Shelter).filter(Shelter.idShelter == 1).first()

            if shelter is None:
                return {"status": "error", "message": "Refugio no encontrado"}

            # Actualizamos el nivel de energía
            shelter.waterLevel = new_water_level

            # Guardamos los cambios
            session.commit()

            return {"status": "ok", "message": "Nivel de agua actualizado exitosamente"}

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
    
    def updateShelterRadiationLevel(self, new_radiation_level: int, session=None):
        if session is None:
            session = Session(self.db_client.engine)

        try:
            # Obtener el único refugio disponible (idShelter siempre es 1)
            shelter = session.query(Shelter).filter(Shelter.idShelter == 1).first()

            if shelter is None:
                return {"status": "error", "message": "Refugio no encontrado"}

            # Actualizamos el nivel de energía
            shelter.radiationLevel = new_radiation_level

            # Guardamos los cambios
            session.commit()

            return {"status": "ok", "message": "Nivel de radiación actualizado exitosamente"}

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



