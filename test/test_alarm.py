import pytest
from app.controllers.alarm_controller import AlarmController
from app.models.alarm import Alarm as AlarmModel
from app.mysql.alarm import Alarm
from app.mysql.room import Room
from app.mysql.resident import Resident
from app.mysql.admin import Admin
from datetime import datetime

def test_create_alarm_success(setup_database):
    """
    Test: Successfully create a new alarm.

    Steps:
        1. Add a room, admin, and resident to the database.
        2. Call the `create_alarm` method with valid data.
        3. Verify the response is successful.
        4. Confirm the alarm is added to the database with the correct details.

    Expected Outcome:
        - The alarm should be successfully created.
        - The alarm should exist in the database with the provided details.

    Arguments:
        setup_database (fixture): The database session used for test setup.
    """
    session = setup_database
    controller = AlarmController()

    # Add required room, admin, and resident
    room = Room(idRoom=1, roomName="Room A", maxPeople=4, createdBy=1, createDate=datetime.now(), idShelter=1)
    admin = Admin(idAdmin=1, email="admin@example.com", name="Admin", password="password123")
    resident = Resident(idResident=1, name="John", surname="Doe", birthDate=datetime(1990, 1, 1), gender="M", idFamily=1, idRoom=1, createdBy=1)
    session.add_all([room, admin, resident])
    session.commit()

    # Alarm data
    alarm_data = AlarmModel(
        idAlarm=1,
        start=datetime.now(),
        end=datetime.now(),
        idRoom=1,
        idResident=1,
        idAdmin=1,
        createDate=datetime.now()
    )

    response = controller.create_alarm(alarm_data, session=session)

    assert response == {"status": "ok"}

    added_alarm = session.query(Alarm).filter_by(idAlarm=1).first()
    assert added_alarm is not None
    assert added_alarm.idRoom == 1
    assert added_alarm.idResident == 1
    assert added_alarm.idAdmin == 1

def test_create_alarm_room_not_exist(setup_database):
    """
    Test: Prevent creating an alarm when the room does not exist.

    Steps:
        1. Call the `create_alarm` method with a nonexistent room ID.
        2. Verify the response indicates that the room does not exist.

    Expected Outcome:
        - The operation should fail with an error message about the room.
        - No alarm should be added to the database.

    Arguments:
        setup_database (fixture): The database session used for test setup.
    """
    session = setup_database
    controller = AlarmController()

    # Alarm data with nonexistent room
    alarm_data = AlarmModel(
        idAlarm=1,
        start=datetime.now(),
        end=datetime.now(),
        idRoom=999,  # Nonexistent room
        idResident=1,
        idAdmin=1,
        createDate=datetime.now()
    )

    response = controller.create_alarm(alarm_data, session=session)

    assert response == {"status": "error", "message": "The room does not exist."}

    alarm_count = session.query(Alarm).count()
    assert alarm_count == 0

def test_create_alarm_admin_not_exist(setup_database):
    """
    Test: Prevent creating an alarm when the admin does not exist.

    Steps:
        1. Add a room and resident to the database.
        2. Call the `create_alarm` method with a nonexistent admin ID.
        3. Verify the response indicates that the admin does not exist.

    Expected Outcome:
        - The operation should fail with an error message about the admin.
        - No alarm should be added to the database.

    Arguments:
        setup_database (fixture): The database session used for test setup.
    """
    session = setup_database
    controller = AlarmController()

    # Add required room and resident
    room = Room(idRoom=1, roomName="Room A", maxPeople=4, createdBy=1, createDate=datetime.now(), idShelter=1)
    resident = Resident(idResident=1, name="John", surname="Doe", birthDate=datetime(1990, 1, 1), gender="M", idFamily=1, idRoom=1, createdBy=1)
    session.add_all([room, resident])
    session.commit()

    # Alarm data with nonexistent admin
    alarm_data = AlarmModel(
        idAlarm=1,
        start=datetime.now(),
        end=datetime.now(),
        idRoom=1,
        idResident=1,
        idAdmin=999,  # Nonexistent admin
        createDate=datetime.now()
    )

    response = controller.create_alarm(alarm_data, session=session)

    assert response == {"status": "error", "message": "The admin does not exist."}

    alarm_count = session.query(Alarm).count()
    assert alarm_count == 0

def test_create_alarm_duplicate(setup_database):
    """
    Test: Prevent creating a duplicate alarm in the same room.

    Steps:
        1. Add a room, admin, resident, and an existing alarm to the database.
        2. Call the `create_alarm` method with the same alarm details.
        3. Verify the response indicates that the alarm already exists.

    Expected Outcome:
        - The operation should fail with an error message about the duplicate alarm.
        - No duplicate alarm should be added to the database.

    Arguments:
        setup_database (fixture): The database session used for test setup.
    """
    session = setup_database
    controller = AlarmController()

    # Add required room, admin, resident, and existing alarm
    room = Room(idRoom=1, roomName="Room A", maxPeople=4, createdBy=1, createDate=datetime.now(), idShelter=1)
    admin = Admin(idAdmin=1, email="admin@example.com", name="Admin", password="password123")
    resident = Resident(idResident=1, name="John", surname="Doe", birthDate=datetime(1990, 1, 1), gender="M", idFamily=1, idRoom=1, createdBy=1)
    alarm = Alarm(idAlarm=1, start=datetime.now(), end=datetime.now(), idRoom=1, idResident=1, idAdmin=1, createDate=datetime.now())
    session.add_all([room, admin, resident, alarm])
    session.commit()

    # Attempt to create duplicate alarm
    alarm_data = AlarmModel(
        idAlarm=1,  # Same alarm ID
        start=datetime.now(),
        end=datetime.now(),
        idRoom=1,
        idResident=1,
        idAdmin=1,
        createDate=datetime.now()
    )

    response = controller.create_alarm(alarm_data, session=session)

    assert response == {"status": "error", "message": "Cannot create alarm, the alarm already exists in this room."}

    alarm_count = session.query(Alarm).count()
    assert alarm_count == 1
