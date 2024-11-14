import pytest
from app.mysql.resident import Resident  # Importación global permitida

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
