import pytest
from app.controllers.admin_controller import AdminController
from sqlalchemy.exc import SQLAlchemyError
from app.models.admin import Admin as AdminModel
from app.mysql.admin import Admin

def test_create_admin_success(setup_database):
    """
    Test: Successfully create a new admin.

    Steps:
        1. Create a new admin with valid details.
        2. Verify the response is successful.
        3. Confirm the admin is added to the database with the correct details.

    Expected Outcome:
        - The admin should be successfully created.
        - The admin should exist in the database with the provided details.

    Arguments:
        setup_database (fixture): The database session used for test setup.
    """
    session = setup_database
    controller = AdminController()

    admin_data = AdminModel(
        idAdmin=1,
        email="admin@example.com",
        name="Admin Name",
        password="securepassword"
    )

    response = controller.create_admin(admin_data, session=session)

    assert response == {"status": "ok", "message": "Admin created successfully."}

    added_admin = session.query(Admin).filter_by(email="admin@example.com").first()
    assert added_admin is not None
    assert added_admin.email == "admin@example.com"
    assert added_admin.name == "Admin Name"
    assert added_admin.password == "securepassword"

def test_create_admin_duplicate_email(setup_database):
    """
    Test: Prevent creating an admin with a duplicate email.

    Steps:
        1. Add an admin with a specific email to the database.
        2. Attempt to create another admin with the same email.
        3. Verify the response indicates an error.

    Expected Outcome:
        - The second attempt should fail with a duplicate email error.
        - The database should only contain one admin with the given email.

    Arguments:
        setup_database (fixture): The database session used for test setup.
    """
    session = setup_database
    controller = AdminController()

    # Add initial admin
    existing_admin = Admin(
        email="admin@example.com",
        name="Existing Admin",
        password="password123"
    )
    session.add(existing_admin)
    session.commit()

    # Attempt to create duplicate
    admin_data = AdminModel(
        idAdmin=2,
        email="admin@example.com",
        name="New Admin",
        password="newpassword456"
    )

    response = controller.create_admin(admin_data, session=session)

    assert response == {"status": "error", "message": "An admin with this email already exists."}

    admin_count = session.query(Admin).filter_by(email="admin@example.com").count()
    assert admin_count == 1

def test_create_admin_database_error(setup_database, mocker):
    """
    Test: Handle a database error during admin creation.

    Steps:
        1. Simulate a database error by mocking the session's commit method.
        2. Attempt to create a new admin.
        3. Verify the response indicates a database error.

    Expected Outcome:
        - The operation should return an error response with the exception message.
        - No admin should be added to the database.

    Arguments:
        setup_database (fixture): The database session used for test setup.
        mocker (pytest-mock): Mocking library for simulating errors.
    """
    session = setup_database
    controller = AdminController()

    admin_data = AdminModel(
        idAdmin=1,
        email="admin2@example.com",
        name="Error Admin",
        password="errorpassword"
    )

    # Mock the commit method to raise an exception
    mocker.patch.object(session, "commit", side_effect=Exception("Database error"))

    response = controller.create_admin(admin_data, session=session)

    assert response == {"status": "error", "message": "Database error"}

    added_admin = session.query(Admin).filter_by(email="admin2@example.com").first()
    assert added_admin is None


def test_update_admin_name_success(setup_database):
    """
    Test: Verify that the name of an admin can be updated successfully.

    Steps:
        1. Add an admin to the database.
        2. Call the `updateAdminName` method to update the admin's name.
        3. Verify the response and the updated name in the database.

    Expected Outcome:
        - The method returns a success message.
        - The admin's name is updated in the database.
    """
    session = setup_database
    controller = AdminController()

    # Add an admin
    admin = Admin(idAdmin=45, email="pedro@pedro.com", name="Pedro", password="pedro123")
    session.add(admin)
    session.commit()

    # Update the admin's name
    response = controller.updateAdminName(idAdmin=45, new_name="Jose", session=session)

    # Verify the response and database changes

    assert response == {"status": "ok", "message": "Nombre actualizado exitosamente"}
    updated_admin = session.query(Admin).filter_by(idAdmin=45).first()
    assert updated_admin.name == "Jose"
    


def test_update_admin_name_not_found(setup_database):
    """
    Test: Verify that the method returns an error if the admin is not found.

    Steps:
        1. Ensure no admin exists in the database.
        2. Call the `updateAdminName` method with a non-existent admin ID.
        3. Verify the response indicates the admin was not found.

    Expected Outcome:
        - The method returns an error message indicating the admin was not found.
    """
    session = setup_database
    controller = AdminController()

    # Call the method with a non-existent admin ID
    response = controller.updateAdminName(idAdmin=999, new_name="3€&hjpds", session=session)

    # Verify the response
    assert response == {"status": "error", "message": "Administrador no encontrado"}


def test_update_admin_name_database_error(setup_database, mocker):
    """
    Test: Verify that the method handles database errors gracefully.

    Steps:
        1. Mock the database session to raise an SQLAlchemyError.
        2. Call the `updateAdminName` method.
        3. Verify the response indicates a database error.

    Expected Outcome:
        - The method returns an error message indicating a database issue.
    """
    session = setup_database
    controller = AdminController()

    # Mock the commit method to raise an exception, simulating an error in the commit
    mocker.patch("app.controllers.admin_controller.Session.commit", side_effect=SQLAlchemyError("Database error"))

    # Call the method to try how it works when there is an error in the database
    response = controller.updateAdminName(idAdmin=444, new_name="nwww")

    # Verify the response
    assert response["status"] == "error"
    assert "Error de base de datos" in response["message"]


def test_update_admin_name_unexpected_error(setup_database, mocker):
    """
    Test: Verify that the method handles unexpected errors gracefully.

    Steps:
        1. Mock the session to raise a general Exception.
        2. Call the `updateAdminName` method.
        3. Verify the response indicates an unexpected error.

    Expected Outcome:
        - The method returns an error message indicating an unexpected issue.
    """
    session = setup_database
    controller = AdminController()

    # Mock the session to raise a general Exception
    mocker.patch("sqlalchemy.orm.Session.query", side_effect=Exception("Unexpected error"))

    # Call the method
    response = controller.updateAdminName(idAdmin=1, new_name="New Name", session=session)

    # Verify the response
    assert response["status"] == "error"
    assert "Unexpected error" in response["message"]