import pytest
from app.controllers.admin_controller import AdminController
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

def test_delete_admin_success(setup_database):
    """
    Test: Successfully delete an existing admin.

    Steps:
        1. Add an admin to the database.
        2. Delete the admin using its ID.
        3. Verify the response indicates success.
        4. Confirm the admin is no longer in the database.

    Expected Outcome:
        - The admin should be deleted successfully.
        - The admin should no longer exist in the database.

    Arguments:
        setup_database (fixture): The database session used for test setup.
    """
    session = setup_database
    controller = AdminController()

    # Add an admin to delete
    admin_to_delete = Admin(
        idAdmin=1,
        email="delete@example.com",
        name="Admin to Delete",
        password="password123"
    )
    session.add(admin_to_delete)
    session.commit()

    # Delete the admin
    response = controller.deleteAdmin(admin_id=1, session=session)

    assert response == {"status": "ok", "message": "Admin deleted successfully"}

    deleted_admin = session.query(Admin).filter_by(idAdmin=1).first()
    assert deleted_admin is None


def test_delete_admin_not_found(setup_database):
    """
    Test: Attempt to delete a non-existent admin.

    Steps:
        1. Attempt to delete an admin with an ID that doesn't exist.
        2. Verify the response indicates the admin was not found.

    Expected Outcome:
        - The operation should return an error indicating the admin was not found.

    Arguments:
        setup_database (fixture): The database session used for test setup.
    """
    session = setup_database
    controller = AdminController()

    # Attempt to delete a non-existent admin
    response = controller.deleteAdmin(admin_id=999, session=session)

    assert response == {"status": "error", "message": "Admin not found"}


def test_delete_admin_database_error(setup_database, mocker):
    """
    Test: Handle a database error during admin deletion.

    Steps:
        1. Simulate a database error by mocking the session's commit method.
        2. Attempt to delete an admin.
        3. Verify the response indicates a database error.

    Expected Outcome:
        - The operation should return an error response with the exception message.
        - No changes should be made to the database.

    Arguments:
        setup_database (fixture): The database session used for test setup.
        mocker (pytest-mock): Mocking library for simulating errors.
    """
    session = setup_database
    controller = AdminController()

    # Add an admin to simulate error during deletion
    admin_to_delete = Admin(
        idAdmin=2,
        email="error@example.com",
        name="Error Admin",
        password="password123"
    )
    session.add(admin_to_delete)
    session.commit()

    # Mock the commit method to raise an exception
    mocker.patch.object(session, "commit", side_effect=Exception("Database error"))

    response = controller.deleteAdmin(admin_id=2, session=session)

    assert response == {"status": "error", "message": "Database error"}

    remaining_admin = session.query(Admin).filter_by(idAdmin=2).first()
    assert remaining_admin is not None

def test_login_admin_success(setup_database):
    """
    Test: Successfully log in an admin with correct credentials.

    Expected Outcome:
        - The login should be successful, returning the admin's details.
    """
    session = setup_database
    controller = AdminController()

    # Add a test admin
    admin = Admin(email="login@example.com", name="Login Admin", password="correctpassword")
    session.add(admin)
    session.commit()

    response = controller.loginAdmin(email="login@example.com", password="correctpassword", session=session)

    assert response["status"] == "ok"
    assert response["user"]["email"] == "login@example.com"

def test_login_admin_invalid_credentials(setup_database):
    """
    Test: Attempt to log in with invalid credentials.

    Expected Outcome:
        - The operation should fail, returning an error message.
    """
    session = setup_database
    controller = AdminController()

    # Add a test admin
    admin = Admin(email="login@example.com", name="Login Admin", password="correctpassword")
    session.add(admin)
    session.commit()

    # Attempt login with incorrect password
    response = controller.loginAdmin(email="login@example.com", password="wrongpassword", session=session)

    assert response == {"status": "error", "message": "Invalid credentials"}

def test_login_admin_not_found(setup_database):
    """
    Test: Attempt to log in with an email not in the database.

    Expected Outcome:
        - The operation should fail, returning an error message.
    """
    session = setup_database
    controller = AdminController()

    response = controller.loginAdmin(email="nonexistent@example.com", password="password", session=session)

    assert response == {"status": "error", "message": "Invalid credentials"}

def test_list_admins_success(setup_database):
    """
    Test: List all admins successfully.

    Expected Outcome:
        - All admins in the database should be returned in the response.
    """
    session = setup_database
    controller = AdminController()

    # Add test admins
    admin1 = Admin(email="admin1@example.com", name="Admin 1", password="password1")
    admin2 = Admin(email="admin2@example.com", name="Admin 2", password="password2")
    session.add_all([admin1, admin2])
    session.commit()

    response = controller.listAdmins(session=session)

    assert response["status"] == "ok"
    assert len(response["admins"]) == 2
    assert response["admins"][0]["email"] == "admin1@example.com"
    assert response["admins"][1]["email"] == "admin2@example.com"

def test_list_admins_empty(setup_database):
    """
    Test: List admins when no admins exist in the database.

    Expected Outcome:
        - The response should indicate success with an empty list of admins.
    """
    session = setup_database
    controller = AdminController()

    response = controller.listAdmins(session=session)

    assert response == {"status": "ok", "admins": []}

def test_update_admin_password_success(setup_database):
    """
    Test: Successfully update an admin's password.

    Expected Outcome:
        - The password should be updated in the database.
    """
    session = setup_database
    controller = AdminController()

    # Add a test admin
    admin = Admin(idAdmin=1, email="password@example.com", name="Password Admin", password="oldpassword")
    session.add(admin)
    session.commit()

    response = controller.updateAdminPassword(idAdmin=1, new_password="newpassword", session=session)

    assert response == {"status": "ok", "message": "Contraseña actualizada exitosamente"}
    updated_admin = session.query(Admin).filter_by(idAdmin=1).first()
    assert updated_admin.password == "newpassword"


def test_update_admin_password_not_found(setup_database):
    """
    Test: Attempt to update the password of a non-existent admin.

    Expected Outcome:
        - The operation should fail, returning an error message.
    """
    session = setup_database
    controller = AdminController()

    response = controller.updateAdminPassword(idAdmin=999, new_password="newpassword", session=session)

    assert response == {"status": "error", "message": "Administrador no encontrado"}

def test_update_admin_email_success(setup_database):
    """
    Test: Successfully update an admin's email.

    Expected Outcome:
        - The email should be updated in the database.
    """
    session = setup_database
    controller = AdminController()

    # Add a test admin
    admin = Admin(idAdmin=1, email="oldemail@example.com", name="Email Admin", password="password")
    session.add(admin)
    session.commit()

    response = controller.updateAdminEmail(idAdmin=1, new_email="newemail@example.com", session=session)

    assert response == {"status": "ok", "message": "Email actualizado exitosamente"}
    updated_admin = session.query(Admin).filter_by(idAdmin=1).first()
    assert updated_admin.email == "newemail@example.com"


def test_update_admin_email_not_found(setup_database):
    """
    Test: Attempt to update the email of a non-existent admin.

    Expected Outcome:
        - The operation should fail, returning an error message.
    """
    session = setup_database
    controller = AdminController()

    response = controller.updateAdminEmail(idAdmin=999, new_email="newemail@example.com", session=session)

    assert response == {"status": "error", "message": "Administrador no encontrado"}


def test_update_admin_name_success(setup_database):
    """
    Test: Successfully update an admin's name.

    Expected Outcome:
        - The name should be updated in the database.
    """
    session = setup_database
    controller = AdminController()

    # Add a test admin
    admin = Admin(idAdmin=1, email="name@example.com", name="Old Name", password="password")
    session.add(admin)
    session.commit()

    response = controller.updateAdminName(idAdmin=1, new_name="New Name", session=session)

    assert response == {"status": "ok", "message": "Nombre actualizado exitosamente"}
    updated_admin = session.query(Admin).filter_by(idAdmin=1).first()
    assert updated_admin.name == "New Name"


def test_update_admin_name_not_found(setup_database):
    """
    Test: Attempt to update the name of a non-existent admin.

    Expected Outcome:
        - The operation should fail, returning an error message.
    """
    session = setup_database
    controller = AdminController()

    response = controller.updateAdminName(idAdmin=999, new_name="New Name", session=session)

    assert response == {"status": "error", "message": "Administrador no encontrado"}

def test_get_admin_by_id_success(setup_database):
    """
    Test: Successfully retrieve an admin by ID.

    Expected Outcome:
        - The admin's details should be returned correctly.
    """
    session = setup_database
    controller = AdminController()

    # Add a test admin
    admin = Admin(idAdmin=1, email="admin@example.com", name="Test Admin", password="password123")
    session.add(admin)
    session.commit()

    response = controller.getAdminById(idAdmin=1, session=session)

    assert response["status"] == "ok"
    assert response["admin"]["email"] == "admin@example.com"
    assert response["admin"]["name"] == "Test Admin"
    assert response["admin"]["password"] == "password123"


def test_get_admin_by_id_not_found(setup_database):
    """
    Test: Attempt to retrieve an admin with a non-existent ID.

    Expected Outcome:
        - The operation should fail, returning an error message.
    """
    session = setup_database
    controller = AdminController()

    response = controller.getAdminById(idAdmin=999, session=session)

    assert response == {"status": "error", "message": "Administrador no encontrado"}


def test_get_admin_by_id_database_error(setup_database, mocker):
    """
    Test: Simulate a database error during admin retrieval.

    Expected Outcome:
        - The operation should fail, returning the database error message.
    """
    session = setup_database
    controller = AdminController()

    # Mock session.query to raise an exception
    mocker.patch("sqlalchemy.orm.Session.query", side_effect=Exception("Database error"))

    response = controller.getAdminById(idAdmin=1, session=session)

    assert response["status"] == "error"
    assert "Database error" in response["message"]



