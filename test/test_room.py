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
from unittest.mock import MagicMock
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError



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
        roomName="Room 1",
        createdBy=1,
        createDate=date.today(),
        idShelter=1,
        maxPeople=4
    )

    response = controller.create_room(room_data, session=session)

    assert response == {"status": "ok"}

    added_room = session.query(Room).filter_by(roomName="Room 1").first()
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
        roomName="Room 1",
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
        roomName="Room 1",
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
    room = Room(idRoom=1, roomName="Room 1", createdBy=1, createDate=date.today(), idShelter=1, maxPeople=4)
    session.add_all([admin, shelter, room])
    session.commit()

    # Duplicate room data
    room_data = RoomModel(
        idRoom=2,
        roomName="Room 1",  # Duplicate name
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
    room1 = Room(idRoom=1, roomName="Room 1", maxPeople=4, idShelter=1)
    room2 = Room(idRoom=2, roomName="Room 2", maxPeople=3, idShelter=1)
    resident1 = Resident(idResident=1, name="Alice", surname="Doe", idRoom=1)
    resident2 = Resident(idResident=2, name="Bob", surname="Doe", idRoom=1)
    resident3 = Resident(idResident=3, name="Charlie", surname="Doe", idRoom=2)
    session.add_all([shelter, room1, room2, resident1, resident2, resident3])
    session.commit()

    # Get room list with resident counts
    response = controller.list_rooms_with_resident_count(session=session)

    assert len(response) == 2
    assert response[0]["roomName"] == "Room 1"
    assert response[0]["resident_count"] == 2
    assert response[1]["roomName"] == "Room 2"
    assert response[1]["resident_count"] == 1


def test_access_room_resident_not_found(setup_database):
    """
    Test: Verify that attempting to access a room with a non-existent resident returns the correct error message.

    Steps:
        1. Use a resident ID that does not exist in the database.
        2. Call the `access_room` method with the invalid resident ID and a valid room ID.
        3. Verify that the method returns the appropriate error message.

    Expected Outcome:
        - The method should return "Resident not found." when the resident ID does not exist.
    """

    session = setup_database
    controller = RoomController()

    response = controller.access_room(idResident=999, idRoom=1, session=session)
    assert response == "Resident not found."

def test_access_room_room_not_found(setup_database):
    """
    Test: Verify that attempting to access a non-existent room returns the correct error message.

    Steps:
        1. Add a valid resident to the database.
        2. Use a room ID that does not exist in the database.
        3. Call the `access_room` method with the valid resident ID and invalid room ID.
        4. Verify that the method returns the appropriate error message.

    Expected Outcome:
        - The method should return "Room not found." when the room ID does not exist.
    """

    session = setup_database
    controller = RoomController()

    resident = Resident(idResident=1, idFamily=1, name="John", surname="Doe")
    session.add(resident)
    session.commit()

    response = controller.access_room(idResident=1, idRoom=999, session=session)
    assert response == "Room not found."

def test_access_room_maintenance_room(setup_database):
    """
    Test: Verify that access to a maintenance room is denied.

    Steps:
        1. Add a valid resident to the database.
        2. Add a room named "Mantenimiento" to the database.
        3. Call the `access_room` method with the resident ID and the maintenance room ID.
        4. Verify that the method denies access with the appropriate error message.

    Expected Outcome:
        - The method should return "Access denied. No puedes entrar a la sala de mantenimiento."
          when a resident tries to access a maintenance room.
    """

    session = setup_database
    controller = RoomController()

    resident = Resident(idResident=1, idFamily=1, name="John", surname="Doe")
    room = Room(idRoom=1, roomName="Mantenimiento", maxPeople=10)
    session.add_all([resident, room])
    session.commit()

    response = controller.access_room(idResident=1, idRoom=1, session=session)
    assert response == "Access denied. No puedes entrar a la sala de mantenimiento."

def test_access_room_full_room(setup_database):
    """
    Test: Verify that access is denied when the room is at full capacity.

    Steps:
        1. Add a room with a maximum capacity of 2 to the database.
        2. Add two residents assigned to the room to fill it to capacity.
        3. Add a new resident who will attempt to access the full room.
        4. Call the `access_room` method with the new resident's ID and the room ID.
        5. Verify that the method denies access with the appropriate error message.

    Expected Outcome:
        - The method should return "Access denied. La sala está llena."
          when a resident tries to enter a room that has reached its maximum capacity.
    """

    session = setup_database
    controller = RoomController()

    room = Room(idRoom=1, roomName="Room 1", maxPeople=2)
    resident1 = Resident(idResident=1, idFamily=1, idRoom=1, name="John", surname="Doe")
    resident2 = Resident(idResident=2, idFamily=1, idRoom=1, name="Jane", surname="Doe")
    session.add_all([room, resident1, resident2])
    session.commit()

    new_resident = Resident(idResident=3, idFamily=1, name="Jack", surname="Smith")
    session.add(new_resident)
    session.commit()

    response = controller.access_room(idResident=3, idRoom=1, session=session)
    assert response == "Access denied. La sala está llena."

def test_access_room_public_room(setup_database):
    """
    Test: Verify that access is granted when the resident attempts to enter a public room.

    Steps:
        1. Add a resident to the database.
        2. Add a room labeled as a "Common Area" with sufficient capacity.
        3. Call the `access_room` method with the resident's ID and the room ID.
        4. Verify that access is granted with the appropriate success message.

    Expected Outcome:
        - The method should return "Access granted. Welcome to the room."
          when a resident successfully accesses a public room.
    """

    session = setup_database
    controller = RoomController()

    resident = Resident(idResident=1, idFamily=1, name="John", surname="Doe")
    room = Room(idRoom=1, roomName="Common Area", maxPeople=10)
    session.add_all([resident, room])
    session.commit()

    response = controller.access_room(idResident=1, idRoom=1, session=session)
    assert response == "Access granted. Welcome to the room."

def test_access_room_family_room(setup_database):
    """
    Test: Verify that access is granted when a resident enters their assigned family room.

    Steps:
        1. Add a family with an assigned room to the database.
        2. Add a resident belonging to that family.
        3. Add the corresponding room with sufficient capacity.
        4. Call the `access_room` method with the resident's ID and the room ID.
        5. Verify that access is granted with the appropriate success message.

    Expected Outcome:
        - The method should return "Access granted. Welcome to the room."
          when the resident accesses their assigned family room.
    """

    session = setup_database
    controller = RoomController()

    family = Family(idFamily=1, idRoom=1, familyName="Smith")
    resident = Resident(idResident=1, idFamily=1, name="John", surname="Doe")
    room = Room(idRoom=1, roomName="Room 101", maxPeople=10)
    session.add_all([family, resident, room])
    session.commit()

    response = controller.access_room(idResident=1, idRoom=1, session=session)
    assert response == "Access granted. Welcome to the room."

def test_access_room_wrong_room(setup_database):
    """
    Test: Verify that access is denied when a resident attempts to enter a room not assigned to their family.

    Steps:
        1. Add two families, each assigned to a different room.
        2. Add a resident belonging to the first family.
        3. Add a room associated with the second family.
        4. Call the `access_room` method with the resident's ID and the second room's ID.
        5. Verify that access is denied with the appropriate error message.

    Expected Outcome:
        - The method should return "Access denied. You are in the wrong room."
          when the resident attempts to access a room they are not assigned to.
    """

    session = setup_database
    controller = RoomController()

    family1 = Family(idFamily=1, idRoom=1, familyName="Smith")
    family2 = Family(idFamily=2, idRoom=2, familyName="Johnson")
    resident = Resident(idResident=1, idFamily=1, name="John", surname="Doe")
    room = Room(idRoom=2, roomName="Room 102", maxPeople=10)
    session.add_all([family1, family2, resident, room])
    session.commit()

    response = controller.access_room(idResident=1, idRoom=2, session=session)
    assert response == "Access denied. You are in the wrong room."

def test_list_rooms_success(setup_database):
    """
    Test: Validate successful retrieval of rooms from the database.

    Steps:
        1. Add multiple rooms to the database.
        2. Call the `list_rooms` method.

    Expected Outcome:
        - The method returns a list of rooms with correct details.
    """
    session = setup_database
    controller = RoomController()

    # Add sample rooms
    room1 = Room(
        idRoom=1,
        roomName="Room 1",
        maxPeople=10,
        idShelter=1,
        createDate=datetime(2024, 12, 1)
    )
    room2 = Room(
        idRoom=2,
        roomName="Room 2",
        maxPeople=8,
        idShelter=2,
        createDate=datetime(2024, 12, 2)
    )
    session.add_all([room1, room2])
    session.commit()

    # Call the method
    response = controller.list_rooms(session=session)

    # Normalize the createDate format in the response
    for room in response:
        room['createDate'] = room['createDate'] + "T00:00:00"

    # Expected result
    expected_response = [
        {
            "idRoom": 1,
            "roomName": "Room 1",
            "maxPeople": 10,
            "idShelter": 1,
            "createDate": "2024-12-01T00:00:00"
        },
        {
            "idRoom": 2,
            "roomName": "Room 2",
            "maxPeople": 8,
            "idShelter": 2,
            "createDate": "2024-12-02T00:00:00"
        }
    ]

    assert response == expected_response

def test_list_rooms_empty(setup_database):
    """
    Test: Validate behavior when no rooms are present in the database.

    Steps:
        1. Ensure the database is empty.
        2. Call the `list_rooms` method.

    Expected Outcome:
        - The method returns an empty list.
    """
    session = setup_database
    controller = RoomController()

    # Ensure no rooms are in the database
    response = controller.list_rooms(session=session)

    assert response == []

def test_list_rooms_sqlalchemy_error(mocker, setup_database):
    """
    Test: Validate behavior when a SQLAlchemyError occurs during the query.

    Steps:
        1. Mock the session to raise a SQLAlchemyError during query execution.
        2. Call the `list_rooms` method.

    Expected Outcome:
        - The method returns a status of "error" with the error message.
    """
    session = setup_database
    controller = RoomController()

    # Mock session.query to raise SQLAlchemyError
    mocker.patch.object(session, "query", side_effect=SQLAlchemyError("Database error"))

    response = controller.list_rooms(session=session)

    assert response == {"status": "error", "message": "Database error"}

def test_list_rooms_unexpected_exception(mocker, setup_database):
    """
    Test: Validate behavior when an unexpected exception occurs.

    Steps:
        1. Mock the session to raise a generic exception during query execution.
        2. Call the `list_rooms` method.

    Expected Outcome:
        - The method returns a status of "error" with the exception message.
    """
    session = setup_database
    controller = RoomController()

    # Mock session.query to raise a generic Exception
    mocker.patch.object(session, "query", side_effect=Exception("Unexpected error"))

    response = controller.list_rooms(session=session)

    assert response == {"status": "error", "message": "Unexpected error"}

def test_update_room_name_success(setup_database):
    """
    Test: Successfully update the name of an existing room.

    Steps:
        1. Add a room to the database with an initial name.
        2. Call `updateRoomName` to update the room's name.
        3. Verify the response and ensure the name is updated in the database.

    Expected Outcome:
        - Response indicates success.
        - The room's name is updated in the database.
    """
    session = setup_database
    controller = RoomController()

    # Add a room to the database
    room = Room(idRoom=1, roomName="Old Room Name", maxPeople=10)
    session.add(room)
    session.commit()

    # Update the room's name
    new_name = "New Room Name"
    response = controller.updateRoomName(idRoom=1, new_name=new_name, session=session)

    # Verify the response and database update
    updated_room = session.query(Room).filter_by(idRoom=1).first()
    assert response == {"status": "ok", "message": "Nombre de la habitación actualizado exitosamente"}
    assert updated_room.roomName == new_name

def test_update_room_name_room_not_found(setup_database):
    """
    Test: Attempt to update the name of a non-existent room.

    Steps:
        1. Ensure the database is empty.
        2. Call `updateRoomName` with a non-existent room ID.
        3. Verify the response indicates the room was not found.

    Expected Outcome:
        - Response indicates the room was not found.
    """
    session = setup_database
    controller = RoomController()

    # Attempt to update a non-existent room
    response = controller.updateRoomName(idRoom=999, new_name="New Name", session=session)

    # Verify the response
    assert response == {"status": "error", "message": "Habitación no encontrada"}

def test_update_room_name_sqlalchemy_error(mocker, setup_database):
    """
    Test: Simulate a SQLAlchemyError during the operation.

    Steps:
        1. Mock the session to raise a SQLAlchemyError when querying the database.
        2. Call `updateRoomName`.
        3. Verify the response indicates a database error.

    Expected Outcome:
        - Response indicates a database error occurred.
    """
    session = setup_database
    controller = RoomController()

    # Mock session.query to raise SQLAlchemyError
    mocker.patch.object(session, "query", side_effect=SQLAlchemyError("Database error"))

    response = controller.updateRoomName(idRoom=1, new_name="New Name", session=session)

    assert response == {"status": "error", "message": "Error de base de datos: Database error"}

def test_update_room_name_unexpected_exception(mocker, setup_database):
    """
    Test: Simulate an unexpected exception during the operation.

    Steps:
        1. Mock the session to raise a generic exception when querying the database.
        2. Call `updateRoomName`.
        3. Verify the response indicates an unexpected error occurred.

    Expected Outcome:
        - Response indicates an unexpected error occurred.
    """
    session = setup_database
    controller = RoomController()

    # Mock session.query to raise a generic Exception
    mocker.patch.object(session, "query", side_effect=Exception("Unexpected error"))

    response = controller.updateRoomName(idRoom=1, new_name="New Name", session=session)

    assert response == {"status": "error", "message": "Unexpected error"}

def test_list_rooms_room_success(setup_database):
    """
    Test: Successfully list rooms with names starting with "Room".

    Steps:
        1. Add multiple rooms to the database, including ones with and without names starting with "Room".
        2. Call `list_rooms_Room` to fetch the rooms.
        3. Verify the response contains only rooms whose names start with "Room".

    Expected Outcome:
        - Response contains only rooms with names starting with "Room".
    """
    session = setup_database
    controller = RoomController()

    # Add rooms to the database
    room1 = Room(idRoom=1, roomName="Room Alpha", maxPeople=10)
    room2 = Room(idRoom=2, roomName="Hall Beta", maxPeople=15)
    room3 = Room(idRoom=3, roomName="Room Gamma", maxPeople=8)
    session.add_all([room1, room2, room3])
    session.commit()

    # Call the method
    response = controller.list_rooms_Room(session=session)

    # Expected response
    expected_response = [
        {"idRoom": 1, "roomName": "Room Alpha", "maxPeople": 10, "idShelter": None, "createDate": None},
        {"idRoom": 3, "roomName": "Room Gamma", "maxPeople": 8, "idShelter": None, "createDate": None}
    ]

    # Assert
    assert response == expected_response

def test_list_rooms_room_no_matches(setup_database):
    """
    Test: No rooms with names starting with "Room".

    Steps:
        1. Add rooms to the database with names not starting with "Room".
        2. Call `list_rooms_Room` to fetch the rooms.
        3. Verify the response is an empty list.

    Expected Outcome:
        - Response is an empty list.
    """
    session = setup_database
    controller = RoomController()

    # Add rooms with names not starting with "Room"
    room1 = Room(idRoom=1, roomName="Hall Alpha", maxPeople=10)
    room2 = Room(idRoom=2, roomName="Conference Beta", maxPeople=20)
    session.add_all([room1, room2])
    session.commit()

    # Call the method
    response = controller.list_rooms_Room(session=session)

    # Assert
    assert response == []

def test_list_rooms_room_unexpected_exception(mocker, setup_database):
    """
    Test: Simulate an unexpected exception during the operation.

    Steps:
        1. Mock the session to raise a generic exception when querying the database.
        2. Call `list_rooms_Room`.
        3. Verify the response indicates an error occurred.

    Expected Outcome:
        - Response indicates an error occurred.
    """
    session = setup_database
    controller = RoomController()

    # Mock session.query to raise a generic Exception
    mocker.patch.object(session, "query", side_effect=Exception("Unexpected error"))

    response = controller.list_rooms_Room(session=session)

    # Assert
    assert response == {"status": "error", "message": "Unexpected error"}
