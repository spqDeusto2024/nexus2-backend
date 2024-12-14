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
