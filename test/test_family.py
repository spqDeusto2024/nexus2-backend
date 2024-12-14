import pytest
from app.controllers.family_controller import FamilyController
from app.models.family import Family as FamilyModel
from app.mysql.family import Family
from app.mysql.resident import Resident
from app.mysql.room import Room
from app.mysql.shelter import Shelter
from app.mysql.admin import Admin
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from unittest.mock import MagicMock


def test_create_family_success(setup_database):
    """
    Test: Successfully create a new family.

    Steps:
        1. Add a room, shelter, and admin to the database.
        2. Call the `create_family` method with valid data.
        3. Verify the response is successful.
        4. Confirm the family is added to the database with the correct details.

    Expected Outcome:
        - The family should be successfully created.
        - The family should exist in the database with the provided details.

    Arguments:
        setup_database (fixture): The database session used for test setup.
    """
    session = setup_database
    controller = FamilyController()

    # Add required room, shelter, and admin
    room = Room(idRoom=1, roomName="Room A", maxPeople=4, createdBy=1, createDate=datetime.now(), idShelter=1)
    shelter = Shelter(idShelter=1, shelterName="Main Shelter", maxPeople=50, energyLevel=100, waterLevel=100, radiationLevel=10)
    admin = Admin(idAdmin=1, email="admin@example.com", name="Admin", password="password123")
    session.add_all([room, shelter, admin])
    session.commit()

    # Family data
    family_data = FamilyModel(
        idFamily=1,
        familyName="Doe Family",
        idRoom=1,
        idShelter=1,
        createdBy=1,
        createDate=datetime.now()
    )

    response = controller.create_family(family_data, session=session)

    assert response == {"status": "ok"}

    added_family = session.query(Family).filter_by(familyName="Doe Family").first()
    assert added_family is not None
    assert added_family.idRoom == 1
    assert added_family.idShelter == 1
    assert added_family.createdBy == 1

def test_create_family_room_not_exist(setup_database):
    """
    Test: Prevent creating a family when the room does not exist.

    Steps:
        1. Call the `create_family` method with a nonexistent room ID.
        2. Verify the response indicates that the room does not exist.

    Expected Outcome:
        - The operation should fail with an error message about the room.
        - No family should be added to the database.

    Arguments:
        setup_database (fixture): The database session used for test setup.
    """
    session = setup_database
    controller = FamilyController()

    # Family data with nonexistent room
    family_data = FamilyModel(
        idFamily=1,
        familyName="Doe Family",
        idRoom=999,  # Nonexistent room
        idShelter=1,
        createdBy=1,
        createDate=datetime.now()
    )

    response = controller.create_family(family_data, session=session)

    assert response == {"status": "error", "message": "The room does not exist."}

    family_count = session.query(Family).count()
    assert family_count == 0

def test_create_family_shelter_not_exist(setup_database):
    """
    Test: Prevent creating a family when the shelter does not exist.

    Steps:
        1. Add a room and admin to the database.
        2. Call the `create_family` method with a nonexistent shelter ID.
        3. Verify the response indicates that the shelter does not exist.

    Expected Outcome:
        - The operation should fail with an error message about the shelter.
        - No family should be added to the database.

    Arguments:
        setup_database (fixture): The database session used for test setup.
    """
    session = setup_database
    controller = FamilyController()

    # Add required room and admin
    room = Room(idRoom=1, roomName="Room A", maxPeople=4, createdBy=1, createDate=datetime.now(), idShelter=1)
    admin = Admin(idAdmin=1, email="admin@example.com", name="Admin", password="password123")
    session.add_all([room, admin])
    session.commit()

    # Family data with nonexistent shelter
    family_data = FamilyModel(
        idFamily=1,
        familyName="Doe Family",
        idRoom=1,
        idShelter=999,  # Nonexistent shelter
        createdBy=1,
        createDate=datetime.now()
    )

    response = controller.create_family(family_data, session=session)

    assert response == {"status": "error", "message": "The shelter does not exist."}

    family_count = session.query(Family).count()
    assert family_count == 0

def test_create_family_duplicate(setup_database):
    """
    Test: Prevent creating a duplicate family in the same room.

    Steps:
        1. Add a room, shelter, admin, and an existing family to the database.
        2. Call the `create_family` method with the same family name and room ID.
        3. Verify the response indicates that the family already exists.

    Expected Outcome:
        - The operation should fail with an error message about the duplicate family.
        - No duplicate family should be added to the database.

    Arguments:
        setup_database (fixture): The database session used for test setup.
    """
    session = setup_database
    controller = FamilyController()

    # Add required room, shelter, admin, and existing family
    room = Room(idRoom=1, roomName="Room A", maxPeople=4, createdBy=1, createDate=datetime.now(), idShelter=1)
    shelter = Shelter(idShelter=1, shelterName="Main Shelter", maxPeople=50, energyLevel=100, waterLevel=100, radiationLevel=10)
    admin = Admin(idAdmin=1, email="admin@example.com", name="Admin", password="password123")
    family = Family(idFamily=1, familyName="Doe Family", idRoom=1, idShelter=1, createdBy=1, createDate=datetime.now())
    session.add_all([room, shelter, admin, family])
    session.commit()

    # Attempt to create duplicate family
    family_data = FamilyModel(
        idFamily=2,
        familyName="Doe Family",  # Same family name
        idRoom=1,                 # Same room
        idShelter=1,
        createdBy=1,
        createDate=datetime.now()
    )

    response = controller.create_family(family_data, session=session)

    assert response == {"status": "error", "message": "A family with the same name already exists in this room."}

    family_count = session.query(Family).count()
    assert family_count == 1

def test_delete_family_successful(mocker, setup_database):
    """
    Test: Validate successful deletion of a family with no members.
    """
    session = setup_database
    controller = FamilyController()

    # Add a family to the database
    family = Family(idFamily=1, familyName="Smith")
    session.add(family)
    session.commit()

    # Test successful deletion of a family with no members
    response = controller.deleteFamily(family_id=1, session=session)
    assert response == {"status": "ok", "message": "Family deleted successfully"}

    # Verify the family was removed from the database
    deleted_family = session.query(Family).filter_by(idFamily=1).first()
    assert deleted_family is None


def test_delete_nonexistent_family(mocker, setup_database):
    """
    Test: Validate error when attempting to delete a family that does not exist.
    """
    session = setup_database
    controller = FamilyController()

    # Attempt to delete a nonexistent family
    response = controller.deleteFamily(family_id=99, session=session)
    assert response == {"status": "error", "message": "Family not found"}


def test_delete_family_with_members(mocker, setup_database):
    """
    Test: Validate error when attempting to delete a family with associated members.
    """
    session = setup_database
    controller = FamilyController()

    # Add a new family and a member associated with it
    family_with_members = Family(idFamily=2, familyName="Johnson")
    resident = Resident(idResident=1, idFamily=2, name="John Doe", surname="Doe")
    session.add(family_with_members)
    session.add(resident)
    session.commit()

    # Attempt to delete a family with associated members
    response = controller.deleteFamily(family_id=2, session=session)
    assert response == {"status": "error", "message": "Cannot delete family, there are members associated with it"}


def test_delete_family_sqlalchemy_error(mocker, setup_database):
    """
    Test: Validate handling of SQLAlchemyError during deletion.
    """
    session = setup_database
    controller = FamilyController()

    # Add a family to the database
    family = Family(idFamily=1, familyName="Smith")
    session.add(family)
    session.commit()

    # Mock SQLAlchemyError during session commit specifically for `deleteFamily`
    mocker.patch("sqlalchemy.orm.session.Session.commit", side_effect=SQLAlchemyError("Database error"))

    # Spy on the rollback method
    rollback_spy = mocker.spy(session, "rollback")

    # Attempt to delete a family, expecting a database error
    response = controller.deleteFamily(family_id=1, session=session)

    # Assertions
    assert response == {"status": "error", "message": "Database error"}
    rollback_spy.assert_called_once()

import pytest
from sqlalchemy.exc import SQLAlchemyError
from unittest.mock import MagicMock
from datetime import datetime

# Assuming the necessary imports for Family, FamilyController, and session fixtures

def test_list_families_success(setup_database):
    """
    Test: Validate successful retrieval of families from the database.

    Steps:
        1. Add multiple families to the database.
        2. Call the `listFamilies` method.

    Expected Outcome:
        - The method returns a status of "ok" and a list of families with correct details.
    """
    session = setup_database
    controller = FamilyController()

    # Add sample families
    family1 = Family(
        idFamily=1,
        familyName="Smith",
        idRoom=101,
        idShelter=201,
        createdBy=1,
        createDate=datetime(2024, 12, 14)
    )
    family2 = Family(
        idFamily=2,
        familyName="Johnson",
        idRoom=102,
        idShelter=202,
        createdBy=2,
        createDate=datetime(2024, 12, 15)
    )
    session.add_all([family1, family2])
    session.commit()

    # Call the method
    response = controller.listFamilies(session=session)

    # Normalize dates to ISO format
    for family in response["families"]:
        family["createDate"] = datetime.fromisoformat(family["createDate"]).isoformat()

    # Expected result
    expected_response = {
        "status": "ok",
        "families": [
            {
                "idFamily": 1,
                "familyName": "Smith",
                "idRoom": 101,
                "idShelter": 201,
                "createdBy": 1,
                "createDate": "2024-12-14T00:00:00"
            },
            {
                "idFamily": 2,
                "familyName": "Johnson",
                "idRoom": 102,
                "idShelter": 202,
                "createdBy": 2,
                "createDate": "2024-12-15T00:00:00"
            }
        ]
    }

    assert response == expected_response

def test_list_families_empty(setup_database):
    """
    Test: Validate behavior when no families are present in the database.

    Steps:
        1. Ensure the database is empty.
        2. Call the `listFamilies` method.

    Expected Outcome:
        - The method returns a status of "ok" with an empty list.
    """
    session = setup_database
    controller = FamilyController()

    # Ensure no families are in the database
    response = controller.listFamilies(session=session)

    assert response == {"status": "ok", "families": []}

def test_list_families_sqlalchemy_error(mocker, setup_database):
    """
    Test: Validate behavior when a SQLAlchemyError occurs during the query.

    Steps:
        1. Mock the session to raise a SQLAlchemyError during query execution.
        2. Call the `listFamilies` method.

    Expected Outcome:
        - The method returns a status of "error" with the error message.
    """
    session = setup_database
    controller = FamilyController()

    # Mock session.query to raise SQLAlchemyError
    mocker.patch.object(session, "query", side_effect=SQLAlchemyError("Database error"))

    response = controller.listFamilies(session=session)

    assert response == {"status": "error", "message": "Database error"}

def test_list_families_unexpected_exception(mocker, setup_database):
    """
    Test: Validate behavior when an unexpected exception occurs.

    Steps:
        1. Mock the session to raise a generic exception during query execution.
        2. Call the `listFamilies` method.

    Expected Outcome:
        - The method returns a status of "error" with the exception message.
    """
    session = setup_database
    controller = FamilyController()

    # Mock session.query to raise a generic Exception
    mocker.patch.object(session, "query", side_effect=Exception("Unexpected error"))

    response = controller.listFamilies(session=session)

    assert response == {"status": "error", "message": "Unexpected error"}
