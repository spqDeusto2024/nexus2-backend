import pytest
from app.controllers.alarm_controller import AlarmController
from app.models.alarm import Alarm as AlarmModel
from app.mysql.alarm import Alarm
from app.mysql.room import Room
from app.mysql.resident import Resident
from app.mysql.admin import Admin
from datetime import datetime

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

def test_create_alarm_success(setup_database):
    """
    Test: Successfully create a new alarm.

    Expected Outcome:
        - The alarm is created and added to the database with correct details.
    """
    session = setup_database
    controller = AlarmController()

    # Add a room
    room = Room(idRoom=1, roomName="Room A", maxPeople=4, idShelter=1)
    session.add(room)
    session.commit()

    # Alarm data
    alarm_data = AlarmModel(
        idAlarm=1,
        start=datetime(2024, 12, 10, 10, 0, 0),
        end=datetime(2024, 12, 10, 12, 0, 0),
        idRoom=1,
        createDate=datetime.now()
    )

    response = controller.create_alarm(alarm_data, session=session)

    assert response == {"status": "ok"}

    # Verify alarm in database
    added_alarm = session.query(Alarm).filter_by(idAlarm=1).first()
    assert added_alarm is not None
    assert added_alarm.idRoom == 1
    assert added_alarm.start == datetime(2024, 12, 10, 10, 0, 0)
    assert added_alarm.end == datetime(2024, 12, 10, 12, 0, 0)


def test_create_alarm_duplicate(setup_database):
    """
    Test: Prevent creating a duplicate alarm in the same room.

    Steps:
        1. Add a room and an alarm to the database.
        2. Attempt to add another alarm with the same ID in the same room.
        3. Verify the response indicates duplication.

    Expected Outcome:
        - The operation should fail with an error message about the duplicate alarm.
    """
    session = setup_database
    controller = AlarmController()

    # Add a room and an alarm
    room = Room(idRoom=1, roomName="Room A", maxPeople=5, idShelter=1)
    alarm = Alarm(
        idAlarm=1,
        start=datetime(2024, 12, 10, 10, 0, 0),
        end=datetime(2024, 12, 10, 12, 0, 0),
        idRoom=1,
        createDate=datetime.now()
    )
    session.add_all([room, alarm])
    session.commit()

    # Duplicate alarm data
    alarm_data = AlarmModel(
        idAlarm=1,  # Same ID
        start=datetime(2024, 12, 11, 10, 0, 0),
        end=datetime(2024, 12, 11, 12, 0, 0),
        idRoom=1,
        createDate=datetime.now()
    )

    response = controller.create_alarm(alarm_data, session=session)

    assert response == {"status": "error", "message": "Cannot create alarm, the alarm already exists in this room."}

    alarm_count = session.query(Alarm).count()
    assert alarm_count == 1

#NOOOOOOOOO SUMAAAA
def test_create_alarm_room_not_exist(setup_database):
    """
    Test: Prevent creating an alarm for a non-existent room.

    Expected Outcome:
        - Returns an error indicating the room does not exist.
    """
    session = setup_database
    controller = AlarmController()

    # Alarm data for non-existent room
    alarm_data = AlarmModel(
        idAlarm=1,
        start=datetime(2024, 12, 10, 10, 0, 0),
        end=datetime(2024, 12, 10, 12, 0, 0),
        idRoom=999,  # Non-existent room
        createDate=datetime.now()
    )

    response = controller.create_alarm(alarm_data, session=session)

    assert response == {"status": "error", "message": "The room does not exist."}

    # Verify no alarm in database
    alarm_count = session.query(Alarm).count()
    assert alarm_count == 0

#NOOOO SUMAAAAA
def test_create_alarm_room_not_exist(setup_database):
    """
    Test: Prevent creating an alarm for a non-existent room.

    Expected Outcome:
        - Returns an error indicating the room does not exist.
    """
    session = setup_database
    controller = AlarmController()

    # Alarm data for non-existent room
    alarm_data = AlarmModel(
        idAlarm=1,
        start=datetime(2024, 12, 10, 10, 0, 0),
        end=datetime(2024, 12, 10, 12, 0, 0),
        idRoom=999,  # Non-existent room
        createDate=datetime.now()
    )

    response = controller.create_alarm(alarm_data, session=session)

    assert response == {"status": "error", "message": "The room does not exist."}

    # Verify no alarm in database
    alarm_count = session.query(Alarm).count()
    assert alarm_count == 0

#NOOOO SUMAAAA
def test_create_alarm_duplicate(setup_database):
    """
    Test: Prevent creating a duplicate alarm in the same room.

    Expected Outcome:
        - Returns an error indicating the alarm already exists in the room.
    """
    session = setup_database
    controller = AlarmController()

    # Add a room and an existing alarm
    room = Room(idRoom=1, roomName="Room A", maxPeople=4, idShelter=1)
    alarm = Alarm(
        idAlarm=1,
        start=datetime(2024, 12, 10, 10, 0, 0),
        end=datetime(2024, 12, 10, 12, 0, 0),
        idRoom=1,
        createDate=datetime.now()
    )
    session.add_all([room, alarm])
    session.commit()

    # Duplicate alarm data
    alarm_data = AlarmModel(
        idAlarm=1,  # Duplicate ID
        start=datetime(2024, 12, 11, 10, 0, 0),
        end=datetime(2024, 12, 11, 12, 0, 0),
        idRoom=1,
        createDate=datetime.now()
    )

    response = controller.create_alarm(alarm_data, session=session)

    assert response == {"status": "error", "message": "Cannot create alarm, the alarm already exists in this room."}

    # Verify only one alarm in database
    alarm_count = session.query(Alarm).count()
    assert alarm_count == 1


def test_create_alarmLevel_success(setup_database):
    """
    Test: Successfully create a new alarm in room 3.

    Expected Outcome:
        - The alarm is created and added to the database with the correct details.
    """
    session = setup_database
    controller = AlarmController()

    # Add room with idRoom=3
    room = Room(idRoom=3, roomName="Room 3", maxPeople=5, idShelter=1)
    session.add(room)
    session.commit()

    # Alarm data (including idRoom)
    alarm_data = AlarmModel(
        idRoom=3,  # Add idRoom to match the Pydantic model validation
        start=datetime(2024, 12, 10, 10, 0, 0),
        end=None,  # End time can be None initially
        createDate=datetime.now()
    )

    response = controller.create_alarmLevel(alarm_data, session=session)

    assert response["status"] == "ok"
    assert "created successfully in room 3" in response["message"]
    assert "idAlarm" in response

    # Verify alarm in database
    added_alarm = session.query(Alarm).filter_by(idRoom=3).first()
    assert added_alarm is not None
    assert added_alarm.start == datetime(2024, 12, 10, 10, 0, 0)
    assert added_alarm.end is None


def test_create_alarmLevel_room_not_exist(setup_database):
    """
    Test: Prevent creating an alarm when room 3 does not exist.

    Expected Outcome:
        - Returns an error indicating that room 3 does not exist.
    """
    session = setup_database
    controller = AlarmController()

    # Alarm data
    alarm_data = AlarmModel(
        idRoom=3,  # Agrega idRoom explícitamente para cumplir con la validación
        start=datetime(2024, 12, 10, 10, 0, 0),
        end=datetime(2024, 12, 10, 12, 0, 0),
        createDate=datetime.now()
    )

    response = controller.create_alarmLevel(alarm_data, session=session)

    assert response == {"status": "error", "message": "Room with idRoom=3 does not exist."}

    # Verify no alarm in database
    alarm_count = session.query(Alarm).count()
    assert alarm_count == 0

def test_update_alarm_enddate_alarm_not_found(setup_database):
    """
    Test: Attempt to update the end date of a non-existent alarm.

    Expected Outcome:
        - Returns an error indicating that the alarm is not found.
    """
    session = setup_database
    controller = AlarmController()

    # New end date
    new_enddate = datetime(2024, 12, 10, 12, 0, 0)

    # Call the method with a non-existent alarm ID
    response = controller.updateAlarmEndDate(idAlarm=999, new_enddate=new_enddate, session=session)

    # Assert the response
    assert response == {"status": "error", "message": "Alarma no encontrada"}

    # Verify no alarms exist in the database
    alarm_count = session.query(Alarm).count()
    assert alarm_count == 0

def test_update_alarm_enddate_unexpected_error(setup_database, mocker):
    """
    Test: Simulate an unexpected error during the update of an alarm's end date.

    Expected Outcome:
        - Returns an error indicating an unexpected issue.
    """
    session = setup_database
    controller = AlarmController()

    # Add a test alarm
    alarm = Alarm(
        idAlarm=1,
        start=datetime(2024, 12, 10, 10, 0, 0),
        end=None,
        idRoom=3,
        createDate=datetime(2024, 12, 10, 9, 0, 0)
    )
    session.add(alarm)
    session.commit()

    # Mock session.commit to raise a generic exception
    mocker.patch.object(session, "commit", side_effect=Exception("Unexpected error"))

    # New end date
    new_enddate = datetime(2024, 12, 10, 12, 0, 0)

    # Call the method
    response = controller.updateAlarmEndDate(idAlarm=1, new_enddate=new_enddate, session=session)

    # Assert the response
    assert response["status"] == "error"
    assert "Unexpected error" in response["message"]

    # Verify the alarm's end date is not updated in the database
    updated_alarm = session.query(Alarm).filter_by(idAlarm=1).first()
    assert updated_alarm is not None
    assert updated_alarm.end is None    


def test_list_alarms_success(setup_database):
    """
    Test: Successfully retrieve a list of alarms from the database.

    Expected Outcome:
        - Returns the list of alarms with their details.
    """
    session = setup_database
    controller = AlarmController()

    # Add test alarms
    alarm1 = Alarm(
        idAlarm=1,
        start=datetime(2024, 12, 1, 8, 0, 0),
        end=datetime(2024, 12, 1, 10, 0, 0),
        idRoom=1,
        createDate=datetime(2024, 12, 1, 7, 30, 0)
    )
    alarm2 = Alarm(
        idAlarm=2,
        start=datetime(2024, 12, 2, 9, 0, 0),
        end=None,  # No end time
        idRoom=2,
        createDate=datetime(2024, 12, 2, 8, 45, 0)
    )
    session.add_all([alarm1, alarm2])
    session.commit()

    # Call the method
    response = controller.list_alarms(session=session)

    # Assert the response
    assert response["status"] == "ok"
    assert len(response["alarms"]) == 2

    expected_response = [
        {
            "idAlarm": 1,
            "start": "2024-12-01T08:00:00",
            "end": "2024-12-01T10:00:00",
            "idRoom": 1,
            "createDate": "2024-12-01T07:30:00"
        },
        {
            "idAlarm": 2,
            "start": "2024-12-02T09:00:00",
            "end": None,
            "idRoom": 2,
            "createDate": "2024-12-02T08:45:00"
        }
    ]

    assert response["alarms"] == expected_response

def test_list_alarms_empty(setup_database):
    """
    Test: Successfully retrieve an empty list of alarms.

    Expected Outcome:
        - Returns an empty list of alarms.
    """
    session = setup_database
    controller = AlarmController()

    # Call the method (no alarms in the database)
    response = controller.list_alarms(session=session)

    # Assert the response
    assert response["status"] == "ok"
    assert response["alarms"] == []

def test_list_alarms_error(setup_database, mocker):
    """
    Test: Simulate an unexpected error during the retrieval of alarms.

    Expected Outcome:
        - Returns an error message indicating the failure.
    """
    session = setup_database
    controller = AlarmController()

    # Mock session.query to raise an exception
    mocker.patch("sqlalchemy.orm.Session.query", side_effect=Exception("Unexpected error"))

    # Call the method
    response = controller.list_alarms(session=session)

    # Assert the response
    assert response["status"] == "error"
    assert response["message"] == "Unexpected error"

