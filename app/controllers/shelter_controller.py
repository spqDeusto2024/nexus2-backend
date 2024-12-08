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

        """
        Retrieves the energy level of the first shelter in the database.

        This method fetches the energy level of the first shelter record found in the database. 
        If no shelter is found, an error is raised.

        Args:
            session (Session, optional): SQLAlchemy session object for database interaction.
                If not provided, a new session will be created.

        Returns:
            dict: A dictionary containing the energy level of the shelter:
                - {"energyLevel": <energy_level>}:
                Where `<energy_level>` is the current energy level of the shelter.

        Raises:
            ValueError: If no shelter record is found in the database.
            Exception: If an unexpected error occurs during the operation.

        Example Response:
            {"energyLevel": 85}

        Notes:
            - This method assumes there is only one shelter or that the first shelter 
            record is the one of interest.
        """

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

        """
        Retrieves the water level of the first shelter in the database.

        This method fetches the water level of the first shelter record found in the database. 
        If no shelter is found, an error is raised.

        Args:
            session (Session, optional): SQLAlchemy session object for database interaction.
                If not provided, a new session will be created.

        Returns:
            dict: A dictionary containing the water level of the shelter:
                - {"waterLevel": <water_level>}:
                Where `<water_level>` is the current water level of the shelter.

        Raises:
            ValueError: If no shelter record is found in the database.
            Exception: If an unexpected error occurs during the operation.

        Example Response:
            {"waterLevel": 70}

        Notes:
            - This method assumes there is only one shelter or that the first shelter 
            record is the one of interest.
        """

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

        """
        Retrieves the radiation level of the first shelter in the database.

        This method fetches the radiation level of the first shelter record found in the database. 
        If no shelter is found, an error is raised.

        Args:
            session (Session, optional): SQLAlchemy session object for database interaction.
                If not provided, a new session will be created.

        Returns:
            dict: A dictionary containing the radiation level of the shelter:
                - {"radiationLevel": <radiation_level>}:
                Where `<radiation_level>` is the current radiation level of the shelter.

        Raises:
            ValueError: If no shelter record is found in the database.
            Exception: If an unexpected error occurs during the operation.

        Example Response:
            {"radiationLevel": 15}

        Notes:
            - This method assumes there is only one shelter or that the first shelter 
            record is the one of interest.
        """

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
        Updates the energy level of the only available shelter.

        This method retrieves the shelter record with a fixed ID (assumed to be 1) and updates 
        its energy level to the provided value.

        Args:
            new_energy_level (int): The new energy level to assign to the shelter.
            session (Session, optional): SQLAlchemy session object for database interaction.
                If not provided, a new session will be created.

        Returns:
            dict: Result of the operation.
                - {"status": "ok", "message": "Energy level updated successfully"}:
                If the energy level is successfully updated.
                - {"status": "error", "message": "Shelter not found"}:
                If no shelter with the given ID is found in the database.
                - {"status": "error", "message": <error_message>}:
                If an error occurs during the operation.

        Raises:
            SQLAlchemyError: If a database-related error occurs.
            Exception: If an unexpected error occurs during the operation.

        Notes:
            - This method assumes there is only one shelter in the system with `idShelter = 1`.
            - Ensure that the `new_energy_level` value is within the acceptable range defined by your application logic.

        Example Response:
            {"status": "ok", "message": "Energy level updated successfully"}
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

        """
        Updates the water level of the only available shelter.

        This method retrieves the shelter record with a fixed ID (assumed to be 1) and updates 
        its water level to the provided value.

        Args:
            new_water_level (int): The new water level to assign to the shelter.
            session (Session, optional): SQLAlchemy session object for database interaction.
                If not provided, a new session will be created.

        Returns:
            dict: Result of the operation.
                - {"status": "ok", "message": "Water level updated successfully"}:
                If the water level is successfully updated.
                - {"status": "error", "message": "Shelter not found"}:
                If no shelter with the given ID is found in the database.
                - {"status": "error", "message": <error_message>}:
                If an error occurs during the operation.

        Raises:
            SQLAlchemyError: If a database-related error occurs.
            Exception: If an unexpected error occurs during the operation.

        Notes:
            - This method assumes there is only one shelter in the system with `idShelter = 1`.
            - Ensure that the `new_water_level` value is within the acceptable range defined by your application logic.

        Example Response:
            {"status": "ok", "message": "Water level updated successfully"}
        """

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

        """
        Updates the radiation level of the only available shelter.

        This method retrieves the shelter record with a fixed ID (assumed to be 1) and updates 
        its radiation level to the provided value.

        Args:
            new_radiation_level (int): The new radiation level to assign to the shelter.
            session (Session, optional): SQLAlchemy session object for database interaction.
                If not provided, a new session will be created.

        Returns:
            dict: Result of the operation.
                - {"status": "ok", "message": "Radiation level updated successfully"}:
                If the radiation level is successfully updated.
                - {"status": "error", "message": "Shelter not found"}:
                If no shelter with the given ID is found in the database.
                - {"status": "error", "message": <error_message>}:
                If an error occurs during the operation.

        Raises:
            SQLAlchemyError: If a database-related error occurs.
            Exception: If an unexpected error occurs during the operation.

        Notes:
            - This method assumes there is only one shelter in the system with `idShelter = 1`.
            - Ensure that the `new_radiation_level` value is within the acceptable range defined by your application logic.

        Example Response:
            {"status": "ok", "message": "Radiation level updated successfully"}
        """

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



