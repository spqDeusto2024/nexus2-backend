import pytest
from app.controllers.resident_controller import ResidentController
from app.models.resident import Resident as ResidentModel
from app.mysql.resident import Resident
from app.mysql.room import Room
from app.mysql.family import Family
from app.mysql.shelter import Shelter
from datetime import date
from sqlalchemy.exc import SQLAlchemyError


def test_create_resident_success(setup_database):
    """
    Test the successful creation of a resident in the database.

    This test verifies that a resident can be successfully created in the database
    given the correct setup and input data. It ensures that all necessary entities 
    (shelter, room, family) are added and linked correctly, and that the `create_resident` 
    method of the `ResidentController` functions as expected.

    Parameters:
    ----------
    setup_database : Session
        A pytest fixture that sets up an in-memory SQLite database session 
        for testing purposes.

    Returns:
    -------
    None
        The test asserts various conditions to ensure correctness and does not 
        return any value.
    """
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
    """
    Test the behavior when trying to create a resident with a nonexistent family.

    This test verifies that the `create_resident` method of the `ResidentController` 
    returns an error response if the specified family ID does not exist in the database. 
    It also ensures that no new resident is added to the database in this scenario.

    Parameters:
    ----------
    setup_database : Session
        A pytest fixture that sets up an in-memory SQLite database session 
        for testing purposes.

    Returns:
    -------
    None
        The test asserts various conditions to ensure correctness and does not 
        return any value.
    """
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
    """
    Test the behavior when trying to create a resident whose family does not have an assigned room.

    This test verifies that the `create_resident` method of the `ResidentController` 
    returns an error response if the family associated with the resident does not 
    have an assigned room. It also ensures that no new resident is added to the database 
    in this scenario.

    Parameters:
    ----------
    setup_database : Session
        A pytest fixture that sets up an in-memory SQLite database session 
        for testing purposes.

    Returns:
    -------
    None
        The test asserts various conditions to ensure correctness and does not 
        return any value.
    """
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
    """
    Test the behavior when attempting to create a duplicate resident in the same room.

    This test verifies that the `create_resident` method of the `ResidentController` 
    returns an error response when trying to create a resident with the same name, 
    surname, and birth date as an existing resident in the same room. It also ensures 
    that no duplicate resident is added to the database.

    Parameters:
    ----------
    setup_database : Session
        A pytest fixture that sets up an in-memory SQLite database session 
        for testing purposes.

    Returns:
    -------
    None
        The test asserts various conditions to ensure correctness and does not 
        return any value.
    """
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
    """
    Test the behavior when attempting to create a resident in a shelter that has reached its maximum capacity.

    This test verifies that the `create_resident` method of the `ResidentController` 
    returns an error response when the shelter's `maxPeople` limit has been reached. 
    It ensures no additional residents are added to the database when the shelter is full.

    Parameters:
    ----------
    setup_database : Session
        A pytest fixture that sets up an in-memory SQLite database session 
        for testing purposes.

    Returns:
    -------
    None
        The test asserts various conditions to ensure correctness and does not 
        return any value.
    """
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
    Test the `list_residents_in_room` method to ensure it retrieves all residents in a specified room.

    This test verifies that the `list_residents_in_room` method of the `ResidentController` 
    correctly returns a list of residents assigned to a given room, and that residents in other rooms 
    are not included in the response.

    Steps:
    ------
    1. Add multiple rooms and residents to the database.
    2. Call the `list_residents_in_room` method with the ID of a specific room.
    3. Verify that the returned data includes only the residents assigned to that room.

    Parameters:
    ----------
    setup_database : Session
        A pytest fixture providing an in-memory SQLite database session for testing.

    Returns:
    -------
    None
        The test asserts various conditions to ensure correctness and does not return any value.
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
    Test the `list_residents_in_room` method to ensure it returns an empty list when no residents 
    are assigned to the specified room.

    This test checks that the method correctly handles the case where a room exists, but no residents 
    are associated with it.

    Steps:
    ------
    1. Add a room to the database without any associated residents.
    2. Call the `list_residents_in_room` method with the ID of the room.
    3. Verify that the response contains an empty list of residents.

    Parameters:
    ----------
    setup_database : Session
        A pytest fixture providing an in-memory SQLite database session for testing.

    Returns:
    -------
    None
        The test asserts the expected behavior and does not return any value.
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
    Test the `list_residents` method to ensure it returns all residents in the database.

    This test checks that the method retrieves the correct list of all residents 
    stored in the database.

    Steps:
    ------
    1. Add multiple residents to the database.
    2. Call the `list_residents` method to retrieve the list of residents.
    3. Verify that the response contains all added residents with the correct details.

    Parameters:
    ----------
    setup_database : Session
        A pytest fixture providing an in-memory SQLite database session for testing.

    Returns:
    -------
    None
        The test asserts the expected behavior and does not return any value.
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
    Test the `list_residents` method to ensure it returns an empty list when no residents are present in the database.

    This test verifies the behavior of the method when the database contains no resident records.

    Steps:
    ------
    1. Ensure the database is empty with no residents added.
    2. Call the `list_residents` method to retrieve the list of residents.
    3. Verify that the response contains an empty list.

    Parameters:
    ----------
    setup_database : Session
        A pytest fixture providing an in-memory SQLite database session for testing.

    Returns:
    -------
    None
        The test asserts the expected behavior and does not return any value.
    """

    session = setup_database
    controller = ResidentController()

    # Call the method
    response = controller.list_residents(session=session)

    # Verify the response
    assert response["status"] == "ok"
    assert len(response["residents"]) == 0


def test_update_resident_birthdate_success(setup_database):
    """
    Test: Verify that the method successfully updates a resident's birth date.

    Steps:
        1. Add a resident to the database.
        2. Call the `updateResidentBirthDate` method with a valid new birth date.
        3. Verify the resident's birth date is updated in the database.

    Expected Outcome:
        - The method returns a success message.
        - The resident's birth date is updated in the database.
    """
    session = setup_database
    controller = ResidentController()

    # Add a resident
    resident = Resident(
        idResident=1, name="John", surname="Doe", birthDate=date(1990, 1, 1), gender="M", createdBy=1
    )
    session.add(resident)
    session.commit()

    # Call the method
    response = controller.updateResidentBirthDate(
        idResident=1, new_birthDate="1995-03-10", session=session
    )

    # Verify the response and the database
    assert response["status"] == "ok"
    assert response["message"] == "Fecha de nacimiento actualizada exitosamente"

    updated_resident = session.query(Resident).filter_by(idResident=1).first()
    assert updated_resident.birthDate == date(1995, 3, 10)


def test_update_resident_birthdate_not_found(setup_database):
    """
    Test: Verify that the method handles the case when a resident is not found.

    Steps:
        1. Ensure the database does not contain the specified resident.
        2. Call the `updateResidentBirthDate` method with a non-existent resident ID.
        3. Verify the response indicates the resident is not found.

    Expected Outcome:
        - The method returns an error message indicating the resident is not found.
    """
    session = setup_database
    controller = ResidentController()

    # Call the method
    response = controller.updateResidentBirthDate(
        idResident=999, new_birthDate="1995-03-10", session=session
    )

    # Verify the response
    assert response["status"] == "error"
    assert response["message"] == "Residente no encontrado"


def test_update_resident_birthdate_invalid_format(setup_database):
    """
    Test: Verify that the method handles invalid date formats gracefully.

    Steps:
        1. Add a resident to the database.
        2. Call the `updateResidentBirthDate` method with an invalid date format.
        3. Verify the response indicates a conversion error.

    Expected Outcome:
        - The method returns an error message indicating the date format is invalid.
    """
    session = setup_database
    controller = ResidentController()

    # Add a resident
    resident = Resident(
        idResident=1, name="John", surname="Doe", birthDate=date(1990, 1, 1), gender="M", createdBy=1
    )
    session.add(resident)
    session.commit()

    # Call the method with an invalid date format
    response = controller.updateResidentBirthDate(
        idResident=1, new_birthDate="10-03-1995", session=session  # Invalid format
    )

    # Verify the response
    assert response["status"] == "error"
    assert "does not match format" in response["message"]


def test_update_resident_birthdate_database_error(setup_database, mocker):
    """
    Test: Verify that the method handles database errors gracefully.

    Steps:
        1. Mock the database session to raise an SQLAlchemyError.
        2. Call the `updateResidentBirthDate` method.
        3. Verify the response indicates a database error.

    Expected Outcome:
        - The method returns an error message indicating a database issue.
    """
    session = setup_database
    controller = ResidentController()

    # Mock the commit method to raise an exception
    mocker.patch("app.controllers.resident_controller.Session.commit", side_effect=SQLAlchemyError("Database error"))

    # Call the method
    response = controller.updateResidentBirthDate(idResident=1, new_birthDate="1995-03-10")

    # Verify the response
    assert response["status"] == "error"
    assert "Error de base de datos" in response["message"]


def test_update_resident_gender_success(setup_database):
    """
    Test: Verify that the method successfully updates a resident's gender.

    Steps:
        1. Add a resident to the database.
        2. Call the `updateResidentGender` method with a valid new gender.
        3. Verify the resident's gender is updated in the database.

    Expected Outcome:
        - The method returns a success message.
        - The resident's gender is updated in the database.
    """
    session = setup_database
    controller = ResidentController()

    # Add a resident
    resident = Resident(
        idResident=1, name="John", surname="Doe", birthDate=date(1990, 1, 1), gender="M", createdBy=1
    )
    session.add(resident)
    session.commit()

    # Call the method
    response = controller.updateResidentGender(
        idResident=1, new_gender="F", session=session
    )

    # Verify the response and the database
    assert response["status"] == "ok"
    assert response["message"] == "Género actualizado exitosamente"

    updated_resident = session.query(Resident).filter_by(idResident=1).first()
    assert updated_resident.gender == "F"


def test_update_resident_gender_not_found(setup_database):
    """
    Test: Verify that the method handles the case when a resident is not found.

    Steps:
        1. Ensure the database does not contain the specified resident.
        2. Call the `updateResidentGender` method with a non-existent resident ID.
        3. Verify the response indicates the resident is not found.

    Expected Outcome:
        - The method returns an error message indicating the resident is not found.
    """
    session = setup_database
    controller = ResidentController()

    # Call the method
    response = controller.updateResidentGender(
        idResident=999, new_gender="F", session=session
    )

    # Verify the response
    assert response["status"] == "error"
    assert response["message"] == "Residente no encontrado"


def test_update_resident_gender_invalid_gender(setup_database):
    """
    Test: Verify that the method handles invalid gender values gracefully.

    Steps:
        1. Add a resident to the database.
        2. Call the `updateResidentGender` method with an invalid gender value.
        3. Verify the response indicates the gender is invalid.

    Expected Outcome:
        - The method returns an error message indicating the gender is invalid.
    """
    session = setup_database
    controller = ResidentController()

    # Add a resident
    resident = Resident(
        idResident=1, name="John", surname="Doe", birthDate=date(1990, 1, 1), gender="M", createdBy=1
    )
    session.add(resident)
    session.commit()

    # Call the method with an invalid gender
    response = controller.updateResidentGender(
        idResident=1, new_gender="X", session=session  # Invalid gender
    )

    # Verify the response
    assert response["status"] == "error"
    assert response["message"] == "Género no válido. Los valores válidos son 'M', 'F' o 'Otro'."


def test_update_resident_gender_database_error(setup_database, mocker):
    """
    Test: Verify that the method handles database errors gracefully.

    Steps:
        1. Mock the database session to raise an SQLAlchemyError.
        2. Call the `updateResidentGender` method.
        3. Verify the response indicates a database error.

    Expected Outcome:
        - The method returns an error message indicating a database issue.
    """
    session = setup_database
    controller = ResidentController()

    # Mock the commit method to raise an exception
    mocker.patch("app.controllers.resident_controller.Session.commit", side_effect=SQLAlchemyError("Database error"))

    # Call the method
    response = controller.updateResidentGender(idResident=1, new_gender="F")

    # Verify the response
    assert response["status"] == "error"
    assert "Error de base de datos" in response["message"]

def test_list_residents_in_room_success(setup_database):
    """
    Test: Verify that the method successfully retrieves all residents in a specific room.

    Steps:
        1. Add a room and multiple residents to the database.
        2. Call the `list_residents_in_room` method for the specific room.
        3. Verify the response includes the correct residents.

    Expected Outcome:
        - The method returns a success status.
        - The response contains a list of residents assigned to the specified room.
    """
    session = setup_database
    controller = ResidentController()

    # Add a room and residents
    room = Room(idRoom=1, roomName="Room A", maxPeople=4, idShelter=1, createdBy=1)
    resident1 = Resident(
        idResident=1, name="John", surname="Doe", birthDate=date(1990, 1, 1), gender="M", createdBy=1, idFamily=1, idRoom=1
    )
    resident2 = Resident(
        idResident=2, name="Jane", surname="Doe", birthDate=date(1992, 6, 15), gender="F", createdBy=1, idFamily=1, idRoom=1
    )
    session.add_all([room, resident1, resident2])
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
        1. Add a room without residents to the database.
        2. Call the `list_residents_in_room` method for the specific room.
        3. Verify the response contains an empty list.

    Expected Outcome:
        - The method returns a success status.
        - The response contains an empty list.
    """
    session = setup_database
    controller = ResidentController()

    # Add a room without residents
    room = Room(idRoom=1, roomName="Room A", maxPeople=4, idShelter=1, createdBy=1)
    session.add(room)
    session.commit()

    # Call the method
    response = controller.list_residents_in_room(idRoom=1, session=session)

    # Verify the response
    assert response["status"] == "ok"
    assert len(response["residents"]) == 0


def test_list_residents_in_room_room_not_found(setup_database):
    """
    Test: Verify that the method handles the case where the specified room does not exist.

    Steps:
        1. Ensure the database does not contain the specified room.
        2. Call the `list_residents_in_room` method with a non-existent room ID.
        3. Verify the response contains an empty list.

    Expected Outcome:
        - The method returns a success status.
        - The response contains an empty list.
    """
    session = setup_database
    controller = ResidentController()

    # Call the method with a non-existent room ID
    response = controller.list_residents_in_room(idRoom=999, session=session)

    # Verify the response
    assert response["status"] == "ok"
    assert len(response["residents"]) == 0


def test_list_residents_in_room_database_error(setup_database, mocker):
    """
    Test: Verify that the method handles database errors gracefully.

    Steps:
        1. Mock the database session to raise an exception during the query.
        2. Call the `list_residents_in_room` method.
        3. Verify the response indicates a database error.

    Expected Outcome:
        - The method returns an error status.
        - The response contains an error message.
    """
    session = setup_database
    controller = ResidentController()

    # Mock the query to raise an exception
    mocker.patch(
        "app.controllers.resident_controller.Session.query",
        side_effect=Exception("Database error")
    )

    # Call the method
    response = controller.list_residents_in_room(idRoom=1, session=session)

    # Verify the response
    assert response["status"] == "error"
    assert "Database error" in response["message"]


def test_update_resident_room_success(setup_database):
    """
    Test: Verify that the method successfully updates the resident's room.

    Steps:
        1. Add a resident and two rooms to the database.
        2. Call the `updateResidentRoom` method to assign the resident to a new room.
        3. Verify the room ID is updated correctly.

    Expected Outcome:
        - The method returns a success status.
        - The resident's `idRoom` field is updated to the new room ID.
    """
    session = setup_database
    controller = ResidentController()

    # Add rooms and a resident
    room1 = Room(idRoom=1, roomName="Room A", maxPeople=4, idShelter=1, createdBy=1)
    room2 = Room(idRoom=2, roomName="Room B", maxPeople=4, idShelter=1, createdBy=1)
    resident = Resident(
        idResident=1, name="John", surname="Doe", birthDate=date(1990, 1, 1), gender="M", createdBy=1, idFamily=1, idRoom=1
    )
    session.add_all([room1, room2, resident])
    session.commit()

    # Call the method to update the resident's room
    response = controller.updateResidentRoom(resident_id=1, new_room_id=2, session=session)

    # Verify the response
    assert response["status"] == "ok"
    assert response["message"] == "Room updated successfully."

    # Verify the resident's room ID is updated
    updated_resident = session.query(Resident).filter(Resident.idResident == 1).first()
    assert updated_resident.idRoom == 2


def test_update_resident_room_resident_not_found(setup_database):
    """
    Test: Verify that the method handles the case where the resident does not exist.

    Steps:
        1. Ensure no resident with the specified ID exists in the database.
        2. Call the `updateResidentRoom` method with a non-existent resident ID.
        3. Verify the response indicates the resident is not found.

    Expected Outcome:
        - The method returns an error status.
        - The response contains an error message indicating the resident was not found.
    """
    session = setup_database
    controller = ResidentController()

    # Call the method with a non-existent resident ID
    response = controller.updateResidentRoom(resident_id=999, new_room_id=1, session=session)

    # Verify the response
    assert response["status"] == "error"
    assert "Residente con ID '999' no encontrado" in response["message"]


def test_update_resident_room_database_error(setup_database, mocker):
    """
    Test: Verify that the method handles database errors gracefully.

    Steps:
        1. Mock the database session to raise an SQLAlchemyError.
        2. Call the `updateResidentRoom` method.
        3. Verify the response indicates a database error.

    Expected Outcome:
        - The method returns an error status.
        - The response contains an error message indicating a database issue.
    """
    session = setup_database
    controller = ResidentController()

    # Add a resident
    resident = Resident(
        idResident=1, name="John", surname="Doe", birthDate=date(1990, 1, 1), gender="M", createdBy=1, idFamily=1, idRoom=1
    )
    session.add(resident)
    session.commit()

    # Mock the session commit to raise an exception
    mocker.patch("app.controllers.resident_controller.Session.commit", side_effect=SQLAlchemyError("Database error"))

    # Call the method
    response = controller.updateResidentRoom(resident_id=1, new_room_id=2, session=session)

    # Verify the response
    assert response["status"] == "error"
    assert "Error de base de datos" in response["message"]


def test_update_resident_room_room_not_found(setup_database):
    """
    Test: Verify that the method updates the resident's room even if the new room does not exist in the database.

    Steps:
        1. Add a resident and a single room to the database.
        2. Call the `updateResidentRoom` method with a non-existent room ID.
        3. Verify the resident's `idRoom` field is updated to the new room ID.

    Expected Outcome:
        - The method returns a success status.
        - The resident's `idRoom` field is updated to the specified new room ID, even if the room does not exist.
    """
    session = setup_database
    controller = ResidentController()

    # Add a room and a resident
    room1 = Room(idRoom=1, roomName="Room A", maxPeople=4, idShelter=1, createdBy=1)
    resident = Resident(
        idResident=1, name="John", surname="Doe", birthDate=date(1990, 1, 1), gender="M", createdBy=1, idFamily=1, idRoom=1
    )
    session.add_all([room1, resident])
    session.commit()

    # Call the method with a non-existent room ID
    response = controller.updateResidentRoom(resident_id=1, new_room_id=999, session=session)

    # Verify the response
    assert response["status"] == "ok"
    assert response["message"] == "Room updated successfully."

    # Verify the resident's room ID is updated
    updated_resident = session.query(Resident).filter(Resident.idResident == 1).first()
    assert updated_resident.idRoom == 999


def test_get_resident_room_success(setup_database):
    """
    Test: Verify that the method retrieves the room information for a resident with an assigned room.

    Steps:
        1. Add a resident and their assigned room to the database.
        2. Call the `getResidentRoomByNameAndSurname` method with the resident's name and surname.
        3. Verify the response contains the correct room information.

    Expected Outcome:
        - The method returns a success status.
        - The response contains the correct room details.
    """
    session = setup_database
    controller = ResidentController()

    # Add a room and a resident
    room = Room(idRoom=1, roomName="Room A", maxPeople=4, idShelter=1, createdBy=1)
    resident = Resident(
        name="John", surname="Doe", birthDate=date(1990, 1, 1), gender="M", createdBy=1, idFamily=1, idRoom=1
    )
    session.add_all([room, resident])
    session.commit()

    # Call the method
    response = controller.getResidentRoomByNameAndSurname(name="John", surname="Doe", session=session)

    # Verify the response
    assert response["status"] == "ok"
    assert response["room"]["roomName"] == "Room A"
    assert response["room"]["maxPeople"] == 4
    assert response["room"]["idShelter"] == 1


def test_get_resident_room_resident_not_found(setup_database):
    """
    Test: Verify that the method handles the case where the resident does not exist.

    Steps:
        1. Ensure no resident with the specified name and surname exists in the database.
        2. Call the `getResidentRoomByNameAndSurname` method with non-existent name and surname.
        3. Verify the response indicates the resident is not found.

    Expected Outcome:
        - The method returns an error status.
        - The response contains an error message indicating the resident was not found.
    """
    session = setup_database
    controller = ResidentController()

    # Call the method with a non-existent resident
    response = controller.getResidentRoomByNameAndSurname(name="NonExistent", surname="Person", session=session)

    # Verify the response
    assert response["status"] == "error"
    assert response["message"] == "Residente no encontrado"


def test_get_resident_room_no_room_assigned(setup_database):
    """
    Test: Verify that the method handles the case where the resident has no assigned room.

    Steps:
        1. Add a resident without an assigned room to the database.
        2. Call the `getResidentRoomByNameAndSurname` method with the resident's name and surname.
        3. Verify the response indicates the resident has no assigned room.

    Expected Outcome:
        - The method returns an error status.
        - The response contains an error message indicating the resident has no assigned room.
    """
    session = setup_database
    controller = ResidentController()

    # Add a resident without a room
    resident = Resident(
        name="John", surname="Doe", birthDate=date(1990, 1, 1), gender="M", createdBy=1, idFamily=1, idRoom=None
    )
    session.add(resident)
    session.commit()

    # Call the method
    response = controller.getResidentRoomByNameAndSurname(name="John", surname="Doe", session=session)

    # Verify the response
    assert response["status"] == "error"
    assert response["message"] == "Residente no tiene habitación asignada"


def test_get_resident_room_room_not_found(setup_database):
    """
    Test: Verify that the method handles the case where the resident's assigned room does not exist.

    Steps:
        1. Add a resident with an assigned room ID but without the corresponding room in the database.
        2. Call the `getResidentRoomByNameAndSurname` method with the resident's name and surname.
        3. Verify the response indicates the room was not found.

    Expected Outcome:
        - The method returns an error status.
        - The response contains an error message indicating the room was not found.
    """
    session = setup_database
    controller = ResidentController()

    # Add a resident with an assigned room ID, but the room does not exist
    resident = Resident(
        name="John", surname="Doe", birthDate=date(1990, 1, 1), gender="M", createdBy=1, idFamily=1, idRoom=999
    )
    session.add(resident)
    session.commit()

    # Call the method
    response = controller.getResidentRoomByNameAndSurname(name="John", surname="Doe", session=session)

    # Verify the response
    assert response["status"] == "error"
    assert response["message"] == "Habitación no encontrada"


def test_update_resident_surname_success(setup_database):
    """
    Test: Verify that the method successfully updates a resident's surname.

    Steps:
        1. Add a resident to the database.
        2. Call the `updateResidentSurname` method with a new surname.
        3. Verify the resident's surname is updated.

    Expected Outcome:
        - The resident's surname is updated successfully in the database.
    """
    session = setup_database
    controller = ResidentController()

    # Add a resident
    resident = Resident(idResident=1, name="John", surname="Doe", birthDate=date(1990, 1, 1), gender="M", createdBy=1)
    session.add(resident)
    session.commit()

    # Call the method
    response = controller.updateResidentSurname(idResident=1, new_surname="Smith", session=session)

    # Verify the response and database update
    assert response["status"] == "ok"
    assert response["message"] == "Apellido actualizado exitosamente"

    updated_resident = session.query(Resident).filter_by(idResident=1).first()
    assert updated_resident.surname == "Smith"



def test_update_resident_surname_not_found(setup_database):
    """
    Test: Verify that the method returns an error when the resident is not found.

    Steps:
        1. Ensure the database does not contain the specified resident.
        2. Call the `updateResidentSurname` method with a non-existent ID.
        3. Verify the response indicates the resident is not found.

    Expected Outcome:
        - The method returns an error message stating "Residente no encontrado".
    """
    session = setup_database
    controller = ResidentController()

    # Call the method with a non-existent resident ID
    response = controller.updateResidentSurname(idResident=999, new_surname="Smith", session=session)

    # Verify the response
    assert response["status"] == "error"
    assert response["message"] == "Residente no encontrado"



def test_update_resident_surname_database_error(setup_database, mocker):
    """
    Test: Verify that the method handles database errors gracefully.

    Steps:
        1. Mock the database session to raise an SQLAlchemyError.
        2. Call the `updateResidentSurname` method.
        3. Verify the response indicates a database error.

    Expected Outcome:
        - The method returns an error message indicating a database issue.
    """
    session = setup_database
    controller = ResidentController()

    # Add a resident
    resident = Resident(idResident=1, name="John", surname="Doe", birthDate=date(1990, 1, 1), gender="M", createdBy=1)
    session.add(resident)
    session.commit()

    # Mock the session's commit method to raise an SQLAlchemyError
    mocker.patch("app.controllers.resident_controller.Session.commit", side_effect=SQLAlchemyError("Database error"))

    # Call the method
    response = controller.updateResidentSurname(idResident=1, new_surname="Smith", session=session)

    # Verify the response
    assert response["status"] == "error"
    assert "Error de base de datos" in response["message"]


def test_get_resident_by_id_success(setup_database):
    """
    Test: Verify that the method retrieves a resident successfully by their ID.

    Steps:
        1. Add a resident to the database.
        2. Call the `getResidentById` method with the resident's ID.
        3. Verify the resident's details are returned correctly.

    Expected Outcome:
        - The resident's details are returned as a dictionary.
    """
    session = setup_database
    controller = ResidentController()

    # Add a resident
    resident = Resident(
        idResident=1, 
        name="John", 
        surname="Doe", 
        birthDate=date(1990, 1, 1), 
        gender="M", 
        idFamily=1
    )
    session.add(resident)
    session.commit()

    # Call the method
    response = controller.getResidentById(idResident=1, session=session)

    # Verify the response
    assert response["status"] == "ok"
    assert response["resident"]["idResident"] == 1
    assert response["resident"]["name"] == "John"
    assert response["resident"]["surname"] == "Doe"
    assert response["resident"]["birthDate"] == date(1990, 1, 1)
    assert response["resident"]["gender"] == "M"
    assert response["resident"]["idFamily"] == 1


def test_get_resident_by_id_not_found(setup_database):
    """
    Test: Verify that the method returns an error when the resident is not found.

    Steps:
        1. Ensure the database does not contain the specified resident ID.
        2. Call the `getResidentById` method with a non-existent ID.
        3. Verify the response indicates the resident is not found.

    Expected Outcome:
        - The method returns an error message stating "Residente no encontrado".
    """
    session = setup_database
    controller = ResidentController()

    # Call the method with a non-existent resident ID
    response = controller.getResidentById(idResident=999, session=session)

    # Verify the response
    assert response["status"] == "error"
    assert response["message"] == "Residente no encontrado"



def test_get_resident_by_id_unexpected_error(setup_database, mocker):
    """
    Test: Verify that the method handles unexpected errors gracefully.

    Steps:
        1. Mock the database query to raise a generic exception.
        2. Call the `getResidentById` method.
        3. Verify the response indicates an error.

    Expected Outcome:
        - The method returns an error message indicating an unexpected error occurred.
    """
    session = setup_database
    controller = ResidentController()

    # Mock the query to raise an exception
    mocker.patch("app.controllers.resident_controller.Session.query", side_effect=Exception("Unexpected error"))

    # Call the method
    response = controller.getResidentById(idResident=1, session=session)

    # Verify the response
    assert response["status"] == "error"
    assert "Unexpected error" in response["message"]



def test_get_resident_by_id_empty_database(setup_database):
    """
    Test: Verify that the method behaves correctly when the database is empty.

    Steps:
        1. Ensure the database contains no residents.
        2. Call the `getResidentById` method with any ID.
        3. Verify the response indicates the resident is not found.

    Expected Outcome:
        - The method returns an error message stating "Residente no encontrado".
    """
    session = setup_database
    controller = ResidentController()

    # Call the method with any ID
    response = controller.getResidentById(idResident=1, session=session)

    # Verify the response
    assert response["status"] == "error"
    assert response["message"] == "Residente no encontrado"


def test_login_success(setup_database):
    """
    Test: Verify that the method successfully logs in a resident with valid credentials.

    Steps:
        1. Add a resident to the database.
        2. Call the `login` method with the resident's name and surname.
        3. Verify the response includes the resident's ID, name, and surname.

    Expected Outcome:
        - The login is successful, and the resident's details are returned.
    """
    session = setup_database
    controller = ResidentController()

    # Add a resident
    resident = Resident(
        idResident=1,
        name="John",
        surname="Doe",
        birthDate=date(1990, 1, 1),
        gender="M",
        idFamily=1
    )
    session.add(resident)
    session.commit()

    # Call the method
    response = controller.login(name="John", surname="Doe", session=session)

    # Verify the response
    assert response["status"] == "ok"
    assert response["user"]["idResident"] == 1
    assert response["user"]["name"] == "John"
    assert response["user"]["surname"] == "Doe"


def test_login_invalid_credentials(setup_database):
    """
    Test: Verify that the method returns an error when the credentials are invalid.

    Steps:
        1. Ensure the database does not contain the provided name and surname.
        2. Call the `login` method with invalid credentials.
        3. Verify the response indicates invalid credentials.

    Expected Outcome:
        - The method returns an error message stating "Invalid credentials".
    """
    session = setup_database
    controller = ResidentController()

    # Call the method with invalid credentials
    response = controller.login(name="Invalid", surname="User", session=session)

    # Verify the response
    assert response["status"] == "error"
    assert response["message"] == "Invalid credentials"


def test_login_unexpected_error(setup_database, mocker):
    """
    Test: Verify that the method handles unexpected errors gracefully.

    Steps:
        1. Mock the database query to raise a generic exception.
        2. Call the `login` method.
        3. Verify the response indicates an error.

    Expected Outcome:
        - The method returns an error message indicating an unexpected error occurred.
    """
    session = setup_database
    controller = ResidentController()

    # Mock the query to raise an exception
    mocker.patch("app.controllers.resident_controller.Session.query", side_effect=Exception("Unexpected error"))

    # Call the method
    response = controller.login(name="John", surname="Doe", session=session)

    # Verify the response
    assert response["status"] == "error"
    assert "Unexpected error" in response["message"]


def test_login_empty_database(setup_database):
    """
    Test: Verify that the method behaves correctly when the database is empty.

    Steps:
        1. Ensure the database contains no residents.
        2. Call the `login` method with any name and surname.
        3. Verify the response indicates invalid credentials.

    Expected Outcome:
        - The method returns an error message stating "Invalid credentials".
    """
    session = setup_database
    controller = ResidentController()

    # Call the method with any credentials
    response = controller.login(name="John", surname="Doe", session=session)

    # Verify the response
    assert response["status"] == "error"
    assert response["message"] == "Invalid credentials"


def test_delete_resident_success(setup_database):
    """
    Test: Verify that the method successfully deletes a resident.

    Steps:
        1. Add a resident to the database.
        2. Call the `delete_resident` method with the resident's ID.
        3. Verify the resident is removed from the database.

    Expected Outcome:
        - The method returns a success status.
        - The resident no longer exists in the database.
    """
    session = setup_database
    controller = ResidentController()

    # Add a resident
    resident = Resident(
        idResident=1,
        name="John",
        surname="Doe",
        birthDate=date(1990, 1, 1),
        gender="M",
        idFamily=1
    )
    session.add(resident)
    session.commit()

    # Call the method
    response = controller.delete_resident(idResident=1, session=session)

    # Verify the response
    assert response["status"] == "ok"

    # Verify the resident no longer exists
    deleted_resident = session.query(Resident).filter_by(idResident=1).first()
    assert deleted_resident is None


def test_delete_resident_not_found(setup_database):
    """
    Test: Verify that the method returns a "not found" status when the resident does not exist.

    Steps:
        1. Ensure the database does not contain a resident with the given ID.
        2. Call the `delete_resident` method with a non-existent ID.
        3. Verify the response indicates the resident was not found.

    Expected Outcome:
        - The method returns a "not found" status.
    """
    session = setup_database
    controller = ResidentController()

    # Call the method with a non-existent resident ID
    response = controller.delete_resident(idResident=999, session=session)

    # Verify the response
    assert response["status"] == "not found"


def test_delete_resident_unexpected_error(setup_database, mocker):
    """
    Test: Verify that the method handles unexpected errors gracefully.

    Steps:
        1. Mock the database delete operation to raise a generic exception.
        2. Call the `delete_resident` method.
        3. Verify the response indicates an error occurred.

    Expected Outcome:
        - The method raises an exception or returns an appropriate error message.
    """
    session = setup_database
    controller = ResidentController()

    # Add a resident
    resident = Resident(
        idResident=1,
        name="John",
        surname="Doe",
        birthDate=date(1990, 1, 1),
        gender="M",
        idFamily=1
    )
    session.add(resident)
    session.commit()

    # Mock the delete operation to raise an exception
    mocker.patch("app.controllers.resident_controller.Session.delete", side_effect=Exception("Unexpected error"))

    # Call the method
    with pytest.raises(Exception) as exc_info:
        controller.delete_resident(idResident=1, session=session)

    # Verify the exception message
    assert "Unexpected error" in str(exc_info.value)



def test_delete_resident_empty_database(setup_database):
    """
    Test: Verify that the method behaves correctly when the database is empty.

    Steps:
        1. Ensure the database contains no residents.
        2. Call the `delete_resident` method with any ID.
        3. Verify the response indicates the resident was not found.

    Expected Outcome:
        - The method returns a "not found" status.
    """
    session = setup_database
    controller = ResidentController()

    # Call the method with any ID
    response = controller.delete_resident(idResident=1, session=session)

    # Verify the response
    assert response["status"] == "not found"





