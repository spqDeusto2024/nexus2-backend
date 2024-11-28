
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.mysql.base import Base
from app.mysql.resident import Resident 
from app.mysql.family import Family
from app.mysql.room import Room
from app.mysql.shelter import Shelter

@pytest.fixture(scope="function")
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture
def setup_database():
    """
    Configura una base de datos temporal para las pruebas.
    """
    # Obtener la URL de la base de datos de prueba desde las variables de entorno
    import os
    db_url = os.getenv("MYSQL_URL", "mysql://user:password@localhost/test_database")
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Limpia después de la prueba
    yield session
    session.close()
    engine.dispose()
