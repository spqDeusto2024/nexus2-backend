import pytest
from app.controllers.machine_controller import MachineController
from app.models.machine import Machine as MachineModel
from app.mysql.machine import Machine
from app.mysql.room import Room
from app.mysql.admin import Admin
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
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

def test_update_machine_status_success(setup_database):
    """
    Test: Successfully update the status of a machine to 'on'.

    Steps:
        1. Add a machine to the database with 'on' set to False.
        2. Call the `updateMachineStatusOn` method with the machine name.
        3. Verify the response is successful.
        4. Confirm the machine's 'on' status is updated to True.

    Expected Outcome:
        - The machine's 'on' status is updated to True.

    Arguments:
        setup_database (fixture): The database session used for test setup.
    """

    session = setup_database
    controller = MachineController()

    # Add a machine to the database
    machine = Machine(idMachine=1, machineName="Test Machine", idRoom=1, on=False, createdBy=1)
    session.add(machine)
    session.commit()

    # Update the machine's status
    response = controller.updateMachineStatusOn("Test Machine", session=session)

    assert response == {"status": "ok", "message": "Estado de la máquina 'Test Machine' actualizado a True"}

    updated_machine = session.query(Machine).filter_by(machineName="Test Machine").first()
    assert updated_machine is not None
    assert updated_machine.on is True

def test_update_machine_status_not_found(setup_database):
    """
    Test: Attempt to update the status of a non-existent machine.

    Steps:
        1. Ensure the database is empty or does not contain the target machine.
        2. Call the `updateMachineStatusOn` method with a non-existent machine name.
        3. Verify the response indicates an error.

    Expected Outcome:
        - The response should indicate the machine was not found.

    Arguments:
        setup_database (fixture): The database session used for test setup.
    """

    session = setup_database
    controller = MachineController()

    # Attempt to update a non-existent machine
    response = controller.updateMachineStatusOn("Nonexistent Machine", session=session)

    assert response == {"status": "error", "message": "Máquina 'Nonexistent Machine' no encontrada"}

def test_update_machine_status_db_error(mocker, setup_database):
    """
    Test: Handle database error during the update process.

    Steps:
        1. Add a machine to the database.
        2. Mock the database query to raise an SQLAlchemyError.
        3. Call the `updateMachineStatusOn` method.
        4. Verify the response indicates a database error.

    Expected Outcome:
        - The response should indicate a database error occurred.

    Arguments:
        mocker (pytest fixture): Used for mocking objects and methods.
        setup_database (fixture): The database session used for test setup.
    """

    session = setup_database
    controller = MachineController()

    # Add a machine to the database
    machine = Machine(idMachine=1, machineName="Test Machine", idRoom=1, on=False, createdBy=1)
    session.add(machine)
    session.commit()

    # Mock the query to raise an SQLAlchemyError
    mocker.patch("sqlalchemy.orm.query.Query.first", side_effect=SQLAlchemyError("Database error"))

    response = controller.updateMachineStatusOn("Test Machine", session=session)

    assert response == {"status": "error", "message": "Error de base de datos: Database error"}

def test_update_machine_status_general_exception(mocker, setup_database):
    """
    Test: Handle a general exception during the update process.

    Steps:
        1. Add a machine to the database.
        2. Mock the database query to raise a general exception.
        3. Call the `updateMachineStatusOn` method.
        4. Verify the response indicates a general error.

    Expected Outcome:
        - The response should indicate a general error occurred.

    Arguments:
        mocker (pytest fixture): Used for mocking objects and methods.
        setup_database (fixture): The database session used for test setup.
    """

    session = setup_database
    controller = MachineController()

    # Add a machine to the database
    machine = Machine(idMachine=1, machineName="Test Machine", idRoom=1, on=False, createdBy=1)
    session.add(machine)
    session.commit()

    # Mock the query to raise a general exception
    mocker.patch("sqlalchemy.orm.query.Query.first", side_effect=Exception("General error"))

    response = controller.updateMachineStatusOn("Test Machine", session=session)

    assert response == {"status": "error", "message": "General error"}


def test_update_machine_status_success_on(setup_database):
    """
    Test: Successfully update the status of a machine to 'on'.

    Steps:
        1. Add a machine to the database with 'on' set to False.
        2. Call the `updateMachineStatusOn` method with the machine name.
        3. Verify the response is successful.
        4. Confirm the machine's 'on' status is updated to True.

    Expected Outcome:
        - The machine's 'on' status is updated to True.

    Arguments:
        setup_database (fixture): The database session used for test setup.
    """

    session = setup_database
    controller = MachineController()

    # Add a machine to the database
    machine = Machine(idMachine=1, machineName="Test Machine", idRoom=1, on=False, createdBy=1)
    session.add(machine)
    session.commit()

    # Update the machine's status
    response = controller.updateMachineStatusOn("Test Machine", session=session)

    assert response == {"status": "ok", "message": "Estado de la máquina 'Test Machine' actualizado a True"}

    updated_machine = session.query(Machine).filter_by(machineName="Test Machine").first()
    assert updated_machine is not None
    assert updated_machine.on is True

def test_update_machine_status_not_found_on(setup_database):
    """
    Test: Attempt to update the status of a non-existent machine.

    Steps:
        1. Ensure the database is empty or does not contain the target machine.
        2. Call the `updateMachineStatusOn` method with a non-existent machine name.
        3. Verify the response indicates an error.

    Expected Outcome:
        - The response should indicate the machine was not found.

    Arguments:
        setup_database (fixture): The database session used for test setup.
    """

    session = setup_database
    controller = MachineController()

    # Attempt to update a non-existent machine
    response = controller.updateMachineStatusOn("Nonexistent Machine", session=session)

    assert response == {"status": "error", "message": "Máquina 'Nonexistent Machine' no encontrada"}

def test_update_machine_status_db_error_on(mocker, setup_database):
    """
    Test: Handle database error during the update process.

    Steps:
        1. Add a machine to the database.
        2. Mock the database query to raise an SQLAlchemyError.
        3. Call the `updateMachineStatusOn` method.
        4. Verify the response indicates a database error.

    Expected Outcome:
        - The response should indicate a database error occurred.

    Arguments:
        mocker (pytest fixture): Used for mocking objects and methods.
        setup_database (fixture): The database session used for test setup.
    """

    from sqlalchemy.exc import SQLAlchemyError

    session = setup_database
    controller = MachineController()

    # Add a machine to the database
    machine = Machine(idMachine=1, machineName="Test Machine", idRoom=1, on=False, createdBy=1)
    session.add(machine)
    session.commit()

    # Mock the query to raise an SQLAlchemyError
    mocker.patch("sqlalchemy.orm.query.Query.first", side_effect=SQLAlchemyError("Database error"))

    response = controller.updateMachineStatusOn("Test Machine", session=session)

    assert response == {"status": "error", "message": "Error de base de datos: Database error"}

def test_update_machine_status_general_exception_on(mocker, setup_database):
    """
    Test: Handle a general exception during the update process.

    Steps:
        1. Add a machine to the database.
        2. Mock the database query to raise a general exception.
        3. Call the `updateMachineStatusOn` method.
        4. Verify the response indicates a general error.

    Expected Outcome:
        - The response should indicate a general error occurred.

    Arguments:
        mocker (pytest fixture): Used for mocking objects and methods.
        setup_database (fixture): The database session used for test setup.
    """

    session = setup_database
    controller = MachineController()

    # Add a machine to the database
    machine = Machine(idMachine=1, machineName="Test Machine", idRoom=1, on=False, createdBy=1)
    session.add(machine)
    session.commit()

    # Mock the query to raise a general exception
    mocker.patch("sqlalchemy.orm.query.Query.first", side_effect=Exception("General error"))

    response = controller.updateMachineStatusOn("Test Machine", session=session)

    assert response == {"status": "error", "message": "General error"}

def test_update_machine_date_success(setup_database):
    """
    Test: Successfully update the `update` field of a machine to the current date.

    Steps:
        1. Add a machine to the database with an initial `update` field value.
        2. Call the `updateMachineDate` method with the machine name.
        3. Verify the response is successful.
        4. Confirm the machine's `update` field is updated to the current date.

    Expected Outcome:
        - The machine's `update` field is updated to today's date.

    Arguments:
        setup_database (fixture): The database session used for test setup.
    """

    from datetime import date

    session = setup_database
    controller = MachineController()

    # Add a machine to the database
    machine = Machine(idMachine=1, machineName="Test Machine", idRoom=1, on=True, createdBy=1, update=date(2020, 1, 1))
    session.add(machine)
    session.commit()

    # Update the machine's date
    response = controller.updateMachineDate("Test Machine", session=session)

    assert response == {"status": "ok", "message": "Fecha de la máquina 'Test Machine' actualizada exitosamente"}

    updated_machine = session.query(Machine).filter_by(machineName="Test Machine").first()
    assert updated_machine is not None
    assert updated_machine.update == date.today()

def test_update_machine_date_not_found(setup_database):
    """
    Test: Attempt to update the `update` field of a non-existent machine.

    Steps:
        1. Ensure the database is empty or does not contain the target machine.
        2. Call the `updateMachineDate` method with a non-existent machine name.
        3. Verify the response indicates an error.

    Expected Outcome:
        - The response should indicate the machine was not found.

    Arguments:
        setup_database (fixture): The database session used for test setup.
    """

    session = setup_database
    controller = MachineController()

    # Attempt to update a non-existent machine
    response = controller.updateMachineDate("Nonexistent Machine", session=session)

    assert response == {"status": "error", "message": "Máquina 'Nonexistent Machine' no encontrada"}

def test_update_machine_date_db_error(mocker, setup_database):
    """
    Test: Handle database error during the update process.

    Steps:
        1. Add a machine to the database.
        2. Mock the database query to raise an SQLAlchemyError.
        3. Call the `updateMachineDate` method.
        4. Verify the response indicates a database error.

    Expected Outcome:
        - The response should indicate a database error occurred.

    Arguments:
        mocker (pytest fixture): Used for mocking objects and methods.
        setup_database (fixture): The database session used for test setup.
    """

    from sqlalchemy.exc import SQLAlchemyError

    session = setup_database
    controller = MachineController()

    # Add a machine to the database
    machine = Machine(idMachine=1, machineName="Test Machine", idRoom=1, on=True, createdBy=1, update=date(2020, 1, 1))
    session.add(machine)
    session.commit()

    # Mock the query to raise an SQLAlchemyError
    mocker.patch("sqlalchemy.orm.query.Query.first", side_effect=SQLAlchemyError("Database error"))

    response = controller.updateMachineDate("Test Machine", session=session)

    assert response == {"status": "error", "message": "Error de base de datos: Database error"}

def test_update_machine_date_general_exception(mocker, setup_database):
    """
    Test: Handle a general exception during the update process.

    Steps:
        1. Add a machine to the database.
        2. Mock the database query to raise a general exception.
        3. Call the `updateMachineDate` method.
        4. Verify the response indicates a general error.

    Expected Outcome:
        - The response should indicate a general error occurred.

    Arguments:
        mocker (pytest fixture): Used for mocking objects and methods.
        setup_database (fixture): The database session used for test setup.
    """

    session = setup_database
    controller = MachineController()

    # Add a machine to the database
    machine = Machine(idMachine=1, machineName="Test Machine", idRoom=1, on=True, createdBy=1, update=date(2020, 1, 1))
    session.add(machine)
    session.commit()

    # Mock the query to raise a general exception
    mocker.patch("sqlalchemy.orm.query.Query.first", side_effect=Exception("General error"))

    response = controller.updateMachineDate("Test Machine", session=session)

    assert response == {"status": "error", "message": "General error"}

def test_list_all_machines_success(setup_database):
    """
    Test: Successfully retrieve all machines from the database.

    Steps:
        1. Add multiple machines to the database.
        2. Call the `list_machines` method.
        3. Verify the response contains all machines with correct details.

    Expected Outcome:
        - The response should include all machines in the database with accurate details.

    Arguments:
        setup_database (fixture): The database session used for test setup.
    """

    session = setup_database
    controller = MachineController()

    # Add machines to the database
    machine1 = Machine(idMachine=1, machineName="Machine A", on=True, idRoom=1, createdBy=1, createDate=datetime(2023, 1, 1), update=datetime(2023, 1, 2))
    machine2 = Machine(idMachine=2, machineName="Machine B", on=False, idRoom=2, createdBy=2, createDate=datetime(2023, 2, 1), update=None)
    session.add_all([machine1, machine2])
    session.commit()

    # List machines
    response = controller.list_machines(session=session)

    assert response["status"] == "ok"
    assert len(response["machines"]) == 2

    machine_a = next(m for m in response["machines"] if m["machineName"] == "Machine A")
    assert machine_a["on"] is True
    assert machine_a["idRoom"] == 1
    assert machine_a["createDate"] == "2023-01-01"
    assert machine_a["update"] == "2023-01-02"

    machine_b = next(m for m in response["machines"] if m["machineName"] == "Machine B")
    assert machine_b["on"] is False
    assert machine_b["idRoom"] == 2
    assert machine_b["createDate"] == "2023-02-01"
    assert machine_b["update"] is None

def test_list_no_machines(setup_database):
    """
    Test: Retrieve an empty list when no machines exist in the database.

    Steps:
        1. Ensure the database is empty.
        2. Call the `list_machines` method.
        3. Verify the response indicates no machines are available.

    Expected Outcome:
        - The response should indicate no machines were found.

    Arguments:
        setup_database (fixture): The database session used for test setup.
    """

    session = setup_database
    controller = MachineController()

    # List machines in an empty database
    response = controller.list_machines(session=session)

    assert response == {"status": "ok", "machines": []}

def test_list_machines_db_error(mocker, setup_database):
    """
    Test: Handle database error during the machine listing process.

    Steps:
        1. Mock the database query to raise an SQLAlchemyError.
        2. Call the `list_machines` method.
        3. Verify the response indicates a database error.

    Expected Outcome:
        - The response should indicate a database error occurred.

    Arguments:
        mocker (pytest fixture): Used for mocking objects and methods.
        setup_database (fixture): The database session used for test setup.
    """

    from sqlalchemy.exc import SQLAlchemyError

    session = setup_database
    controller = MachineController()

    # Mock the query to raise an SQLAlchemyError
    mocker.patch("sqlalchemy.orm.query.Query.all", side_effect=SQLAlchemyError("Database error"))

    response = controller.list_machines(session=session)

    assert response == {"status": "error", "message": "Database error"}

def test_list_machines_general_exception(mocker, setup_database):
    """
    Test: Handle a general exception during the machine listing process.

    Steps:
        1. Mock the database query to raise a general exception.
        2. Call the `list_machines` method.
        3. Verify the response indicates a general error.

    Expected Outcome:
        - The response should indicate a general error occurred.

    Arguments:
        mocker (pytest fixture): Used for mocking objects and methods.
        setup_database (fixture): The database session used for test setup.
    """

    session = setup_database
    controller = MachineController()

    # Mock the query to raise a general exception
    mocker.patch("sqlalchemy.orm.query.Query.all", side_effect=Exception("General error"))

    response = controller.list_machines(session=session)

    assert response == {"status": "error", "message": "General error"}

def test_delete_machine_success(setup_database):
    """
    Test: Successfully delete a machine from the database.

    Steps:
        1. Add a machine to the database.
        2. Call the `deleteMachine` method with the machine ID.
        3. Verify the machine is deleted from the database.

    Expected Outcome:
        - The response should indicate successful deletion.

    Arguments:
        setup_database (fixture): The database session used for test setup.
    """

    session = setup_database
    controller = MachineController()

    # Add a machine to the database
    machine = Machine(idMachine=1, machineName="Machine A", on=True, idRoom=1, createdBy=1)
    session.add(machine)
    session.commit()

    # Delete the machine
    response = controller.deleteMachine(machine_id=1, session=session)

    assert response == {"status": "ok", "message": "Machine deleted successfully"}

    # Verify the machine is removed
    deleted_machine = session.query(Machine).filter(Machine.idMachine == 1).first()
    assert deleted_machine is None

def test_delete_machine_not_found(setup_database):
    """
    Test: Attempt to delete a non-existent machine from the database.

    Steps:
        1. Ensure no machine exists with the specified ID.
        2. Call the `deleteMachine` method with a non-existent machine ID.
        3. Verify the response indicates the machine was not found.

    Expected Outcome:
        - The response should indicate the machine was not found.

    Arguments:
        setup_database (fixture): The database session used for test setup.
    """

    session = setup_database
    controller = MachineController()

    # Attempt to delete a non-existent machine
    response = controller.deleteMachine(machine_id=999, session=session)

    assert response == {"status": "error", "message": "Machine not found"}

def test_delete_machine_db_error(mocker, setup_database):
    """
    Test: Handle database error during the machine deletion process.

    Steps:
        1. Add a machine to the database.
        2. Mock the database delete operation to raise an SQLAlchemyError.
        3. Call the `deleteMachine` method.
        4. Verify the response indicates a database error.

    Expected Outcome:
        - The response should indicate a database error occurred.

    Arguments:
        mocker (pytest fixture): Used for mocking objects and methods.
        setup_database (fixture): The database session used for test setup.
    """

    from sqlalchemy.exc import SQLAlchemyError

    session = setup_database
    controller = MachineController()

    # Add a machine to the database
    machine = Machine(idMachine=1, machineName="Machine A", on=True, idRoom=1, createdBy=1)
    session.add(machine)
    session.commit()

    # Mock the delete operation to raise an SQLAlchemyError
    mocker.patch("sqlalchemy.orm.session.Session.delete", side_effect=SQLAlchemyError("Database error"))

    response = controller.deleteMachine(machine_id=1, session=session)

    assert response == {"status": "error", "message": "Database error"}

def test_delete_machine_general_exception(mocker, setup_database):
    """
    Test: Handle a general exception during the machine deletion process.

    Steps:
        1. Add a machine to the database.
        2. Mock the database delete operation to raise a general exception.
        3. Call the `deleteMachine` method.
        4. Verify the response indicates a general error.

    Expected Outcome:
        - The response should indicate a general error occurred.

    Arguments:
        mocker (pytest fixture): Used for mocking objects and methods.
        setup_database (fixture): The database session used for test setup.
    """
    
    session = setup_database
    controller = MachineController()

    # Add a machine to the database
    machine = Machine(idMachine=1, machineName="Machine A", on=True, idRoom=1, createdBy=1)
    session.add(machine)
    session.commit()

    # Mock the delete operation to raise a general exception
    mocker.patch("sqlalchemy.orm.session.Session.delete", side_effect=Exception("General error"))

    response = controller.deleteMachine(machine_id=1, session=session)

    assert response == {"status": "error", "message": "General error"}
