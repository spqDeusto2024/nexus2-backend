import os
from sqlalchemy.orm import Session
from app.mysql.mysql import DatabaseClient
from app.mysql.base import Base
from app.mysql.admin import Admin
from app.mysql.family import Family
from app.mysql.machine import Machine
from app.mysql.resident import Resident
from app.mysql.room import Room
from app.mysql.shelter import Shelter
from datetime import date

def initialize_database():
    
    """
    Seeds the database with initial data for all entities if the database is empty.
    This function ensures that the database is initialized with a default set of data
    for all core entities. It checks whether each entity's table is empty before 
    populating it with predefined data. This is useful for setting up the application
    with consistent initial data when running for the first time.

    Entities covered:
        - Admin: Represents administrative users of the system.
        - Family: Represents families residing in the shelter.
        - Machine: Represents machines associated with rooms in the shelter.
        - Resident: Represents individual residents in the shelter.
        - Room: Represents rooms available in the shelter.
        - Shelter: Represents the shelter itself, including metadata such as capacity
          and resource levels.

    Data Seeded:
        - Admins: Two sample admin accounts with email, name, and password.
        - Shelter: A single shelter with attributes like address, phone, energy level, etc.
        - Rooms: A set of rooms with details about their capacity and assignment to the shelter.
        - Families: A couple of families assigned to specific rooms in the shelter.
        - Residents: Sample residents, some assigned to families and others not.
        - Machines: A machine (e.g., a heater) associated with a room.

    Process:
        1. Checks if each entity's table is empty.
        2. If empty, inserts predefined data for that entity.
        3. Commits the session to persist the data.
        4. Handles errors by rolling back the session and printing the error message.

    """

    db_url = os.getenv("MYSQL_URL")
    if not db_url:
        raise ValueError("MYSQL_URL environment variable is not set.")

    db = DatabaseClient(db_url)
    Base.metadata.create_all(db.engine)
    session = Session(db.engine)

    try:
        if not session.query(Admin).first():
            admin_data = [
                {"idAdmin": 1, "email": "admin1@gmail.com", "name": "Maria", "password": "Maria1"},
                {"idAdmin": 2, "email": "admin2@gmail.com", "name": "Ana", "password": "Ana2"},
            ]
            session.bulk_insert_mappings(Admin, admin_data)

        if not session.query(Shelter).first():
            shelter_data = [
                {
                    "idShelter": 1,
                    "shelterName": "Nexus2",
                    "address": "123 Shelter Street",
                    "phone": "1234567890",
                    "email": "nexus2@gmail.com",
                    "maxPeople": 200,
                    "energyLevel": 85,
                    "waterLevel": 95,
                    "radiationLevel": 10,
                },
            ]
            session.bulk_insert_mappings(Shelter, shelter_data)

        if not session.query(Room).first():
            room_data = [
                {"idRoom": 1, "roomName": "Room 1", "maxPeople": 4, "createdBy": 1, "createDate": date.today(), "idShelter": 1},
                {"idRoom": 2, "roomName": "Room 2", "maxPeople": 3, "createdBy": 1, "createDate": date.today(), "idShelter": 1},
                {"idRoom": 3, "roomName": "Kitchen", "maxPeople": 2, "createdBy": 1, "createDate": date.today(), "idShelter": 1},
            ]
            session.bulk_insert_mappings(Room, room_data)

        if not session.query(Family).first():
            family_data = [
                {"idFamily": 1, "familyName": "Doe Family", "idRoom": 1, "idShelter": 1, "createdBy": 1, "createDate": date.today()},
                {"idFamily": 2, "familyName": "Smith Family", "idRoom": 2, "idShelter": 1, "createdBy": 2, "createDate": date.today()},
            ]
            session.bulk_insert_mappings(Family, family_data)

        if not session.query(Resident).first():
            resident_data = [
                {"idResident": 1, "name": "John", "surname": "Doe", "birthDate": date(1990, 1, 1), "gender": "M", "createdBy": 1, "createDate": date.today(), "idRoom": 1, "idFamily": 1},
                {"idResident": 2, "name": "Jane", "surname": "Smith", "birthDate": date(1985, 6, 15), "gender": "F", "createdBy": 1, "createDate": date.today(), "idRoom": 2, "idFamily": None},
            ]
            session.bulk_insert_mappings(Resident, resident_data)

        if not session.query(Machine).first():
            machine_data = [
                {"idMachine": 2, "machineName": "Heater", "on": False, "idRoom": 2, "createdBy": 1, "createDate": date.today(), "update": None},
            ]
            session.bulk_insert_mappings(Machine, machine_data)

        session.commit()
        print("Database successfully seeded.")
    except Exception as e:
        session.rollback()
        print(f"Error seeding database: {e}")
    finally:
        session.close()
