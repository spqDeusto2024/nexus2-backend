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
