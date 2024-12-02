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


