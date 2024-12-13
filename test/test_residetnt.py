import pytest
from app.controllers.resident_controller import ResidentController
from app.models.resident import Resident as ResidentModel
from app.mysql.resident import Resident
from app.mysql.room import Room
from app.mysql.family import Family
from app.mysql.shelter import Shelter
from datetime import date

def test_create_resident_success(setup_database):
    session = setup_database
    controller = ResidentController()

    # Add required family, room, and shelter
    shelter = Shelter(idShelter=1, shelterName="Main Shelter", maxPeople=10)
    room = Room(idRoom=1, roomName="Room A", maxPeople=4, idShelter=1)
    family = Family(idFamily=1, familyName="Doe Family", idRoom=1, idShelter=1)
    session.add_all([shelter, room, family])
    session.commit()

    # Resident data
    resident_data = ResidentModel(
        idResident=1,  # Autogenerado en MySQL, pero necesario para Pydantic
        name="John",
        surname="Doe",
        birthDate=date(1990, 1, 1),
        gender="M",
        createdBy=1,
        createDate=date.today(),
        idRoom=1,  # Requerido por el modelo
        idFamily=1
    )

    response = controller.create_resident(resident_data, session=session)

    assert response == {"status": "ok"}

    added_resident = session.query(Resident).filter_by(name="John", surname="Doe").first()
    assert added_resident is not None
    assert added_resident.idFamily == 1
    assert added_resident.idRoom == 1


def test_create_resident_family_not_exist(setup_database):
    session = setup_database
    controller = ResidentController()

    # Resident data with nonexistent family
    resident_data = ResidentModel(
        idResident=1,
        name="John",
        surname="Doe",
        birthDate=date(1990, 1, 1),
        gender="M",
        createdBy=1,
        createDate=date.today(),
        idRoom=1,
        idFamily=999  # Nonexistent family
    )

    response = controller.create_resident(resident_data, session=session)

    assert response == {"status": "error", "message": "The family does not exist."}

    resident_count = session.query(Resident).count()
    assert resident_count == 0


def test_create_resident_family_no_room(setup_database):
    session = setup_database
    controller = ResidentController()

    # Add required shelter and family without room
    shelter = Shelter(idShelter=1, shelterName="Main Shelter", maxPeople=10)
    family = Family(idFamily=1, familyName="Doe Family", idRoom=None, idShelter=1)
    session.add_all([shelter, family])
    session.commit()

    # Resident data
    resident_data = ResidentModel(
        idResident=1,
        name="John",
        surname="Doe",
        birthDate=date(1990, 1, 1),
        gender="M",
        createdBy=1,
        createDate=date.today(),
        idRoom=None,  # No room assigned
        idFamily=1
    )

    response = controller.create_resident(resident_data, session=session)

    assert response == {"status": "error", "message": "The family does not have an assigned room."}

    resident_count = session.query(Resident).count()
    assert resident_count == 0


def test_create_resident_duplicate(setup_database):
    session = setup_database
    controller = ResidentController()

    # Add required family, room, shelter, and resident
    shelter = Shelter(idShelter=1, shelterName="Main Shelter", maxPeople=10)
    room = Room(idRoom=1, roomName="Room A", maxPeople=4, idShelter=1)
    family = Family(idFamily=1, familyName="Doe Family", idRoom=1, idShelter=1)
    resident = Resident(idResident=1, name="John", surname="Doe", birthDate=date(1990, 1, 1), gender="M", createdBy=1, idFamily=1, idRoom=1)
    session.add_all([shelter, room, family, resident])
    session.commit()

    # Attempt to create duplicate resident
    resident_data = ResidentModel(
        idResident=2,
        name="John",
        surname="Doe",
        birthDate=date(1990, 1, 1),
        gender="M",
        createdBy=1,
        createDate=date.today(),
        idRoom=1,
        idFamily=1
    )

    response = controller.create_resident(resident_data, session=session)

    assert response == {"status": "error", "message": "Resident already exists in this room."}

    resident_count = session.query(Resident).count()
    assert resident_count == 1


def test_create_resident_shelter_full(setup_database):
    session = setup_database
    controller = ResidentController()

    # Add required shelter, family, and residents to reach shelter capacity
    shelter = Shelter(idShelter=1, shelterName="Main Shelter", maxPeople=2)
    room = Room(idRoom=1, roomName="Room A", maxPeople=4, idShelter=1)
    family = Family(idFamily=1, familyName="Doe Family", idRoom=1, idShelter=1)
    resident1 = Resident(idResident=1, name="Alice", surname="Doe", birthDate=date(1990, 1, 1), gender="F", createdBy=1, idFamily=1, idRoom=1)
    resident2 = Resident(idResident=2, name="Bob", surname="Doe", birthDate=date(1992, 2, 2), gender="M", createdBy=1, idFamily=1, idRoom=1)
    session.add_all([shelter, room, family, resident1, resident2])
    session.commit()

    # Attempt to add another resident
    resident_data = ResidentModel(
        idResident=3,
        name="John",
        surname="Doe",
        birthDate=date(1995, 3, 3),
        gender="M",
        createdBy=1,
        createDate=date.today(),
        idRoom=1,
        idFamily=1
    )

    response = controller.create_resident(resident_data, session=session)

    assert response == {"status": "error", "message": "Shelter is full."}

    resident_count = session.query(Resident).count()
    assert resident_count == 2

def test_list_residents_in_room(setup_database):
    """
    Test: Verify that the method returns all residents in a specific room.

    Steps:
        1. Add residents to multiple rooms in the database.
        2. Call the `list_residents_in_room` method for a specific room.
        3. Verify the response includes the correct residents for the given room.

    Expected Outcome:
        - The returned list contains only the residents assigned to the specified room.
    """
    session = setup_database
    controller = ResidentController()

    # Add required rooms and residents
    room1 = Room(idRoom=1, roomName="Room A", maxPeople=4, idShelter=1, createdBy=1, createDate=date.today())
    room2 = Room(idRoom=2, roomName="Room B", maxPeople=4, idShelter=1, createdBy=1, createDate=date.today())
    resident1 = Resident(name="John", surname="Doe", birthDate=date(1990, 1, 1), gender="M", createdBy=1, idFamily=1, idRoom=1)
    resident2 = Resident(name="Jane", surname="Doe", birthDate=date(1992, 6, 15), gender="F", createdBy=1, idFamily=1, idRoom=1)
    resident3 = Resident(name="Alice", surname="Brown", birthDate=date(1995, 3, 10), gender="F", createdBy=1, idFamily=1, idRoom=2)
    session.add_all([room1, room2, resident1, resident2, resident3])
    session.commit()

    # Call the method
    response = controller.list_residents_in_room(idRoom=1, session=session)

    # Verify the response
    assert response["status"] == "ok"
    assert len(response["residents"]) == 2
    assert response["residents"][0]["name"] == "John"
    assert response["residents"][1]["name"] == "Jane"


def test_list_residents_in_room_no_residents(setup_database):
    """
    Test: Verify that the method returns an empty list when no residents are in the specified room.

    Steps:
        1. Add rooms without residents to the database.
        2. Call the `list_residents_in_room` method for a specific room.
        3. Verify the response is an empty list.

    Expected Outcome:
        - The returned list is empty.
    """
    session = setup_database
    controller = ResidentController()

    # Add a room without residents
    room = Room(idRoom=1, roomName="Room A", maxPeople=4, idShelter=1, createdBy=1, createDate=date.today())
    session.add(room)
    session.commit()

    # Call the method
    response = controller.list_residents_in_room(idRoom=1, session=session)

    # Verify the response
    assert response["status"] == "ok"
    assert len(response["residents"]) == 0


def test_list_residents(setup_database):
    """
    Test: Verify that the method returns all residents in the database.

    Steps:
        1. Add multiple residents to the database.
        2. Call the `list_residents` method.
        3. Verify the response includes all residents.

    Expected Outcome:
        - The returned list contains all residents in the database.
    """
    session = setup_database
    controller = ResidentController()

    # Add residents
    resident1 = Resident(name="John", surname="Doe", birthDate=date(1990, 1, 1), gender="M", createdBy=1, idFamily=1, idRoom=1)
    resident2 = Resident(name="Jane", surname="Doe", birthDate=date(1992, 6, 15), gender="F", createdBy=1, idFamily=1, idRoom=1)
    session.add_all([resident1, resident2])
    session.commit()

    # Call the method
    response = controller.list_residents(session=session)

    # Verify the response
    assert response["status"] == "ok"
    assert len(response["residents"]) == 2
    assert response["residents"][0]["name"] == "John"
    assert response["residents"][1]["name"] == "Jane"


def test_list_residents_no_residents(setup_database):
    """
    Test: Verify that the method returns an empty list when there are no residents in the database.

    Steps:
        1. Ensure no residents are added to the database.
        2. Call the `list_residents` method.
        3. Verify the response is an empty list.

    Expected Outcome:
        - The returned list is empty.
    """
    session = setup_database
    controller = ResidentController()

    # Call the method
    response = controller.list_residents(session=session)

    # Verify the response
    assert response["status"] == "ok"
    assert len(response["residents"]) == 0

def test_delete_resident_success(setup_database):
    """
    Test: Successfully delete an existing resident.

    Expected Outcome:
        - The resident is removed from the database.
    """
    session = setup_database
    controller = ResidentController()

    # Add a test resident
    resident = Resident(
        idResident=1,
        name="John",
        surname="Doe",
        birthDate=date(1990, 1, 1),
        gender="M",
        createdBy=1,
        createDate=date.today(),
        idFamily=None,
        idRoom=None
    )
    session.add(resident)
    session.commit()

    # Call the method
    response = controller.delete_resident(idResident=1, session=session)

    # Assert the response
    assert response == {"status": "ok"}

    # Verify the resident is deleted from the database
    deleted_resident = session.query(Resident).filter_by(idResident=1).first()
    assert deleted_resident is None


def test_delete_resident_not_found(setup_database):
    """
    Test: Attempt to delete a non-existent resident.

    Expected Outcome:
        - Returns a "not found" status.
    """
    session = setup_database
    controller = ResidentController()

    # Call the method with a non-existent resident ID
    response = controller.delete_resident(idResident=999, session=session)

    # Assert the response
    assert response == {"status": "not found"}

def test_update_resident_success(setup_database):
    """
    Test: Successfully update an existing resident's details.

    Expected Outcome:
        - The resident's details are updated in the database.
    """
    session = setup_database
    controller = ResidentController()

    # Add a test resident
    resident = Resident(
        idResident=1,
        name="John",
        surname="Doe",
        birthDate=date(1990, 1, 1),
        idRoom=1,
        createDate=date.today()
    )
    session.add(resident)
    session.commit()

    # Updates to apply
    updates = {
        "name": "Jane",
        "surname": "Smith",
        "idRoom": 2,
        "update": date(2024, 12, 10)
    }

    # Call the method
    response = controller.update_resident(idResident=1, updates=updates, session=session)

    # Assert response
    assert response == {"status": "ok"}

    # Verify updates in the database
    updated_resident = session.query(Resident).filter_by(idResident=1).first()
    assert updated_resident is not None
    assert updated_resident.name == "Jane"
    assert updated_resident.surname == "Smith"
    assert updated_resident.idRoom == 2
    assert updated_resident.update == date(2024, 12, 10)


def test_update_resident_not_found(setup_database):
    """
    Test: Attempt to update a non-existent resident.

    Expected Outcome:
        - Returns a "not found" status.
    """
    session = setup_database
    controller = ResidentController()

    # Updates to apply
    updates = {"name": "Jane", "surname": "Smith"}

    # Call the method
    response = controller.update_resident(idResident=999, updates=updates, session=session)

    # Assert response
    assert response == {"status": "not found"}


def test_update_resident_no_valid_fields(setup_database):
    """
    Test: Attempt to update a resident with invalid fields.

    Expected Outcome:
        - The update skips invalid fields, and the valid ones are applied.
    """
    session = setup_database
    controller = ResidentController()

    # Add a test resident
    resident = Resident(
        idResident=1,
        name="John",
        surname="Doe",
        idRoom=1,
        createDate=date.today()
    )
    session.add(resident)
    session.commit()

    # Updates with invalid fields
    updates = {
        "nonexistent_field": "value",
        "name": "Jane"
    }

    # Call the method
    response = controller.update_resident(idResident=1, updates=updates, session=session)

    # Assert response
    assert response == {"status": "ok"}

    # Verify updates in the database
    updated_resident = session.query(Resident).filter_by(idResident=1).first()
    assert updated_resident is not None
    assert updated_resident.name == "Jane"
    assert updated_resident.surname == "Doe"  # Not changed
    assert not hasattr(updated_resident, "nonexistent_field")

def test_get_resident_by_id_success(setup_database):
    """
    Test: Successfully retrieve a resident by their ID.

    Expected Outcome:
        - The resident's details are returned with a success status.
    """
    session = setup_database
    controller = ResidentController()

    # Add a test resident
    resident = Resident(
        idResident=1,
        name="John",
        surname="Doe",
        birthDate=date(1990, 1, 1),
        gender="M",
        idFamily=101,
        createDate=date(2024, 12, 1)
    )
    session.add(resident)
    session.commit()

    # Call the method
    response = controller.getResidentById(idResident=1, session=session)

    # Assert the response
    assert response == {
        "status": "ok",
        "resident": {
            "idResident": 1,
            "name": "John",
            "surname": "Doe",
            "birthDate": date(1990, 1, 1),
            "gender": "M",
            "idFamily": 101,
        },
    }


def test_get_resident_by_id_not_found(setup_database):
    """
    Test: Attempt to retrieve a resident with an ID that does not exist.

    Expected Outcome:
        - Returns an error indicating the resident was not found.
    """
    session = setup_database
    controller = ResidentController()

    # Call the method with a non-existent ID
    response = controller.getResidentById(idResident=999, session=session)

    # Assert the response
    assert response == {"status": "error", "message": "Residente no encontrado"}


def test_get_resident_by_id_database_error(setup_database, mocker):
    """
    Test: Simulate a database error when retrieving a resident.

    Expected Outcome:
        - Returns an error indicating a database issue.
    """
    session = setup_database
    controller = ResidentController()

    # Mock session.query to raise an exception
    mocker.patch("sqlalchemy.orm.Session.query", side_effect=Exception("Database error"))

    # Call the method
    response = controller.getResidentById(idResident=1, session=session)

    # Assert the response
    assert response["status"] == "error"
    assert "Database error" in response["message"]

def test_update_resident_name_success(setup_database):
    """
    Test: Successfully update the name of a resident.

    Expected Outcome:
        - The resident's name is updated successfully in the database.
    """
    session = setup_database
    controller = ResidentController()

    # Add a test resident
    resident = Resident(
        idResident=1,
        name="John",
        surname="Doe",
        birthDate=date(1990, 1, 1),
        gender="M",
        createDate=date(2024, 12, 1)
    )
    session.add(resident)
    session.commit()

    # Call the method to update the name
    response = controller.updateResidentName(idResident=1, new_name="Jane", session=session)

    # Assert the response
    assert response == {"status": "ok", "message": "Nombre actualizado exitosamente"}

    # Verify the resident's name is updated in the database
    updated_resident = session.query(Resident).filter_by(idResident=1).first()
    assert updated_resident is not None
    assert updated_resident.name == "Jane"


def test_update_resident_name_not_found(setup_database):
    """
    Test: Attempt to update the name of a non-existent resident.

    Expected Outcome:
        - Returns an error indicating the resident was not found.
    """
    session = setup_database
    controller = ResidentController()

    # Call the method with a non-existent ID
    response = controller.updateResidentName(idResident=999, new_name="Jane", session=session)

    # Assert the response
    assert response == {"status": "error", "message": "Residente no encontrado"}

def test_update_resident_surname_success(setup_database):
    """
    Test: Successfully update the surname of a resident.

    Expected Outcome:
        - The resident's surname is updated successfully in the database.
    """
    session = setup_database
    controller = ResidentController()

    # Add a test resident
    resident = Resident(
        idResident=1,
        name="John",
        surname="Doe",
        birthDate=date(1990, 1, 1),
        gender="M",
        createDate=date(2024, 12, 1)
    )
    session.add(resident)
    session.commit()

    # New surname
    new_surname = "Smith"

    # Call the method
    response = controller.updateResidentSurname(idResident=1, new_surname=new_surname, session=session)

    # Assert the response
    assert response == {"status": "ok", "message": "Apellido actualizado exitosamente"}

    # Verify the surname is updated in the database
    updated_resident = session.query(Resident).filter_by(idResident=1).first()
    assert updated_resident is not None
    assert updated_resident.surname == new_surname

def test_update_resident_surname_not_found(setup_database):
    """
    Test: Attempt to update the surname of a non-existent resident.

    Expected Outcome:
        - Returns an error indicating the resident was not found.
    """
    session = setup_database
    controller = ResidentController()

    # Call the method for a non-existent resident
    response = controller.updateResidentSurname(idResident=999, new_surname="Smith", session=session)

    # Assert the response
    assert response == {"status": "error", "message": "Residente no encontrado"}

