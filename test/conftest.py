# Archivo: test/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.mysql.base import Base
from app.mysql.resident import Resident 
from app.mysql.family import Family
from app.mysql.room import Room
from app.mysql.shelter import Shelter

@pytest.fixture(scope="function")
def setup_database():
    """
    Fixture to create an SQLite in-memory database for testing.
    """
    engine = create_engine("sqlite:///:memory:")  
    Base.metadata.create_all(engine)  
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
