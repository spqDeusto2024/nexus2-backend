import pytest
from app.mysql.resident import Resident
from app.controllers.handler import Controllers 
from app.mysql.room import Room 
from app.mysql.shelter import Shelter
from app.mysql.family import Family
from datetime import date
from sqlalchemy.orm import Session
from app.mysql.admin import Admin as AdminModel
from app.models.admin import Admin as AdminSchema

def test_create_resident_with_capacity(setup_database):
    """
    Test: Verifies that a family with an assigned room and sufficient capacity can add a new resident.

    Steps:
        1. Verify that the family has an assigned room.
        2. Ensure that the room has enough capacity to accommodate the new resident.
        3. Call the `create_resident` method to add the new resident.
        4. Verify that the new resident was successfully added to the database.

    Expected Outcome:
        - The new resident should be successfully created and assigned to the family and the room.
        - The resident should be present in the database with the correct details.

    Arguments:
        setup_database (fixture): The database session used for test setup.
    """
    controllers = Controllers()
    db_session = setup_database

    family = Family(idFamily=1, familyName="Doe Family", idRoom=101, idShelter=1, createdBy=1, createDate=date.today())
    db_session.add(family)
    db_session.commit()

    new_resident = Resident(
        name="John",
        surname="Doe",
        birthDate=date(1990, 1, 1),
        gender="M",
        createdBy=1,
        createDate=date.today(),
        idFamily=1,
        idRoom=101 
    )
    
    response = controllers.create_resident(new_resident, session=db_session)

    assert response == {"status": "ok"}
    
    added_resident = db_session.query(Resident).filter_by(name="John", surname="Doe").first()
    assert added_resident is not None
    assert added_resident.name == "John"
    assert added_resident.surname == "Doe"
    
def test_create_resident_with_capacity_exceeded_existing_room(setup_database):
    """
    Test: Verifies that a family with an assigned room exceeding the room's capacity is reassigned to a new room with available space.

    Steps:
        1. Simulate a room where the family is already assigned and has reached the maximum capacity.
        2. Call the `create_resident` method to reassign the family to a new room with available space.
        3. Verify that the family was reassigned to a room that has enough space for the new resident.

    Expected Outcome:
        - The new resident should be successfully added to the family.
        - The family should be reassigned to a room that has enough capacity for the new resident.
        - The room assigned to the family should be updated in the database.

    Arguments:
        setup_database (fixture): The database session used for test setup.

    """
    controllers = Controllers()
    db_session = setup_database

    room = Room(idRoom=101, roomName="Room 101", maxPeople=2, idShelter=1)
    db_session.add(room)
    db_session.commit()

    db_session.add(Resident(name="Resident 1", surname="Test", idRoom=101, idFamily=1, createdBy=1, createDate=date.today()))
    db_session.add(Resident(name="Resident 2", surname="Test", idRoom=101, idFamily=1, createdBy=1, createDate=date.today()))
    db_session.commit()

    family = Family(idFamily=1, familyName="Doe Family", idRoom=101, idShelter=1, createdBy=1, createDate=date.today())
    db_session.add(family)
    db_session.commit()

    new_resident = Resident(name="John", surname="Doe", birthDate=date(1990, 1, 1), gender="M", createdBy=1, idFamily=1, idRoom=None)

    response = controllers.create_resident(new_resident, session=db_session)

    assert response == {"status": "ok"}

    updated_family = db_session.query(Family).filter_by(idFamily=1).first()
    assert updated_family.idRoom != 101  

def test_create_resident_no_room_assigned(setup_database):
    """
    Test: Verifies that when a family does not have a room assigned, a new room is created for them.

    Steps:
        1. Ensure that the family does not have a room assigned (`idRoom` is `None`).
        2. Call the `create_resident` method to create a new resident for the family.
        3. Verify that the method automatically assigns a new room to the family.
        4. Ensure that the resident was created successfully in the newly assigned room.

    Expected Outcome:
        - A new room should be created for the family, and the resident should be assigned to that room.
        - The response should indicate success (`status: "ok"`).

    Arguments:
        setup_database (fixture): The database session used for test setup.
    """
    controllers = Controllers()
    db_session = setup_database

    family = Family(idFamily=1, familyName="Doe Family", idRoom=None, idShelter=1, createdBy=1, createDate=date.today())
    db_session.add(family)
    db_session.commit()

    new_resident = Resident(name="John", surname="Doe", birthDate=date(1990, 1, 1), gender="M", createdBy=1, idFamily=1, idRoom=None)

    response = controllers.create_resident(new_resident, session=db_session)

    assert response == {"status": "error", "message": "The family does not have an assigned room."}

def test_create_resident_duplicate(setup_database):
    """
    Test: Verifies that a resident cannot be added if a duplicate exists in the room.

    Steps:
        1. Create a family with a room assigned.
        2. Add a resident to the room.
        3. Attempt to add another resident with the same name, surname, and family ID to the same room.
        4. Ensure that the error message "Cannot create resident, the resident already exists in this room." is returned.

    Expected Outcome:
        - The second resident should not be added to the room.
        - The system should return an error message indicating that the resident already exists in the room.
        - The database should contain only one resident with the given name, surname, and room.

    Arguments:
        setup_database (fixture): The database session used for test setup.

    """
    controllers = Controllers()
    db_session = setup_database

    family = Family(idFamily=1, familyName="Doe Family", idRoom=101, idShelter=1, createdBy=1, createDate=date.today())
    db_session.add(family)
    db_session.commit()

    resident1 = Resident(name="John", surname="Doe", birthDate=date(1990, 1, 1), gender="M", createdBy=1, idFamily=1, idRoom=101)
    db_session.add(resident1)
    db_session.commit()

    new_resident = Resident(name="John", surname="Doe", birthDate=date(1990, 1, 1), gender="M", createdBy=1, idFamily=1, idRoom=101)
    response = controllers.create_resident(new_resident, session=db_session)

    assert response == {"status": "error", "message": "Cannot create resident, the resident already exists in this room."}


def test_create_resident_shelter_full_capacity(setup_database):
    """
    Test: Verifies that a new resident cannot be added if the shelter is at full capacity.
    
    Steps:
        1. Create a shelter with a maximum capacity limit for residents.
        2. Add residents to the shelter until its capacity is reached.
        3. Attempt to add another resident and ensure that the error message 
           "The shelter is full" is returned.

    Expected Outcome:
        - The shelter should reject the addition of a new resident once it reaches its maximum capacity.
        - The system should return an error message indicating that the shelter is full.
        - The number of residents in the shelter should not exceed the shelter's maximum capacity.

    Arguments:
        setup_database (fixture): The database session used for the test setup.
    """
    controllers = Controllers()
    db_session = setup_database

    shelter = Shelter(idShelter=1, shelterName="Main Shelter", maxPeople=2, energyLevel=80, waterLevel=90, radiationLevel=10)
    db_session.add(shelter)
    db_session.commit()

    family = Family(idFamily=1, familyName="Doe Family", idRoom=101, idShelter=1, createdBy=1, createDate=date.today())
    db_session.add(family)
    db_session.commit()

    resident1 = Resident(name="John", surname="Doe", birthDate=date(1990, 1, 1), gender="M", createdBy=1, idFamily=1, idRoom=101)
    resident2 = Resident(name="Jane", surname="Doe", birthDate=date(1992, 1, 1), gender="F", createdBy=1, idFamily=1, idRoom=101)
    db_session.add(resident1)
    db_session.add(resident2)
    db_session.commit()

    new_resident = Resident(name="Alice", surname="Doe", birthDate=date(1995, 1, 1), gender="F", createdBy=1, idFamily=1, idRoom=101)
    response = controllers.create_resident(new_resident, session=db_session)

    assert response == {"status": "error", "message": "The shelter is full."}


def test_delete_resident(setup_database):
    """
    Unit test for the `delete_resident` method in the Controllers class.

    Test Steps:
        1. Create an instance of the `Controllers` class.
        2. Use the in-memory database session provided by `setup_database`.
        3. Insert a mock resident into the database with valid details.
        4. Commit the mock resident to ensure they are added to the database.
        5. Query the database to verify the resident was successfully added.
        6. Call the `delete_resident` method with the resident's ID and the test session.
        7. Use `expire_all` to refresh the session state.
        8. Assert that the method returns a success response: `{"status": "ok"}`.
        9. Query the database again to verify the resident's record has been deleted.
        10. Assert that the resident is no longer present in the database.

    Expected Outcome:
        - The `delete_resident` method should return `{"status": "ok"}`.
        - The resident's record should be successfully removed from the database.
    """
    from app.controllers.handler import Controllers

    controllers = Controllers()
    db_session = setup_database

    test_resident = Resident(
        idResident=1,
        name="Maria",
        surname="Mutiloa",
        birthDate=date(2001, 1, 1),
        gender="F",
        createdBy=1,
        createDate=date(2024, 11, 14),
        update=None,
        idFamily=1,
        idRoom=101,
    )
    db_session.add(test_resident)
    db_session.commit()

    added_resident = db_session.query(Resident).filter_by(idResident=1).first()
    assert added_resident is not None

    response = controllers.delete_resident(1, session=db_session)

    db_session.expire_all()
    assert response == {"status": "ok"}
    deleted_resident = db_session.query(Resident).filter_by(idResident=1).first()
    assert deleted_resident is None

def test_update_resident(setup_database):

    """
    Test for the `update_resident` method.

    Purpose:
        Verifies that an existing resident's details can be updated successfully.

    Steps:
        1. Creates a test resident entry in the in-memory SQLite database.
        2. Ensures the resident was correctly added to the database.
        3. Updates specific fields (`name` and `idRoom`) of the resident.
        4. Verifies the response status from the update operation.
        5. Confirms that the resident's details were updated in the database.
        6. Ensures that unchanged fields remain intact.
    """

    controllers = Controllers()
    db_session = setup_database

    test_resident = Resident(
        idResident=1,
        name="Maria",
        surname="Mutiloa",
        birthDate=date(2001, 1, 1),
        gender="M",
        createdBy=1,
        createDate=date(2024, 11, 14),
        update=None,
        idFamily=1,
        idRoom=101,
    )
    db_session.add(test_resident)
    db_session.commit()

    added_resident = db_session.query(Resident).filter_by(idResident=1).first()
    assert added_resident is not None
    assert added_resident.name == "Maria"
    assert added_resident.surname == "Mutiloa"

    updated_fields = {"name": "Ana", "idRoom": 202}
    response = controllers.update_resident(1, updated_fields, session=db_session)

    assert response == {"status": "ok"}

    updated_resident = db_session.query(Resident).filter_by(idResident=1).first()
    assert updated_resident is not None
    assert updated_resident.name == "Ana"
    assert updated_resident.surname == "Mutiloa" 
    assert updated_resident.idRoom == 202 

def test_create_room(setup_database):
    
    """
    Test: Verifies that a room is created.

    Expected Outcome:
        - The new room should be successfully created.
        - The room should be present in the database with the correct details.

    Arguments:
        setup_database (fixture): The database session used for test setup.
    """
    controllers = Controllers()
    db_session = setup_database

    room = Room(idRoom=1, roomName="Canteen", createdBy=1, createDate=date.today(), idShelter=1, maxPeople=20)
    db_session.add(room)
    db_session.commit()

    response = controllers.create_room(room, session=db_session)

    assert response == {"status": "ok"}

    added_room = db_session.query(Room).filter_by(roomName="Canteen").first()
    assert added_room is not None
    assert added_room.roomName == "Canteen"
    

def test_list_rooms_with_resident_count(setup_database):

    """
    Test for the `list_rooms_with_resident_count` method in the controller.

    This test ensures that the method correctly retrieves all rooms along with 
    the count of residents assigned to each room.

    Steps:
        1. Create two room records (`room1` and `room2`) and add them to the database.
        2. Create three resident records (`resident1`, `resident2`, `resident3`) and 
           assign them to rooms:
           - `resident1` and `resident2` belong to `room1`.
           - `resident3` belongs to `room2`.
        3. Commit these records to the test database.
        4. Call the `list_rooms_with_resident_count` method from the controller to 
           retrieve room details along with resident counts.
        5. Validate that:
           - Two rooms are returned in the result.
           - The resident count for each room matches the expected values.
           - Room details such as `idRoom` and `roomName` are correctly included.
    """

    from app.controllers.handler import Controllers

    controllers = Controllers()
    db_session = setup_database

    room1 = Room(idRoom=1, roomName="Room A", maxPeople=4, createdBy=1, createDate=date(2024, 11, 14), idShelter=1)
    room2 = Room(idRoom=2, roomName="Room B", maxPeople=3, createdBy=1, createDate=date(2024, 11, 14), idShelter=1)
    db_session.add_all([room1, room2])
    db_session.commit()

    resident1 = Resident(idResident=1, name="John", surname="Doe", birthDate=date(1990, 1, 1), gender="M", createdBy=1, createDate=date(2024, 11, 14), idRoom=1)
    resident2 = Resident(idResident=2, name="Jane", surname="Smith", birthDate=date(1985, 6, 15), gender="F", createdBy=1, createDate=date(2024, 11, 14), idRoom=1)
    resident3 = Resident(idResident=3, name="Alice", surname="Brown", birthDate=date(1995, 8, 23), gender="F", createdBy=1, createDate=date(2024, 11, 14), idRoom=2)
    db_session.add_all([resident1, resident2, resident3])
    db_session.commit()

    result = controllers.list_rooms_with_resident_count(session=db_session)

    assert len(result) == 2
    assert result[0]["idRoom"] == 1
    assert result[0]["roomName"] == "Room A"
    assert result[0]["resident_count"] == 2

    assert result[1]["idRoom"] == 2
    assert result[1]["roomName"] == "Room B"
    assert result[1]["resident_count"] == 1
    
def test_get_shelter_energy_level(setup_database):
    """
    Test for the `get_shelter_energy_level` method.

    Test Steps:
        1. Setup:
            - Create a test instance of the `Shelter` model with predefined attributes,
              including an `energyLevel` value.
            - Add the test shelter to the in-memory SQLite database and commit the transaction.
        2. Execution:
            - Call the `get_shelter_energy_level` method via the `Controllers` class.
        3. Verification:
            - Ensure the method returns the expected energy level (`{"energyLevel": 80}`).

    Expected Result:
        The method should return a dictionary with the correct energy level of the shelter.

    """
    from app.controllers.handler import Controllers

    controllers = Controllers()
    db_session = setup_database

    test_shelter = Shelter(
        idShelter=1,
        shelterName="Main Shelter",
        address="123 Shelter Street",
        phone="1234567890",
        email="shelter@example.com",
        maxPeople=100,
        energyLevel=80,
        waterLevel=90,
        radiationLevel=10,
    )
    db_session.add(test_shelter)
    db_session.commit()

    response = controllers.get_shelter_energy_level(session=db_session)

    assert response == {"energyLevel": 80}

def test_get_shelter_water_level(setup_database):
    
    """
    Test for the `get_shelter_water_level` method.

    Test Steps:
        1. Setup:
            - Create a test instance of the `Shelter` model with predefined attributes,
              including a `waterLevel` value.
            - Add the test shelter to the in-memory SQLite database and commit the transaction.
        2. Execution:
            - Call the `get_shelter_water_level` method via the `Controllers` class.
        3. Verification:
            - Ensure the method returns the expected water level (`{"waterLevel": 90}`).

    Expected Result:
        The method should return a dictionary with the correct water level of the shelter.

    """
    from app.controllers.handler import Controllers

    controllers = Controllers()
    db_session = setup_database

    test_shelter = Shelter(
        idShelter=1,
        shelterName="Main Shelter",
        address="123 Shelter Street",
        phone="1234567890",
        email="shelter@example.com",
        maxPeople=100,
        energyLevel=80,
        waterLevel=90,
        radiationLevel=10,
    )
    db_session.add(test_shelter)
    db_session.commit()

    response = controllers.get_shelter_water_level(session=db_session)

    assert response == {"waterLevel": 90}

def test_get_shelter_radiation_level(setup_database):
    
    """
    Test for the `get_shelter_radiation_level` method.

    Test Steps:
        1. Setup:
            - Create a test instance of the `Shelter` model with predefined attributes,
              including a `radiationLevel` value.
            - Add the test shelter to the in-memory SQLite database and commit the transaction.
        2. Execution:
            - Call the `get_shelter_radiation_level` method via the `Controllers` class.
        3. Verification:
            - Ensure the method returns the expected radiation level (`{"radiationLevel": 10}`).

    Expected Result:
        The method should return a dictionary with the correct radiation level of the shelter.

    """
    from app.controllers.handler import Controllers

    controllers = Controllers()
    db_session = setup_database

    test_shelter = Shelter(
        idShelter=1,
        shelterName="Main Shelter",
        address="123 Shelter Street",
        phone="1234567890",
        email="shelter@example.com",
        maxPeople=100,
        energyLevel=80,
        waterLevel=90,
        radiationLevel=10,
    )
    db_session.add(test_shelter)
    db_session.commit()

    response = controllers.get_shelter_radiation_level(session=db_session)

    assert response == {"radiationLevel": 10}

def test_access_room(setup_database):

    """
    Test for the `access_room` method in the controller.

    This test validates the logic for determining access rights of residents to rooms, 
    based on the following scenarios:
    
    Scenarios Tested:
        1. Resident is granted access to their assigned family room.
        2. Resident is denied access to a family room they are not part of.
        3. Resident is granted access to a non-restricted room (not starting with "Room").
        4. Resident attempts to access a room that does not exist.
        5. A non-existent resident attempts to access a room.
    """

    controllers = Controllers()
    db_session = setup_database

    room1 = Room(idRoom=1, roomName="Room A", maxPeople=4, createdBy=1, createDate=date(2024, 11, 14), idShelter=1)
    room2 = Room(idRoom=2, roomName="Meeting Room", maxPeople=3, createdBy=1, createDate=date(2024, 11, 14), idShelter=1)
    room3 = Room(idRoom=3, roomName="RoomPrivate1", maxPeople=2, createdBy=1, createDate=date(2024, 11, 14), idShelter=1)
    db_session.add_all([room1, room2, room3])

    family1 = Family(idFamily=1, familyName="Doe Family", idRoom=1, idShelter=1, createdBy=1, createDate=date(2024, 11, 14))
    db_session.add(family1)

    resident1 = Resident(idResident=1, name="John", surname="Doe", birthDate=date(1990, 1, 1), gender="M",
                          createdBy=1, createDate=date(2024, 11, 14), idRoom=1, idFamily=1)
    resident2 = Resident(idResident=2, name="Jane", surname="Smith", birthDate=date(1985, 6, 15), gender="F",
                          createdBy=1, createDate=date(2024, 11, 14), idRoom=1, idFamily=None)
    db_session.add_all([resident1, resident2])
    db_session.commit()

    response1 = controllers.access_room(1, 1, session=db_session)
    assert response1 == "Access granted. Welcome to the room."

    response2 = controllers.access_room(2, 1, session=db_session)
    assert response2 == "Access denied. You are in the wrong room."

    response3 = controllers.access_room(2, 2, session=db_session) 
    assert response3 == "Access granted. Welcome to the room."

    response4 = controllers.access_room(1, 999, session=db_session)
    assert response4 == "Room not found."

    response5 = controllers.access_room(999, 1, session=db_session)
    assert response5 == "Resident not found."

def test_list_residents_in_room(setup_database):

    """
    Test for the `list_residents_in_room` method in the controller.

    This test ensures that the method correctly retrieves all residents 
    assigned to a specific room.

    Steps:
        1. Create two room records (`room1` and `room2`) and add them to the database.
        2. Create three resident records (`resident1`, `resident2`, `resident3`) and 
           assign them to rooms:
           - `resident1` and `resident2` belong to `room1`.
           - `resident3` belongs to `room2`.
        3. Commit these records to the test database.
        4. Call the `list_residents_in_room` method from the controller for `room1` 
           and validate that:
           - Two residents are returned in the result.
           - Each resident's details are correct and match the input data.
        5. Repeat the process for `room2`.
    """

    from app.controllers.handler import Controllers

    controllers = Controllers()
    db_session = setup_database

    room1 = Room(idRoom=1, roomName="Room A", maxPeople=4, createdBy=1, createDate=date(2024, 11, 14), idShelter=1)
    room2 = Room(idRoom=2, roomName="Room B", maxPeople=3, createdBy=1, createDate=date(2024, 11, 14), idShelter=1)
    db_session.add_all([room1, room2])
    db_session.commit()

    resident1 = Resident(idResident=1, name="John", surname="Doe", birthDate=date(1990, 1, 1), gender="M", createdBy=1, createDate=date(2024, 11, 14), idRoom=1)
    resident2 = Resident(idResident=2, name="Jane", surname="Smith", birthDate=date(1985, 6, 15), gender="F", createdBy=1, createDate=date(2024, 11, 14), idRoom=1)
    resident3 = Resident(idResident=3, name="Alice", surname="Brown", birthDate=date(1995, 8, 23), gender="F", createdBy=1, createDate=date(2024, 11, 14), idRoom=2)
    db_session.add_all([resident1, resident2, resident3])
    db_session.commit()

    result = controllers.list_residents_in_room(1, session=db_session)

    assert len(result) == 2
    assert result[0]["idResident"] == 1
    assert result[0]["name"] == "John"
    assert result[0]["surname"] == "Doe"
    assert result[0]["idRoom"] == 1

    assert result[1]["idResident"] == 2
    assert result[1]["name"] == "Jane"
    assert result[1]["surname"] == "Smith"
    assert result[1]["idRoom"] == 1

    result = controllers.list_residents_in_room(2, session=db_session)

    assert len(result) == 1
    assert result[0]["idResident"] == 3
    assert result[0]["name"] == "Alice"
    assert result[0]["surname"] == "Brown"
    assert result[0]["idRoom"] == 2

def test_create_admin_success(setup_database):
    
    """
    Test the successful creation of an admin.

    This test ensures that:
        1. The `create_admin` function creates a new admin successfully when provided with valid data.
        2. The response from the function indicates success with the correct message.
        3. The admin record is correctly added to the database with:
           - The expected email and name.
           - The password hashed using SHA-256.

    Steps:
        1. Create a mock admin object with valid details.
        2. Call the `create_admin` method to add the admin to the database.
        3. Verify that the response status is "ok" and the message indicates success.
        4. Query the database to confirm the admin's details were saved correctly.
        5. Check that the password is stored as a SHA-256 hash.
    """

    db_session: Session = setup_database
    controllers = Controllers()

    admin_data = AdminSchema(
        idAdmin=1,
        email="admin@example.com",
        name="Admin Name",
        password="securepassword"
    )

    response = controllers.create_admin(admin_data, session=db_session)

    assert response["status"] == "ok"
    assert response["message"] == "Admin created successfully."

    admin_from_db = db_session.query(AdminModel).filter_by(email=admin_data.email).first()
    assert admin_from_db is not None
    assert admin_from_db.email == admin_data.email
    assert admin_from_db.name == admin_data.name

    hashed_password = hashlib.sha256(admin_data.password.encode()).hexdigest()
    assert admin_from_db.password == hashed_password

def test_create_admin_duplicate_email(setup_database):
    
    """
    Test the creation of an admin with an email that already exists.

    This test ensures that:
        1. The `create_admin` function prevents the creation of a new admin 
           when an admin with the same email already exists in the database.
        2. The response from the function indicates failure with an appropriate error message.

    Steps:
        1. Insert an existing admin into the database with a specific email.
        2. Attempt to create a new admin with the same email.
        3. Verify that the response status is "error" and the message indicates the duplication issue.
        4. Ensure that no new admin is added to the database for the duplicate email.
    """

    db_session: Session = setup_database
    controllers = Controllers()

    existing_admin = AdminModel(
        idAdmin=1,
        email="admin@example.com",
        name="Existing Admin",
        password=hashlib.sha256("securepassword".encode()).hexdigest()
    )
    db_session.add(existing_admin)
    db_session.commit()

    admin_data = AdminSchema(
        idAdmin=2,
        email="admin@example.com",
        name="New Admin",
        password="newpassword"
    )

    response = controllers.create_admin(admin_data, session=db_session)

    assert response["status"] == "error"
    assert response["message"] == "An admin with this email already exists."

def test_create_admin_password_hashing(setup_database):
    
    """
    Test that the password is hashed correctly when creating an admin.

    This test ensures that:
        1. The `create_admin` function hashes the password using the SHA-256 algorithm before storing it.
        2. The hashed password in the database matches the expected hash for the provided password.

    Steps:
        1. Create a mock admin object with a valid password.
        2. Call the `create_admin` method to add the admin to the database.
        3. Query the database to retrieve the saved admin record.
        4. Compute the SHA-256 hash of the provided password locally.
        5. Verify that the hash stored in the database matches the computed hash.
    """

    db_session: Session = setup_database
    controllers = Controllers()

    admin_data = AdminSchema(
        idAdmin=1,
        email="admin@example.com",
        name="Admin Name",
        password="securepassword"
    )

    response = controllers.create_admin(admin_data, session=db_session)

    assert response["status"] == "ok"

    admin_from_db = db_session.query(AdminModel).filter_by(email=admin_data.email).first()
    assert admin_from_db is not None
    hashed_password = hashlib.sha256(admin_data.password.encode()).hexdigest()
    assert admin_from_db.password == hashed_password

