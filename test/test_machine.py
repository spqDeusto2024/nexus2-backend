import pytest
from app.controllers.machine_controller import MachineController
from app.models.machine import Machine as MachineModel
from app.mysql.machine import Machine
from app.mysql.room import Room
from app.mysql.admin import Admin
from datetime import datetime
from datetime import date


def test_create_machine_success(setup_database):
    """
    Test: Successfully create a new machine.

    Steps:
        1. Add a room and admin to the database.
        2. Call the `create_machine` method with valid data.
        3. Verify the response is successful.
        4. Confirm the machine is added to the database with the correct details.

    Expected Outcome:
        - The machine should be successfully created.
        - The machine should exist in the database with the provided details.

    Arguments:
        setup_database (fixture): The database session used for test setup.
    """
    session = setup_database
    controller = MachineController()

    # Add required room and admin
    room = Room(idRoom=1, roomName="Room A", maxPeople=4, createdBy=1, createDate=datetime.now(), idShelter=1)
    admin = Admin(idAdmin=1, email="admin@example.com", name="Admin", password="password123")
    session.add_all([room, admin])
    session.commit()

    # Machine data
    machine_data = MachineModel(
        idMachine=1,
        machineName="Machine A",
        idRoom=1,
        on=True,
        createdBy=1,
        createDate=datetime.now(),
        update=datetime.now()
    )

    response = controller.create_machine(machine_data, session=session)

    assert response == {"status": "ok"}

    added_machine = session.query(Machine).filter_by(machineName="Machine A").first()
    assert added_machine is not None
    assert added_machine.idRoom == 1
    assert added_machine.createdBy == 1
    assert added_machine.on is True  # Validate 'on' is set to True by default


def test_create_machine_room_not_exist(setup_database):
    """
    Test: Prevent creating a machine when the room does not exist.

    Steps:
        1. Call the `create_machine` method with a nonexistent room ID.
        2. Verify the response indicates that the room does not exist.

    Expected Outcome:
        - The operation should fail with an error message about the room.
        - No machine should be added to the database.

    Arguments:
        setup_database (fixture): The database session used for test setup.
    """
    session = setup_database
    controller = MachineController()

    # Machine data with nonexistent room
    machine_data = MachineModel(
        idMachine=1,
        machineName="Machine A",
        idRoom=999,  # Nonexistent room
        createdBy=1,
        on=True,
        createDate=datetime.now(),
        update=datetime.now()
    )

    response = controller.create_machine(machine_data, session=session)

    assert response == {"status": "error", "message": "The room does not exist."}

    machine_count = session.query(Machine).count()
    assert machine_count == 0


def test_create_machine_admin_not_exist(setup_database):
    """
    Test: Prevent creating a machine when the admin does not exist.

    Steps:
        1. Add a room to the database.
        2. Call the `create_machine` method with a nonexistent admin ID.
        3. Verify the response indicates that the admin does not exist.

    Expected Outcome:
        - The operation should fail with an error message about the admin.
        - No machine should be added to the database.

    Arguments:
        setup_database (fixture): The database session used for test setup.
    """
    session = setup_database
    controller = MachineController()

    # Add required room
    room = Room(idRoom=1, roomName="Room A", maxPeople=4, createdBy=1, createDate=datetime.now(), idShelter=1)
    session.add(room)
    session.commit()

    # Machine data with nonexistent admin
    machine_data = MachineModel(
        idMachine=1,
        machineName="Machine A",
        idRoom=1,
        on=True,
        createdBy=999,  # Nonexistent admin
        createDate=datetime.now(),
        update=datetime.now()
    )

    response = controller.create_machine(machine_data, session=session)

    assert response == {"status": "error", "message": "The admin does not exist."}

    machine_count = session.query(Machine).count()
    assert machine_count == 0


def test_create_machine_duplicate(setup_database):
    """
    Test: Prevent creating a duplicate machine in the same room.

    Steps:
        1. Add a room, admin, and an existing machine to the database.
        2. Call the `create_machine` method with the same machine name and room ID.
        3. Verify the response indicates that the machine already exists.

    Expected Outcome:
        - The operation should fail with an error message about the duplicate machine.
        - No duplicate machine should be added to the database.

    Arguments:
        setup_database (fixture): The database session used for test setup.
    """
    session = setup_database
    controller = MachineController()

    # Add required room, admin, and existing machine
    room = Room(idRoom=1, roomName="Room A", maxPeople=4, createdBy=1, createDate=datetime.now(), idShelter=1)
    admin = Admin(idAdmin=1, email="admin@example.com", name="Admin", password="password123")
    machine = Machine(idMachine=1, machineName="Machine A", on=True, idRoom=1, createdBy=1, createDate=datetime.now(), update=datetime.now())
    session.add_all([room, admin, machine])
    session.commit()

    # Attempt to create duplicate machine
    machine_data = MachineModel(
        idMachine=2,
        machineName="Machine A",  # Same machine name
        idRoom=1,                 # Same room
        on=True,
        createdBy=1,
        createDate=datetime.now(),
        update=datetime.now()
    )

    response = controller.create_machine(machine_data, session=session)

    assert response == {"status": "error", "message": "A machine with the same name already exists in this room."}

    machine_count = session.query(Machine).count()
    assert machine_count == 1








def test_delete_machine_not_found(setup_database):
    """
    Test: Attempt to delete a machine that does not exist.

    Expected Outcome:
        - Returns an error indicating the machine was not found.
    """
    session = setup_database
    controller = MachineController()

    # Call the method for a non-existent machine
    response = controller.deleteMachine(machine_id=999, session=session)

    # Assert the response
    assert response == {"status": "error", "message": "Machine not found"}

def test_delete_machine_success(setup_database):
    """
    Test: Successfully delete a machine from the database.

    Expected Outcome:
        - The machine is deleted successfully.
    """
    session = setup_database
    controller = MachineController()

    # Add a test machine
    machine = Machine(
        idMachine=1,
        machineName="Machine A",
        on=True,
        idRoom=1,
        createdBy=1,
        createDate=date(2024, 12, 1)  # Convertimos a un objeto datetime.date
    )
    session.add(machine)
    session.commit()

    # Call the method
    response = controller.deleteMachine(machine_id=1, session=session)

    # Assert the response
    assert response == {"status": "ok", "message": "Machine deleted successfully"}

    # Verify the machine is deleted
    deleted_machine = session.query(Machine).filter_by(idMachine=1).first()
    assert deleted_machine is None



def test_list_machines_empty(setup_database):
    """
    Test: No machines are present in the database.

    Expected Outcome:
        - Returns an empty list.
    """
    session = setup_database
    controller = MachineController()

    # Call the method with no machines in the database
    response = controller.list_machines(session=session)

    # Assert the response
    assert response["status"] == "ok"
    assert response["machines"] == []

def test_list_machines_error(setup_database, mocker):
    """
    Test: Simulate an unexpected error during machine retrieval.

    Expected Outcome:
        - Returns an error message indicating the issue.
    """
    session = setup_database
    controller = MachineController()

    # Mock session.query to raise an exception
    mocker.patch("sqlalchemy.orm.Session.query", side_effect=Exception("Unexpected error"))

    # Call the method
    response = controller.list_machines(session=session)

    # Assert the response
    assert response["status"] == "error"
    assert "Unexpected error" in response["message"]