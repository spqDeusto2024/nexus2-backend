import pytest
from app.mysql.resident import Resident  # Importación global permitida

from datetime import date

def test_create_resident(setup_database, monkeypatch):

    """
    Test for the `create_resident` method in the `Controllers` class.

    Purpose:
        Validates that the `create_resident` method correctly creates a new 
        resident entry in the database.

    Steps:
        1. Mock the `DatabaseClient` to use an in-memory SQLite database.
        2. Apply a monkeypatch to replace the real `DatabaseClient` with the mock.
        3. Initialize the `Controllers` class.
        4. Create a mock `Resident` object with valid data.
        5. Call the `create_resident` method using the mock resident data.
        6. Verify the response from `create_resident`.
        7. Query the database to ensure the resident was successfully created.
        8. Assert that the resident's details in the database match the input data.

    Expected Outcome:
        - The `create_resident` method returns a response indicating success.
        - The resident is successfully added to the database with correct details.

    Dependencies:
        - `setup_database` fixture for providing an SQLite in-memory database.
        - `monkeypatch` for replacing the `DatabaseClient`.

    Assertions:
        - Response from `create_resident` is `{"status": "ok"}`.
        - The resident exists in the database with matching `name`, `surname`, and `idRoom`.

    """
    def mock_database_client(url):
        class MockDatabaseClient:
            def __init__(self, url):
                self.engine = setup_database.bind

        return MockDatabaseClient(url)

    monkeypatch.setattr("app.mysql.mysql.DatabaseClient", mock_database_client)

    from app.controllers.handler import Controllers
    from app.mysql.resident import Resident

    controllers = Controllers()
    mock_resident = Resident(
        idResident=1,
        name="John",
        surname="Doe",
        birthDate=date(1990, 1, 1),  
        gender="M",
        createdBy=1,
        createDate=date(2024, 11, 14),  
        update=None,
        idFamily=1,
        idRoom=101,
    )

    response = controllers.create_resident(mock_resident)

    assert response == {"status": "ok"}

    db_session = setup_database
    created_resident = db_session.query(Resident).filter_by(name="John").first()
    assert created_resident is not None
    assert created_resident.name == "John"
    assert created_resident.surname == "Doe"
    assert created_resident.idRoom == 101
