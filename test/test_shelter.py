import pytest
from app.controllers.shelter_controller import ShelterController
from app.mysql.shelter import Shelter
from sqlalchemy.orm import Session


def test_get_shelter_energy_level_success(setup_database):
    """
    Test: Retrieve the energy level of a shelter.

    Steps:
        1. Add a shelter with specific energy level to the database.
        2. Call the `get_shelter_energy_level` method.
        3. Verify the returned energy level matches the database record.

    Expected Outcome:
        - The energy level should be correctly retrieved.
    """
    session = setup_database
    controller = ShelterController()

    # Add a shelter with an energy level
    shelter = Shelter(idShelter=1, shelterName="Main Shelter", energyLevel=80, waterLevel=90, radiationLevel=10)
    session.add(shelter)
    session.commit()

    response = controller.get_shelter_energy_level(session=session)

    assert response == {"energyLevel": 80}


def test_get_shelter_water_level_success(setup_database):
    """
    Test: Retrieve the water level of a shelter.

    Steps:
        1. Add a shelter with specific water level to the database.
        2. Call the `get_shelter_water_level` method.
        3. Verify the returned water level matches the database record.

    Expected Outcome:
        - The water level should be correctly retrieved.
    """
    session = setup_database
    controller = ShelterController()

    # Add a shelter with a water level
    shelter = Shelter(idShelter=1, shelterName="Main Shelter", energyLevel=80, waterLevel=90, radiationLevel=10)
    session.add(shelter)
    session.commit()

    response = controller.get_shelter_water_level(session=session)

    assert response == {"waterLevel": 90}


def test_get_shelter_radiation_level_success(setup_database):
    """
    Test: Retrieve the radiation level of a shelter.

    Steps:
        1. Add a shelter with specific radiation level to the database.
        2. Call the `get_shelter_radiation_level` method.
        3. Verify the returned radiation level matches the database record.

    Expected Outcome:
        - The radiation level should be correctly retrieved.
    """
    session = setup_database
    controller = ShelterController()

    # Add a shelter with a radiation level
    shelter = Shelter(idShelter=1, shelterName="Main Shelter", energyLevel=80, waterLevel=90, radiationLevel=10)
    session.add(shelter)
    session.commit()

    response = controller.get_shelter_radiation_level(session=session)

    assert response == {"radiationLevel": 10}


def test_get_shelter_no_shelter_found(setup_database):
    """
    Test: Handle the case where no shelter is found in the database.

    Steps:
        1. Ensure the shelter table is empty.
        2. Call any of the methods (`get_shelter_energy_level`, `get_shelter_water_level`, or `get_shelter_radiation_level`).
        3. Verify that the method raises a `ValueError`.

    Expected Outcome:
        - A `ValueError` should be raised with the appropriate message.
    """
    session = setup_database
    controller = ShelterController()

    with pytest.raises(ValueError, match="No shelter found in the database."):
        controller.get_shelter_energy_level(session=session)

    with pytest.raises(ValueError, match="No shelter found in the database."):
        controller.get_shelter_water_level(session=session)

    with pytest.raises(ValueError, match="No shelter found in the database."):
        controller.get_shelter_radiation_level(session=session)
