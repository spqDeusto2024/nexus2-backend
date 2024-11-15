import pytest
from app.mysql.resident import Resident
from app.controllers.handler import Controllers 
from app.mysql.room import Room 
from datetime import date

def test_create_resident(setup_database):

    """
    Unit test for the `create_resident` method in the Controllers class.

    Test Steps:
        1. Create an instance of the `Controllers` class.
        2. Use the in-memory database session provided by `setup_database`.
        3. Define a mock resident object with valid details.
        4. Call the `create_resident` method with the mock resident and the test session.
        5. Assert that the method returns a success response: `{"status": "ok"}`.
        6. Query the database for the created resident using their name.
        7. Verify that the resident exists in the database.
        8. Assert that the resident's details (e.g., name, surname, room ID) match the expected values.

    Expected Outcome:
        - The `create_resident` method should return `{"status": "ok"}`.
        - The resident should be successfully added to the database with all details matching the mock input.
    """

    from app.controllers.handler import Controllers

    controllers = Controllers()
    db_session = setup_database

    mock_resident = Resident(
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

    response = controllers.create_resident(mock_resident, session=db_session)
    assert response == {"status": "ok"}

    created_resident = db_session.query(Resident).filter_by(name="Maria").first()
    assert created_resident is not None
    assert created_resident.name == "Maria"
    assert created_resident.surname == "Mutiloa"
    assert created_resident.idFamily == 1
    assert created_resident.idRoom == 101

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
    