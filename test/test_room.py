import pytest
from app.controllers.room_controller import RoomController
from app.models.room import Room as RoomModel
from app.mysql.room import Room
from app.mysql.shelter import Shelter
from app.mysql.admin import Admin
from app.mysql.resident import Resident
from app.mysql.family import Family
from app.mysql.shelter import Shelter
from datetime import date


def test_create_room_success(setup_database):
    """
    Test: Successfully create a new room.

    Steps:
        1. Add an admin and shelter to the database.
        2. Call the `create_room` method with valid data.
        3. Verify the response indicates success.
        4. Confirm the room exists in the database with correct details.

    Expected Outcome:
        - The room should be successfully created and associated with the shelter.
    """
    session = setup_database
    controller = RoomController()

    # Add required admin and shelter
    admin = Admin(idAdmin=1, email="admin@example.com", name="Admin Name", password="password")
    shelter = Shelter(idShelter=1, shelterName="Main Shelter")
    session.add_all([admin, shelter])
    session.commit()

    # Room data
    room_data = RoomModel(
        idRoom=1,
        roomName="Room A",
        createdBy=1,
        createDate=date.today(),
        idShelter=1,
        maxPeople=4
    )

    response = controller.create_room(room_data, session=session)

    assert response == {"status": "ok"}

    added_room = session.query(Room).filter_by(roomName="Room A").first()
    assert added_room is not None
    assert added_room.idShelter == 1
    assert added_room.maxPeople == 4


def test_create_room_admin_not_exist(setup_database):
    """
    Test: Prevent creating a room when the admin does not exist.

    Steps:
        1. Call the `create_room` method with a nonexistent admin ID.
        2. Verify the response indicates the admin does not exist.

    Expected Outcome:
        - The operation should fail with an error message about the admin.
    """
    session = setup_database
    controller = RoomController()

    # Add shelter
    shelter = Shelter(idShelter=1, shelterName="Main Shelter")
    session.add(shelter)
    session.commit()

    # Room data with nonexistent admin
    room_data = RoomModel(
        idRoom=1,
        roomName="Room A",
        createdBy=999,  # Nonexistent admin
        createDate=date.today(),
        idShelter=1,
        maxPeople=4
    )

    response = controller.create_room(room_data, session=session)

    assert response == {"status": "error", "message": "The admin does not exist."}

    room_count = session.query(Room).count()
    assert room_count == 0


def test_create_room_shelter_not_exist(setup_database):
    """
    Test: Prevent creating a room when the shelter does not exist.

    Steps:
        1. Call the `create_room` method with a nonexistent shelter ID.
        2. Verify the response indicates the shelter does not exist.

    Expected Outcome:
        - The operation should fail with an error message about the shelter.
    """
    session = setup_database
    controller = RoomController()

    # Add admin
    admin = Admin(idAdmin=1, email="admin@example.com", name="Admin Name", password="password")
    session.add(admin)
    session.commit()

    # Room data with nonexistent shelter
    room_data = RoomModel(
        idRoom=1,
        roomName="Room A",
        createdBy=1,
        createDate=date.today(),
        idShelter=999,  # Nonexistent shelter
        maxPeople=4
    )

    response = controller.create_room(room_data, session=session)

    assert response == {"status": "error", "message": "The shelter does not exist."}

    room_count = session.query(Room).count()
    assert room_count == 0


def test_create_room_duplicate(setup_database):
    """
    Test: Prevent creating a duplicate room in the same shelter.

    Steps:
        1. Add a room to the database.
        2. Attempt to add another room with the same name in the same shelter.
        3. Verify the response indicates duplication.

    Expected Outcome:
        - The operation should fail with an error message about the duplicate room.
    """
    session = setup_database
    controller = RoomController()

    # Add required admin, shelter, and room
    admin = Admin(idAdmin=1, email="admin@example.com", name="Admin Name", password="password")
    shelter = Shelter(idShelter=1, shelterName="Main Shelter")
    room = Room(idRoom=1, roomName="Room A", createdBy=1, createDate=date.today(), idShelter=1, maxPeople=4)
    session.add_all([admin, shelter, room])
    session.commit()

    # Duplicate room data
    room_data = RoomModel(
        idRoom=2,
        roomName="Room A",  # Duplicate name
        createdBy=1,
        createDate=date.today(),
        idShelter=1,
        maxPeople=4
    )

    response = controller.create_room(room_data, session=session)

    assert response == {"status": "error", "message": "The room already exists in this shelter."}

    room_count = session.query(Room).count()
    assert room_count == 1


def test_list_rooms_with_resident_count(setup_database):
    """
    Test: List all rooms along with the count of residents in each room.

    Steps:
        1. Add rooms and residents to the database.
        2. Call the `list_rooms_with_resident_count` method.
        3. Verify the returned data matches the database records.

    Expected Outcome:
        - The room list should include the correct count of residents for each room.
    """
    session = setup_database
    controller = RoomController()

    # Add required shelter, rooms, and residents
    shelter = Shelter(idShelter=1, shelterName="Main Shelter")
    room1 = Room(idRoom=1, roomName="Room A", maxPeople=4, idShelter=1)
    room2 = Room(idRoom=2, roomName="Room B", maxPeople=3, idShelter=1)
    resident1 = Resident(idResident=1, name="Alice", surname="Doe", idRoom=1)
    resident2 = Resident(idResident=2, name="Bob", surname="Doe", idRoom=1)
    resident3 = Resident(idResident=3, name="Charlie", surname="Doe", idRoom=2)
    session.add_all([shelter, room1, room2, resident1, resident2, resident3])
    session.commit()

    # Get room list with resident counts
    response = controller.list_rooms_with_resident_count(session=session)

    assert len(response) == 2
    assert response[0]["roomName"] == "Room A"
    assert response[0]["resident_count"] == 2
    assert response[1]["roomName"] == "Room B"
    assert response[1]["resident_count"] == 1

def test_create_room_duplicate_name_different_shelter(setup_database):
    """
    Test: Successfully create a room with a duplicate name in a different shelter.

    Expected Outcome:
        - The operation should succeed.
    """
    session = setup_database
    controller = RoomController()

    # Add required admin, shelters, and room
    admin = Admin(idAdmin=1, email="admin@example.com", name="Admin Name", password="password")
    shelter1 = Shelter(idShelter=1, shelterName="Shelter 1")
    shelter2 = Shelter(idShelter=2, shelterName="Shelter 2")
    room = Room(idRoom=1, roomName="Room A", createdBy=1, createDate=date.today(), idShelter=1, maxPeople=4)
    session.add_all([admin, shelter1, shelter2, room])
    session.commit()

    # Room data for a different shelter
    room_data = RoomModel(
        idRoom=2,
        roomName="Room A",  # Same name
        createdBy=1,
        createDate=date.today(),
        idShelter=2,  # Different shelter
        maxPeople=4
    )

    response = controller.create_room(room_data, session=session)

    assert response == {"status": "ok"}

def test_list_rooms_Room_no_matches(setup_database):
    """
    Test: List rooms starting with 'Room' when no rooms match.

    Expected Outcome:
        - The response should be an empty list.
    """
    session = setup_database
    controller = RoomController()

    # Add rooms that do not match the pattern
    room1 = Room(idRoom=1, roomName="Kitchen", maxPeople=4, idShelter=1)
    room2 = Room(idRoom=2, roomName="Living Area", maxPeople=3, idShelter=1)
    session.add_all([room1, room2])
    session.commit()

    response = controller.list_rooms_Room(session=session)

    assert response == []

def test_list_rooms_unexpected_error(setup_database, mocker):
    """
    Test: Simulate an unexpected error during listing rooms.

    Expected Outcome:
        - The operation should return an error message.
    """
    session = setup_database
    controller = RoomController()

    # Mock session.query to raise an exception
    mocker.patch("sqlalchemy.orm.Session.query", side_effect=Exception("Unexpected error"))

    response = controller.list_rooms(session=session)

    assert response == {"status": "error", "message": "Unexpected error"}

def test_access_room_resident_not_found(setup_database):
    """
    Test: Attempt to access a room when the resident does not exist.

    Expected Outcome:
        - The operation should return "Resident not found."
    """
    session = setup_database
    controller = RoomController()

    # Add room
    room = Room(idRoom=1, roomName="Room A", maxPeople=4, idShelter=1)
    session.add(room)
    session.commit()

    # Attempt to access the room with a nonexistent resident
    response = controller.access_room(idResident=999, idRoom=1, session=session)

    assert response == "Resident not found."

def test_list_rooms_with_resident_count_unexpected_error(setup_database, mocker):
    """
    Test: Simulate an unexpected error during listing rooms with resident count.

    Steps:
        1. Mock the session's `query` method to raise an exception.
        2. Verify the response indicates an error.
    """
    session = setup_database
    controller = RoomController()

    # Mock session.query to raise an exception
    mocker.patch("sqlalchemy.orm.Session.query", side_effect=Exception("Unexpected error"))

    response = controller.list_rooms_with_resident_count(session=session)

    assert response["status"] == "error"
    assert "Unexpected error" in response["message"]

def test_list_rooms_with_resident_count_empty(setup_database):
    """
    Test: List rooms when no rooms exist in the database.

    Expected Outcome:
        - The response should be an empty list.
    """
    session = setup_database
    controller = RoomController()

    # Call the method without adding any rooms
    response = controller.list_rooms_with_resident_count(session=session)

    assert response == []
