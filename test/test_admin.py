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


def test_login_admin_success(setup_database):
    """
    Test: Verify that the method successfully logs in an admin with correct credentials.

    Steps:
        1. Add an admin to the database with known email and password.
        2. Call the `loginAdmin` method with valid credentials.
        3. Verify the response contains a JWT token and user information.

    Expected Outcome:
        - The method returns a status of "ok".
        - A valid JWT token is included in the response.
        - User information (ID and email) is correct.
    """

    session = setup_database
    controller = AdminController()

    # Add an admin
    admin = Admin(idAdmin=1, email="admin@example.com", name="HelloBoy", password="password123")
    session.add(admin)
    session.commit()

    # Call the method
    response = controller.loginAdmin(email="admin@example.com", password="password123", session=session)

    # Verify the response
    assert response["status"] == "ok"
    assert "token" in response
    assert response["user"]["idAdmin"] == 1
    assert response["user"]["email"] == "admin@example.com"


def test_login_admin_invalid_email(setup_database):
    """
    Test: Verify that the method handles incorrect email credentials.

    Steps:
        1. Add an admin to the database with a known email and password.
        2. Call the `loginAdmin` method with an incorrect email.
        3. Verify the response indicates invalid credentials.

    Expected Outcome:
        - The method returns a status of "error".
        - The response contains the message "Invalid credentials".
    """

    session = setup_database
    controller = AdminController()

    # Add an admin
    admin = Admin(idAdmin=1, email="admin@example.com", name="HelloBoy", password="password123")
    session.add(admin)
    session.commit()

    # Call the method with an incorrect email
    response = controller.loginAdmin(email="wrong@example.com", password="password123", session=session)

    # Verify the response
    assert response["status"] == "error"
    assert response["message"] == "Invalid credentials"



def test_login_admin_invalid_password(setup_database):
    """
    Test: Verify that the method handles incorrect password credentials.

    Steps:
        1. Add an admin to the database with a known email and password.
        2. Call the `loginAdmin` method with an incorrect password.
        3. Verify the response indicates invalid credentials.

    Expected Outcome:
        - The method returns a status of "error".
        - The response contains the message "Invalid credentials".
    """

    session = setup_database
    controller = AdminController()

    # Add an admin
    admin = Admin(idAdmin=1, email="admin@example.com", name="HelloBoy", password="password123")
    session.add(admin)
    session.commit()

    # Call the method with an incorrect password
    response = controller.loginAdmin(email="admin@example.com", password="wrongpassword", session=session)

    # Verify the response
    assert response["status"] == "error"
    assert response["message"] == "Invalid credentials"



def test_login_admin_nonexistent_user(setup_database):
    """
    Test: Verify that the method handles a login attempt for a non-existent admin.

    Steps:
        1. Ensure the database does not contain any admins.
        2. Call the `loginAdmin` method with any credentials.
        3. Verify the response indicates invalid credentials.

    Expected Outcome:
        - The method returns a status of "error".
        - The response contains the message "Invalid credentials".
    """

    session = setup_database
    controller = AdminController()

    # Call the method with non-existent admin credentials
    response = controller.loginAdmin(email="nonexistent@example.com", password="password123", session=session)

    # Verify the response
    assert response["status"] == "error"
    assert response["message"] == "Invalid credentials"



def test_login_admin_unexpected_error(setup_database, mocker):
    """
    Test: Verify that the method handles unexpected errors gracefully.

    Steps:
        1. Mock the database query to raise an exception.
        2. Call the `loginAdmin` method.
        3. Verify the response indicates an error occurred.

    Expected Outcome:
        - The method returns a status of "error".
        - The response contains the exception message.
    """

    session = setup_database
    controller = AdminController()

    # Mock the query to raise an exception
    mocker.patch("app.controllers.admin_controller.Session.query", side_effect=Exception("Unexpected error"))

    # Call the method
    response = controller.loginAdmin(email="admin@example.com", password="password123", session=session)

    # Verify the response
    assert response["status"] == "error"
    assert "Unexpected error" in response["message"]


def test_get_admin_by_id_success(setup_database):
    """
    Test: Verify that the method retrieves an admin successfully by their ID.

    Steps:
        1. Add an admin to the database with a known ID.
        2. Call the `getAdminById` method with the admin's ID.
        3. Verify the response contains the correct admin details.

    Expected Outcome:
        - The method returns a status of "ok".
        - The admin details in the response match the database record.
    """

    session = setup_database
    controller = AdminController()

    # Add an admin
    admin = Admin(idAdmin=1, email="admin@example.com", name="Admin Name", password="hashedpassword")
    session.add(admin)
    session.commit()

    # Call the method
    response = controller.getAdminById(idAdmin=1, session=session)

    # Verify the response
    assert response["status"] == "ok"
    assert response["admin"]["idAdmin"] == 1
    assert response["admin"]["email"] == "admin@example.com"
    assert response["admin"]["name"] == "Admin Name"
    assert response["admin"]["password"] == "hashedpassword"


def test_get_admin_by_id_not_found(setup_database):
    """
    Test: Verify that the method returns an error when the admin ID is not found.

    Steps:
        1. Ensure the database does not contain an admin with the specified ID.
        2. Call the `getAdminById` method with a non-existent ID.
        3. Verify the response indicates that the admin was not found.

    Expected Outcome:
        - The method returns a status of "error".
        - The response contains the message "Administrador no encontrado".
    """

    session = setup_database
    controller = AdminController()

    # Call the method with a non-existent admin ID
    response = controller.getAdminById(idAdmin=999, session=session)

    # Verify the response
    assert response["status"] == "error"
    assert response["message"] == "Administrador no encontrado"


def test_get_admin_by_id_unexpected_error(setup_database, mocker):
    """
    Test: Verify that the method handles unexpected errors gracefully.

    Steps:
        1. Mock the database query to raise an exception.
        2. Call the `getAdminById` method.
        3. Verify the response indicates an error occurred.

    Expected Outcome:
        - The method returns a status of "error".
        - The response contains the exception message.
    """

    session = setup_database
    controller = AdminController()

    # Mock the query to raise an exception
    mocker.patch("app.controllers.admin_controller.Session.query", side_effect=Exception("Unexpected error"))

    # Call the method
    response = controller.getAdminById(idAdmin=1, session=session)

    # Verify the response
    assert response["status"] == "error"
    assert "Unexpected error" in response["message"]



def test_delete_admin_success(setup_database):
    """
    Test: Verify that an admin is successfully deleted by their ID.

    Steps:
        1. Add an admin to the database with a known ID.
        2. Call the `deleteAdmin` method with the admin's ID.
        3. Verify the admin is removed from the database.

    Expected Outcome:
        - The method returns a status of "ok".
        - The admin record is no longer present in the database.
    """

    session = setup_database
    controller = AdminController()

    # Add an admin to the database
    admin = Admin(idAdmin=1, email="admin@example.com", name="Admin Name", password="hashedpassword")
    session.add(admin)
    session.commit()

    # Call the method
    response = controller.deleteAdmin(admin_id=1, session=session)

    # Verify the response
    assert response["status"] == "ok"
    assert response["message"] == "Admin deleted successfully"

    # Verify the admin is deleted from the database
    deleted_admin = session.query(Admin).filter(Admin.idAdmin == 1).first()
    assert deleted_admin is None



def test_delete_admin_not_found(setup_database):
    """
    Test: Verify that the method handles the case when the admin ID is not found.

    Steps:
        1. Ensure the database does not contain an admin with the specified ID.
        2. Call the `deleteAdmin` method with a non-existent ID.
        3. Verify the response indicates that the admin was not found.

    Expected Outcome:
        - The method returns a status of "error".
        - The response contains the message "Admin not found".
    """

    session = setup_database
    controller = AdminController()

    # Call the method with a non-existent admin ID
    response = controller.deleteAdmin(admin_id=999, session=session)

    # Verify the response
    assert response["status"] == "error"
    assert response["message"] == "Admin not found"



def test_delete_admin_unexpected_error(setup_database, mocker):
    """
    Test: Verify that the method handles unexpected errors gracefully.

    Steps:
        1. Mock the database session's `delete` method to raise an exception.
        2. Call the `deleteAdmin` method.
        3. Verify the response indicates an error occurred.

    Expected Outcome:
        - The method returns a status of "error".
        - The response contains the exception message.
    """

    session = setup_database
    controller = AdminController()

    # Add an admin to the database
    admin = Admin(idAdmin=1, email="admin@example.com", name="Admin Name", password="hashedpassword")
    session.add(admin)
    session.commit()

    # Mock the `delete` method to raise an exception
    mocker.patch("app.controllers.admin_controller.Session.delete", side_effect=Exception("Unexpected error"))

    # Call the method
    response = controller.deleteAdmin(admin_id=1, session=session)

    # Verify the response
    assert response["status"] == "error"
    assert "Unexpected error" in response["message"]

    # Verify the admin is still in the database
    existing_admin = session.query(Admin).filter(Admin.idAdmin == 1).first()
    assert existing_admin is not None


def test_list_admins_success(setup_database):
    """
    Test: Verify that the method retrieves all admins successfully.

    Steps:
        1. Add multiple admins to the database.
        2. Call the `listAdmins` method.
        3. Verify the response contains all the admins.

    Expected Outcome:
        - The method returns a status of "ok".
        - The response contains a list of all admins with their IDs and emails.
    """

    session = setup_database
    controller = AdminController()

    # Add admins to the database
    admin1 = Admin(idAdmin=1, email="admin1@example.com", name="Admin One", password="hashedpassword1")
    admin2 = Admin(idAdmin=2, email="admin2@example.com", name="Admin Two", password="hashedpassword2")
    session.add_all([admin1, admin2])
    session.commit()

    # Call the method
    response = controller.listAdmins(session=session)

    # Verify the response
    assert response["status"] == "ok"
    assert len(response["admins"]) == 2
    assert response["admins"][0]["email"] == "admin1@example.com"
    assert response["admins"][1]["email"] == "admin2@example.com"


def test_list_admins_empty(setup_database):
    """
    Test: Verify that the method handles an empty database gracefully.

    Steps:
        1. Ensure no admins are present in the database.
        2. Call the `listAdmins` method.
        3. Verify the response contains an empty list.

    Expected Outcome:
        - The method returns a status of "ok".
        - The response contains an empty list of admins.
    """

    session = setup_database
    controller = AdminController()

    # Call the method
    response = controller.listAdmins(session=session)

    # Verify the response
    assert response["status"] == "ok"
    assert response["admins"] == []



def test_list_admins_unexpected_error(setup_database, mocker):
    """
    Test: Verify that the method handles unexpected errors gracefully.

    Steps:
        1. Mock the database session's `query` method to raise an exception.
        2. Call the `listAdmins` method.
        3. Verify the response indicates an error occurred.

    Expected Outcome:
        - The method returns a status of "error".
        - The response contains the exception message.
    """

    session = setup_database
    controller = AdminController()

    # Mock the `query` method to raise an exception
    mocker.patch("app.controllers.admin_controller.Session.query", side_effect=Exception("Unexpected error"))

    # Call the method
    response = controller.listAdmins(session=session)

    # Verify the response
    assert response["status"] == "error"
    assert "Unexpected error" in response["message"]


def test_update_admin_password_success(setup_database):
    """
    Test: Verify that the method successfully updates the password of an admin.

    Steps:
        1. Add an admin to the database.
        2. Call the `updateAdminPassword` method with a new password.
        3. Verify the response indicates success.
        4. Confirm that the password is updated in the database.

    Expected Outcome:
        - The method returns a status of "ok".
        - The admin's password is updated in the database.
    """

    session = setup_database
    controller = AdminController()

    # Add an admin to the database
    admin = Admin(idAdmin=1, email="admin@example.com", name="Admin", password="oldpassword")
    session.add(admin)
    session.commit()

    # Call the method to update the password
    response = controller.updateAdminPassword(idAdmin=1, new_password="newpassword", session=session)

    # Verify the response
    assert response["status"] == "ok"
    assert response["message"] == "Contraseña actualizada exitosamente"

    # Verify the password in the database
    updated_admin = session.query(Admin).filter_by(idAdmin=1).first()
    assert updated_admin.password == "newpassword"


def test_update_admin_password_not_found(setup_database):
    """
    Test: Verify that the method handles the case where the admin is not found.

    Steps:
        1. Ensure no admins exist in the database.
        2. Call the `updateAdminPassword` method with a non-existent admin ID.
        3. Verify the response indicates that the admin is not found.

    Expected Outcome:
        - The method returns a status of "error".
        - The response contains a "Administrador no encontrado" message.
    """

    session = setup_database
    controller = AdminController()

    # Call the method for a non-existent admin
    response = controller.updateAdminPassword(idAdmin=999, new_password="newpassword", session=session)

    # Verify the response
    assert response["status"] == "error"
    assert response["message"] == "Administrador no encontrado"


def test_update_admin_password_database_error(setup_database, mocker):
    """
    Test: Verify that the method handles database errors gracefully.

    Steps:
        1. Mock the database session's commit method to raise an SQLAlchemyError.
        2. Call the `updateAdminPassword` method.
        3. Verify the response indicates a database error.

    Expected Outcome:
        - The method returns a status of "error".
        - The response contains an error message indicating a database issue.
    """

    session = setup_database
    controller = AdminController()

    # Add an admin to the database
    admin = Admin(idAdmin=1, email="admin@example.com", name="Admin", password="oldpassword")
    session.add(admin)
    session.commit()

    # Mock the `commit` method to raise an exception
    mocker.patch("app.controllers.admin_controller.Session.commit", side_effect=SQLAlchemyError("Database error"))

    # Call the method
    response = controller.updateAdminPassword(idAdmin=1, new_password="newpassword", session=session)

    # Verify the response
    assert response["status"] == "error"
    assert "Error de base de datos" in response["message"]


def test_update_admin_password_unexpected_error(setup_database, mocker):
    """
    Test: Verify that the method handles unexpected errors gracefully.

    Steps:
        1. Mock the database session's `query` method to raise a generic exception.
        2. Call the `updateAdminPassword` method.
        3. Verify the response indicates an error occurred.

    Expected Outcome:
        - The method returns a status of "error".
        - The response contains the exception message.
    """

    session = setup_database
    controller = AdminController()

    # Mock the `query` method to raise a generic exception
    mocker.patch("app.controllers.admin_controller.Session.query", side_effect=Exception("Unexpected error"))

    # Call the method
    response = controller.updateAdminPassword(idAdmin=1, new_password="newpassword", session=session)

    # Verify the response
    assert response["status"] == "error"
    assert "Unexpected error" in response["message"]


def test_update_admin_email_success(setup_database):
    """
    Test: Verify that the method successfully updates the email of an admin.

    Steps:
        1. Add an admin to the database.
        2. Call the `updateAdminEmail` method with a new email.
        3. Verify the response indicates success.
        4. Confirm that the email is updated in the database.

    Expected Outcome:
        - The method returns a status of "ok".
        - The admin's email is updated in the database.
    """

    session = setup_database
    controller = AdminController()

    # Add an admin to the database
    admin = Admin(idAdmin=1, email="oldemail@example.com", name="Admin", password="password")
    session.add(admin)
    session.commit()

    # Call the method to update the email
    response = controller.updateAdminEmail(idAdmin=1, new_email="newemail@example.com", session=session)

    # Verify the response
    assert response["status"] == "ok"
    assert response["message"] == "Email actualizado exitosamente"

    # Verify the email in the database
    updated_admin = session.query(Admin).filter_by(idAdmin=1).first()
    assert updated_admin.email == "newemail@example.com"


def test_update_admin_email_not_found(setup_database):
    """
    Test: Verify that the method handles the case where the admin is not found.

    Steps:
        1. Ensure no admins exist in the database.
        2. Call the `updateAdminEmail` method with a non-existent admin ID.
        3. Verify the response indicates that the admin is not found.

    Expected Outcome:
        - The method returns a status of "error".
        - The response contains a "Administrador no encontrado" message.
    """

    session = setup_database
    controller = AdminController()

    # Call the method for a non-existent admin
    response = controller.updateAdminEmail(idAdmin=999, new_email="newemail@example.com", session=session)

    # Verify the response
    assert response["status"] == "error"
    assert response["message"] == "Administrador no encontrado"


def test_update_admin_email_database_error(setup_database, mocker):
    """
    Test: Verify that the method handles database errors gracefully.

    Steps:
        1. Mock the database session's commit method to raise an SQLAlchemyError.
        2. Call the `updateAdminEmail` method.
        3. Verify the response indicates a database error.

    Expected Outcome:
        - The method returns a status of "error".
        - The response contains an error message indicating a database issue.
    """

    session = setup_database
    controller = AdminController()

    # Add an admin to the database
    admin = Admin(idAdmin=1, email="oldemail@example.com", name="Admin", password="password")
    session.add(admin)
    session.commit()

    # Mock the `commit` method to raise an exception
    mocker.patch("app.controllers.admin_controller.Session.commit", side_effect=SQLAlchemyError("Database error"))

    # Call the method
    response = controller.updateAdminEmail(idAdmin=1, new_email="newemail@example.com", session=session)

    # Verify the response
    assert response["status"] == "error"
    assert "Error de base de datos" in response["message"]


def test_update_admin_email_unexpected_error(setup_database, mocker):
    """
    Test: Verify that the method handles unexpected errors gracefully.

    Steps:
        1. Mock the database session's `query` method to raise a generic exception.
        2. Call the `updateAdminEmail` method.
        3. Verify the response indicates an error occurred.

    Expected Outcome:
        - The method returns a status of "error".
        - The response contains the exception message.
    """
    
    session = setup_database
    controller = AdminController()

    # Mock the `query` method to raise a generic exception
    mocker.patch("app.controllers.admin_controller.Session.query", side_effect=Exception("Unexpected error"))

    # Call the method
    response = controller.updateAdminEmail(idAdmin=1, new_email="newemail@example.com", session=session)

    # Verify the response
    assert response["status"] == "error"
    assert "Unexpected error" in response["message"]






