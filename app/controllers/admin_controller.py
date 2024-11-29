from app.mysql.mysql import DatabaseClient
from app.mysql.admin import Admin  # SQLAlchemy model for the database
from app.models.admin import Admin as AdminModel  # Pydantic model for request validation
from sqlalchemy.orm import Session
import app.utils.vars as gb
from fastapi import HTTPException

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

class AdminController:

    def __init__(self, db_url=None):
        # Usa MYSQL_URL de la variable de entorno si no se pasa db_url
        self.db_url = db_url or os.getenv("MYSQL_URL")
        if not self.db_url:
            raise ValueError("MYSQL_URL environment variable is not set.")
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



    def loginAdmin(self, email: str, password: str, session=None):
        """
        Verifica las credenciales de login usando el email y la contraseña del administrador.

        Args:
            email (str): Email del administrador.
            password (str): Contraseña del administrador.
            session (Session, optional): Sesión SQLAlchemy para interacción con la base de datos.

        Returns:
            dict: Resultado del login.
                - {"status": "ok", "user": {idAdmin, email}}: Si el login es exitoso.
                - {"status": "error", "message": <error_message>}: Si ocurre algún error.
        """
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

            return {
                "status": "ok",
                "user": {
                    "idAdmin": user.idAdmin,  # Asegúrate de que el atributo sea correcto
                    "email": user.email,
                },
            }

        except Exception as e:
            # Aquí se captura cualquier otra excepción que pueda ocurrir
            return {"status": "error", "message": str(e)}

        finally:
            # Asegúrate de cerrar la sesión para evitar problemas de conexiones abiertas
            if session:
                session.close()

    def deleteAdmin(self, admin_id: int, session=None):
        """
        Elimina un administrador de la base de datos usando su ID.

        Args:
            admin_id (int): ID del administrador que se desea eliminar.
            session (Session, optional): Sesión SQLAlchemy para interacción con la base de datos.

        Returns:
            dict: Resultado de la operación.
                - {"status": "ok", "message": "Admin deleted successfully"}: Si la eliminación es exitosa.
                - {"status": "error", "message": <error_message>}: Si ocurre algún error.
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
        Lista todos los administradores registrados en la base de datos.

        Args:
            session (Session, optional): Sesión SQLAlchemy para interacción con la base de datos.

        Returns:
            dict: Resultado de la operación.
                - {"status": "ok", "admins": [<listado_de_admins>]}: Si se encuentran administradores.
                - {"status": "error", "message": <error_message>}: Si ocurre algún error.
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
