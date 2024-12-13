from app.mysql.mysql import DatabaseClient
from app.mysql.admin import Admin  # SQLAlchemy model for the database
from app.models.admin import Admin as AdminModel  # Pydantic model for request validation
from sqlalchemy.orm import Session
import app.utils.vars as gb
from fastapi import HTTPException
import jwt
from datetime import datetime, timedelta

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
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
import os

class AdminController:

    def __init__(self, db_url=None):
        # Usa MYSQL_URL de la variable de entorno si no se pasa db_url
        self.db_url = db_url or os.getenv("MYSQL_URL")
        if not self.db_url:
            raise ValueError("MYSQL_URL environment variable is not set.")
        self.db_client = DatabaseClient(self.db_url)

    

    def create_admin(self, admin_data: AdminModel, session=None):
        """
        Creates a new admin in the system.

        This method checks if an admin with the provided email already exists. 
        If not, it creates a new admin record in the database with the provided details.

        Args:
            admin_data (AdminModel): An object containing the admin's details, including:
                - email (str): The admin's email address.
                - name (str): The admin's name.
                - password (str): The admin's hashed password.
            session (Session, optional): SQLAlchemy session object for database interaction.
                If not provided, a new session will be created.

        Returns:
            dict: Result of the operation.
                - {"status": "ok", "message": "Admin created successfully."} if the admin is created successfully.
                - {"status": "error", "message": <error_message>} if there is an error, such as an existing email or a database issue.

        Raises:
            Exception: If any unexpected error occurs during the creation process.

        """
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



    def loginAdmin(self, email: str, password: str, session=None):
        """
        Verifies the login credentials of an admin using their email and password.

        Args:
            email (str): The admin's email address.
            password (str): The admin's plain text password.
            session (Session, optional): SQLAlchemy session object for database interaction.

        Returns:
            dict: Result of the login attempt.
                - {"status": "ok", "token": <JWT token>, "user": {"idAdmin": <idAdmin>, "email": <email>}}: 
                If the login is successful.
                - {"status": "error", "message": <error_message>}: 
                If an error occurs or the credentials are invalid.
        """
        SECRET_KEY = "nexus2" 
        if session is None:
            session = Session(self.db_client.engine)

        try:
            # Busca al administrador en la base de datos por email
            user = session.query(Admin).filter(Admin.email == email).first()

            # Verificamos si no se encontró el usuario
            if not user:
                return {"status": "error", "message": "Invalid credentials"}

            # Compara la contraseña sin hash
            if user.password != password:
                return {"status": "error", "message": "Invalid credentials"}

            # Generar el JWT token
            payload = {
                "idAdmin": user.idAdmin,  # ID del admin
                "email": user.email,      # Email del admin
                "exp": datetime.utcnow() + timedelta(hours=1)  # Expira en 1 hora
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

            return {
                "status": "ok",
                "token": token,  # El JWT token generado
                "user": {
                    "idAdmin": user.idAdmin,
                    "email": user.email,
                },
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

        finally:
            if session:
                session.close()

    def deleteAdmin(self, admin_id: int, session=None):
        """
        Deletes an admin from the database using their ID.

        This method looks up an admin in the database by their unique ID and deletes 
        the corresponding record if it exists.

        Args:
            admin_id (int): The unique identifier of the admin to delete.
            session (Session, optional): SQLAlchemy session object for database interaction.
                If not provided, a new session will be created.

        Returns:
            dict: Result of the operation.
                - {"status": "ok", "message": "Admin deleted successfully"}:
                If the admin is successfully deleted.
                - {"status": "error", "message": <error_message>}:
                If an error occurs or the admin is not found.

        Raises:
            Exception: If an unexpected error occurs during the deletion process.

        """
        if session is None:
            session = Session(self.db_client.engine)

        try:
            # Busca al administrador en la base de datos por ID
            user = session.query(Admin).filter(Admin.idAdmin == admin_id).first()

            # Verificamos si no se encontró el administrador
            if not user:
                return {"status": "error", "message": "Admin not found"}

            # Eliminamos al administrador
            session.delete(user)
            session.commit()

            return {"status": "ok", "message": "Admin deleted successfully"}

        except Exception as e:
            # Aquí se captura cualquier otra excepción que pueda ocurrir
            session.rollback()  # Deshacemos cualquier cambio en caso de error
            return {"status": "error", "message": str(e)}

        finally:
            # Asegúrate de cerrar la sesión para evitar problemas de conexiones abiertas
            if session:
                session.close()




    def listAdmins(self, session=None):
        
        """
        Lists all admins registered in the database.

        This method retrieves all admin records from the database and formats them 
        into a list of dictionaries containing their ID and email.

        Args:
            session (Session, optional): SQLAlchemy session object for database interaction.
                If not provided, a new session will be created.

        Returns:
            dict: Result of the operation.
                - {"status": "ok", "admins": [<list_of_admins>]}:
                If the admins are successfully retrieved. Each admin in the list contains:
                    - idAdmin (int): The unique identifier of the admin.
                    - email (str): The email address of the admin.
                - {"status": "error", "message": <error_message>}:
                If an error occurs during the operation.

        Raises:
            Exception: If an unexpected error occurs while querying the database.
        """
        if session is None:
            session = Session(self.db_client.engine)

        try:
            # Consulta todos los administradores
            admins = session.query(Admin).all()

            # Convertimos el resultado en una lista de diccionarios
            admins_list = [
                {"idAdmin": admin.idAdmin, "email": admin.email}
                for admin in admins
            ]

            return {"status": "ok", "admins": admins_list}

        except Exception as e:
            # Captura cualquier excepción
            return {"status": "error", "message": str(e)}

        finally:
            # Cerramos la sesión
            if session:
                session.close()



    def getAdminById(self, idAdmin: int, session=None):
        """
        Retrieves an admin by their ID.

        This method queries the database for an admin with the specified ID and 
        returns their details if found.

        Args:
            idAdmin (int): The unique identifier of the admin to retrieve.
            session (Session, optional): SQLAlchemy session object for database interaction.
                If not provided, a new session will be created.

        Returns:
            dict: Result of the operation.
                - {"status": "ok", "admin": <admin_info>}:
                If the admin is found. `admin_info` contains:
                    - idAdmin (int): The unique identifier of the admin.
                    - email (str): The admin's email address.
                    - name (str): The admin's name.
                    - password (str): The admin's hashed password.
                - {"status": "error", "message": <error_message>}:
                If an error occurs or the admin is not found.

        Raises:
            Exception: If an unexpected error occurs while querying the database.
        """
        if session is None:
            session = Session(self.db_client.engine)

        try:
            # Busca el administrador por su idAdmin
            admin = session.query(Admin).filter(Admin.idAdmin == idAdmin).first()

            if admin is None:
                return {"status": "error", "message": "Administrador no encontrado"}

            # Convertimos el resultado en un diccionario
            admin_info = {
                "idAdmin": admin.idAdmin,
                "email": admin.email,
                "name": admin.name,
                "password": admin.password
            }

            return {"status": "ok", "admin": admin_info}

        except Exception as e:
            # Captura cualquier excepción
            return {"status": "error", "message": str(e)}

        finally:
            # Cerramos la sesión
            if session:
                session.close()

    
    def refreshAccessToken(self, refresh_token: str):
        SECRET_KEY = "nexus2"
        REFRESH_SECRET_KEY = "nexus2"

        try:
            payload = jwt.decode(refresh_token, REFRESH_SECRET_KEY, algorithms=["HS256"])
            new_access_token = jwt.encode(
                {
                    "idAdmin": payload["idAdmin"],
                    "email": payload["email"],
                    "exp": datetime.utcnow() + timedelta(hours=1),
                },
                SECRET_KEY,
                algorithm="HS256",
            )
            return {"status": "ok", "accessToken": new_access_token}
        except jwt.ExpiredSignatureError:
            return {"status": "error", "message": "Refresh token has expired"}
        except jwt.InvalidTokenError:
            return {"status": "error", "message": "Invalid refresh token"}




    def updateAdminPassword(self, idAdmin: int, new_password: str, session=None):
        """
        Updates the password of an admin.

        This method searches for an admin by their ID and updates their password to the provided new value.

        Args:
            idAdmin (int): The unique identifier of the admin whose password will be updated.
            new_password (str): The new password to assign to the admin.
            session (Session, optional): SQLAlchemy session object for database interaction.
                If not provided, a new session will be created.

        Returns:
            dict: Result of the operation.
                - {"status": "ok", "message": "Password updated successfully"}:
                If the password is updated successfully.
                - {"status": "error", "message": <error_message>}:
                If an error occurs or the admin is not found.

        Raises:
            SQLAlchemyError: If a database-related error occurs.
            Exception: If an unexpected error occurs during the operation.
        """
        if session is None:
            session = Session(self.db_client.engine)

        try:
            # Buscar al administrador por idAdmin
            admin = session.query(Admin).filter(Admin.idAdmin == idAdmin).first()

            if admin is None:
                return {"status": "error", "message": "Administrador no encontrado"}

            # Actualizamos la contraseña
            admin.password = new_password

            # Guardamos los cambios
            session.commit()

            return {"status": "ok", "message": "Contraseña actualizada exitosamente"}

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
    


    def updateAdminEmail(self, idAdmin: int, new_email: str, session=None):

        """
        Updates the email of an admin.

        This method searches for an admin by their ID and updates their email to the provided new value.

        Args:
            idAdmin (int): The unique identifier of the admin whose email will be updated.
            new_email (str): The new email address to assign to the admin.
            session (Session, optional): SQLAlchemy session object for database interaction.
                If not provided, a new session will be created.

        Returns:
            dict: Result of the operation.
                - {"status": "ok", "message": "Email updated successfully"}:
                If the email is updated successfully.
                - {"status": "error", "message": <error_message>}:
                If an error occurs or the admin is not found.

        Raises:
            SQLAlchemyError: If a database-related error occurs.
            Exception: If an unexpected error occurs during the operation.
        """
        if session is None:
            session = Session(self.db_client.engine)

        try:
            # Buscar al administrador por idAdmin
            admin = session.query(Admin).filter(Admin.idAdmin == idAdmin).first()

            if admin is None:
                return {"status": "error", "message": "Administrador no encontrado"}

            # Actualizamos la contraseña
            admin.email = new_email

            # Guardamos los cambios
            session.commit()

            return {"status": "ok", "message": "Email actualizado exitosamente"}

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
    

    def updateAdminName(self, idAdmin: int, new_name: str, session=None):
        """
        Updates the name of an admin.

        This method searches for an admin by their ID and updates their name to the provided new value.

        Args:
            idAdmin (int): The unique identifier of the admin whose name will be updated.
            new_name (str): The new name to assign to the admin.
            session (Session, optional): SQLAlchemy session object for database interaction.
                If not provided, a new session will be created.

        Returns:
            dict: Result of the operation.
                - {"status": "ok", "message": "Name updated successfully"}:
                If the name is updated successfully.
                - {"status": "error", "message": <error_message>}:
                If an error occurs or the admin is not found.

        Raises:
            SQLAlchemyError: If a database-related error occurs.
            Exception: If an unexpected error occurs during the operation.
        """
        if session is None:
            session = Session(self.db_client.engine)

        try:
            # Buscar al administrador por idAdmin
            admin = session.query(Admin).filter(Admin.idAdmin == idAdmin).first()

            if admin is None:
                return {"status": "error", "message": "Administrador no encontrado"}

            # Actualizamos la contraseña
            admin.name = new_name

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
    
    