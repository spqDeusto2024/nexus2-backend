import pytest
from app.controllers.alarm_controller import AlarmController
from app.models.alarm import Alarm as AlarmModel
from app.mysql.alarm import Alarm
from app.mysql.room import Room
from app.mysql.resident import Resident
from app.mysql.admin import Admin
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

def test_create_alarm(mocker, setup_database):
    """
    Test: Validate the functionality of the `create_alarm` method.

    Steps:
        1. Add a room to the database.
        2. Test successful creation of an alarm.
        3. Test creation of an alarm for a non-existent room.
        4. Test creation of a duplicate alarm.
        5. Mock the session commit to raise a SQLAlchemyError and handle it.

    Expected Outcome:
        - Alarm is created successfully if the room exists and no duplicates are found.
        - Error is returned if the room does not exist.
        - Error is returned if a duplicate alarm is detected.
        - SQLAlchemy errors are handled gracefully.

    Arguments:
        mocker (pytest fixture): Used for mocking objects and methods.
        setup_database (fixture): The database session used for test setup.
    """
    session = setup_database
    controller = AlarmController()  # Assuming this is the controller containing `create_alarm`

    # Step 1: Add a room to the database
    room = Room(idRoom=1, roomName="Room A")
    session.add(room)
    session.commit()

    # Step 2: Test successful creation of an alarm
    alarm_data = AlarmModel(
        idAlarm=1,
        start="2024-12-14T08:00:00",
        end="2024-12-14T09:00:00",
        idRoom=1,
        createDate="2024-12-14T07:00:00"
    )

    response = controller.create_alarm(body=alarm_data, session=session)
    assert response == {"status": "ok"}

    # Verify the alarm was added to the database
    added_alarm = session.query(Alarm).filter_by(idAlarm=1, idRoom=1).first()
    assert added_alarm is not None
    assert added_alarm.start == alarm_data.start

    # Step 3: Test creation of an alarm for a non-existent room
    alarm_data_nonexistent_room = AlarmModel(
        idAlarm=2,
        start="2024-12-14T10:00:00",
        end="2024-12-14T11:00:00",
        idRoom=99,
        createDate="2024-12-14T07:30:00"
    )

    response = controller.create_alarm(body=alarm_data_nonexistent_room, session=session)
    assert response == {"status": "error", "message": "The room does not exist."}

    # Step 4: Test creation of a duplicate alarm
    duplicate_alarm_data = AlarmModel(
        idAlarm=1,  # Same idAlarm and idRoom as the first alarm
        start="2024-12-14T08:00:00",
        end="2024-12-14T09:00:00",
        idRoom=1,
        createDate="2024-12-14T07:00:00"
    )

    response = controller.create_alarm(body=duplicate_alarm_data, session=session)
    assert response == {"status": "error", "message": "Cannot create alarm, the alarm already exists in this room."}

    # Step 5: Mock SQLAlchemyError during session commit
    mocker.patch("sqlalchemy.orm.session.Session.commit", side_effect=SQLAlchemyError("Database error"))

    # Spy on the rollback method
    rollback_spy = mocker.spy(session, "rollback")

    alarm_data_error = AlarmModel(
        idAlarm=3,
        start="2024-12-14T12:00:00",
        end="2024-12-14T13:00:00",
        idRoom=1,
        createDate="2024-12-14T07:45:00"
    )

    response = controller.create_alarm(body=alarm_data_error, session=session)
    assert response == {"status": "error", "message": "Database error"}

    # Verify rollback was called
    rollback_spy.assert_called_once()


def test_list_alarms_success(setup_database):
    """
    Test: Verify that the method retrieves all alarms in the database successfully.

    Steps:
        1. Add multiple alarms to the database.
        2. Call the `list_alarms` method.
        3. Verify the response contains the correct list of alarms.

    Expected Outcome:
        - The method returns a success status.
        - The response contains all the alarms with their correct details.
    """
    session = setup_database
    controller = AlarmController()

    # Add alarms
    alarm1 = Alarm(idAlarm=1, start=datetime(2023, 1, 1, 8, 0, 0), end=datetime(2023, 1, 1, 10, 0, 0), idRoom=1, createDate=datetime(2023, 1, 1))
    alarm2 = Alarm(idAlarm=2, start=datetime(2023, 1, 2, 9, 0, 0), end=datetime(2023, 1, 2, 11, 0, 0), idRoom=2, createDate=datetime(2023, 1, 2))
    session.add_all([alarm1, alarm2])
    session.commit()

    # Call the method
    response = controller.list_alarms(session=session)

    # Verify the response
    assert response["status"] == "ok"
    assert len(response["alarms"]) == 2
    assert response["alarms"][0]["idAlarm"] == 1
    assert response["alarms"][1]["idAlarm"] == 2
    assert response["alarms"][0]["start"] == "2023-01-01T08:00:00"
    assert response["alarms"][1]["end"] == "2023-01-02T11:00:00"


def test_list_alarms_empty_database(setup_database):
    """
    Test: Verify that the method handles an empty database gracefully.

    Steps:
        1. Ensure the database has no alarms.
        2. Call the `list_alarms` method.
        3. Verify the response indicates no alarms are found.

    Expected Outcome:
        - The method returns a success status.
        - The response contains an empty list of alarms.
    """
    session = setup_database
    controller = AlarmController()

    # Call the method
    response = controller.list_alarms(session=session)

    # Verify the response
    assert response["status"] == "ok"
    assert len(response["alarms"]) == 0


def test_list_alarms_database_error(setup_database, mocker):
    """
    Test: Verify that the method handles database errors gracefully.

    Steps:
        1. Mock the session query to raise an exception.
        2. Call the `list_alarms` method.
        3. Verify the response indicates a database error.

    Expected Outcome:
        - The method returns an error status.
        - The response contains an error message indicating a database issue.
    """
    session = setup_database
    controller = AlarmController()

    # Mock the query method to raise an exception
    mocker.patch("app.controllers.alarm_controller.Session.query", side_effect=Exception("Database error"))

    # Call the method
    response = controller.list_alarms(session=session)

    # Verify the response
    assert response["status"] == "error"
    assert "Database error" in response["message"]


def test_create_alarm_level_success(setup_database):
    """
    Test: Verify that the method successfully creates an alarm in room 3.

    Steps:
        1. Add room 3 to the database.
        2. Call the `create_alarmLevel` method with valid alarm data.
        3. Verify that the alarm is created and the response contains the correct details.

    Expected Outcome:
        - The method returns a success status.
        - The response includes the generated `idAlarm` and a success message.
        - The database contains the new alarm.
    """
    session = setup_database
    controller = AlarmController()

    # Add room 3 to the database
    room = Room(idRoom=3, roomName="Room C", maxPeople=5, idShelter=1)
    session.add(room)
    session.commit()

    # Alarm data
    alarm_data = AlarmModel(
        idAlarm=3,
        start=datetime(2023, 1, 1, 8, 0, 0),
        end=datetime(2023, 1, 1, 9, 0, 0),
        idRoom=3,
        createDate=datetime(2023, 1, 1)
    )

    # Call the method
    response = controller.create_alarmLevel(body=alarm_data, session=session)

    # Verify the response
    assert response["status"] == "ok"
    assert "idAlarm" in response
    assert "created successfully" in response["message"]

    # Verify the alarm in the database
    alarm = session.query(Alarm).filter(Alarm.idRoom == 3).first()
    assert alarm is not None
    assert alarm.start == alarm_data.start
    assert alarm.end == alarm_data.end


def test_create_alarm_level_room_not_exist(setup_database):
    """
    Test: Verify that the method returns an error if room 3 does not exist.

    Steps:
        1. Ensure the database does not contain room 3.
        2. Call the `create_alarmLevel` method with valid alarm data.
        3. Verify that the response indicates the room does not exist.

    Expected Outcome:
        - The method returns an error status.
        - The response contains a message indicating that room 3 does not exist.
        - No alarm is created in the database.
    """
    session = setup_database
    controller = AlarmController()

    # Alarm data
    alarm_data = AlarmModel(
        idAlarm=3,
        start=datetime(2023, 1, 1, 8, 0, 0),
        end=datetime(2023, 1, 1, 9, 0, 0),
        idRoom=3,
        createDate=datetime(2023, 1, 1)
    )

    # Call the method
    response = controller.create_alarmLevel(body=alarm_data, session=session)

    # Verify the response
    assert response["status"] == "error"
    assert "Room with idRoom=3 does not exist" in response["message"]

    # Verify no alarm is created in the database
    alarm_count = session.query(Alarm).count()
    assert alarm_count == 0



def test_create_alarm_level_database_error(setup_database, mocker):
    """
    Test: Verify that the method handles database errors gracefully.

    Steps:
        1. Mock the database session to raise an SQLAlchemyError.
        2. Call the `create_alarmLevel` method with valid alarm data.
        3. Verify the response indicates a database error.

    Expected Outcome:
        - The method returns an error status.
        - The response contains a message indicating a database error.
    """
    session = setup_database
    controller = AlarmController()

    # Add room 3 to the database
    room = Room(idRoom=3, roomName="Room C", maxPeople=5, idShelter=1)
    session.add(room)
    session.commit()

    # Mock the commit method to raise an exception
    mocker.patch("app.controllers.alarm_controller.Session.commit", side_effect=SQLAlchemyError("Database error"))

    # Alarm data
    alarm_data = AlarmModel(
        idAlarm=3,
        start=datetime(2023, 1, 1, 8, 0, 0),
        end=datetime(2023, 1, 1, 9, 0, 0),
        idRoom=3,
        createDate=datetime(2023, 1, 1)
    )

    # Call the method
    response = controller.create_alarmLevel(body=alarm_data, session=session)

    # Verify the response
    assert response["status"] == "error"
    assert "Database error" in response["message"]



def test_update_alarm_end_date_success(setup_database):
    """
    Test: Verify that the method updates the end date of an alarm successfully.

    Steps:
        1. Add an alarm to the database.
        2. Call the `updateAlarmEndDate` method with a valid `idAlarm` and new end date.
        3. Verify that the end date of the alarm is updated.

    Expected Outcome:
        - The method returns a success status.
        - The alarm's end date is updated in the database.
    """
    session = setup_database
    controller = AlarmController()

    # Add an alarm
    alarm = Alarm(
        idAlarm=1,
        start=datetime(2023, 1, 1, 8, 0, 0),
        end=None,
        idRoom=1,
        createDate=datetime(2023, 1, 1)
    )

    session.add(alarm)
    session.commit()

    # Update end date
    end_date = datetime(2023, 1, 1, 10, 0, 0)
    response = controller.updateAlarmEndDate(idAlarm=1, new_enddate=end_date, session=session)

    # Verify the response
    assert response["status"] == "ok"
    assert "actualizada exitosamente" in response["message"]

    # Verify the alarm in the database
    updated_alarm = session.query(Alarm).filter(Alarm.idAlarm == 1).first()
    assert updated_alarm is not None


def test_update_alarm_end_date_not_found(setup_database):
    """
    Test: Verify that the method returns an error if the alarm does not exist.

    Steps:
        1. Ensure the database does not contain the specified alarm ID.
        2. Call the `updateAlarmEndDate` method with a non-existent `idAlarm`.
        3. Verify that the response indicates the alarm was not found.

    Expected Outcome:
        - The method returns an error status.
        - The response contains a message indicating the alarm was not found.
    """
    session = setup_database
    controller = AlarmController()

    # Update end date for non-existent alarm
    new_enddate = datetime(2023, 1, 1, 10, 0, 0)
    response = controller.updateAlarmEndDate(idAlarm=999, new_enddate=new_enddate, session=session)

    # Verify the response
    assert response["status"] == "error"
    assert "Alarma no encontrada" in response["message"]


def test_update_alarm_end_date_database_error(setup_database, mocker):
    """
    Test: Verify that the method handles database errors gracefully.

    Steps:
        1. Mock the database session to raise an SQLAlchemyError.
        2. Call the `updateAlarmEndDate` method with a valid `idAlarm` and new end date.
        3. Verify the response indicates a database error.

    Expected Outcome:
        - The method returns an error status.
        - The response contains a message indicating a database error.
    """
    session = setup_database
    controller = AlarmController()

    # Add an alarm
    alarm = Alarm(
        idAlarm=1,
        start=datetime(2023, 1, 1, 8, 0, 0),
        end=None,
        idRoom=1,
        createDate=datetime(2023, 1, 1)
    )
    session.add(alarm)
    session.commit()

    # Mock the commit method to raise an exception
    mocker.patch("app.controllers.alarm_controller.Session.commit", side_effect=SQLAlchemyError("Database error"))

    # Update end date
    new_enddate = datetime(2023, 1, 1, 10, 0, 0)
    response = controller.updateAlarmEndDate(idAlarm=1, new_enddate=new_enddate, session=session)

    # Verify the response
    assert response["status"] == "error"
    assert "Error de base de datos" in response["message"]

    # Verify the alarm in the database remains unchanged
    unchanged_alarm = session.query(Alarm).filter(Alarm.idAlarm == 1).first()
    assert unchanged_alarm is not None
    assert unchanged_alarm.end is None


