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
        

def test_updateShelterEnergyLevel_success(setup_database, mocker):
    """
    Test to verify that the updateShelterEnergyLevel method correctly updates the energy level of a shelter.

    This test simulates the process of updating the energy level of a shelter in the database.
    It first creates a shelter with an initial energy level of 100, saves it to the database, and then
    calls the updateShelterEnergyLevel method to update the energy level to 80.

    Steps:
        1. Add a shelter to the database.
        2. Call the `updateShelterEnergyLevel` method to update the shelter's energy level.
        3. Verify the response and the updated energy level in the database.
    
    Expected Outcome:
        - The method returns a success message.
        - The shelter's energy level is updated in the database.
    """

    session = setup_database
    controller = ShelterController()

    # Add a shelter
    shelter = Shelter(idShelter=1, shelterName="Main Shelter", maxPeople=50, energyLevel=100, waterLevel=100, radiationLevel=10)
    session.add(shelter)
    session.commit()

    # Update the shelter's energy level
    response = controller.updateShelterEnergyLevel(80, session)

    # Verify the response and databes changes
    assert response == {"status": "ok", "message": "Nivel de energía actualizado exitosamente"}
    updated_shelter = session.query(Shelter).filter(Shelter.idShelter == 1).first()
    assert updated_shelter.energyLevel == 80


def test_updateShelterWaterLevel_success(setup_database, mocker):
    """
    Test to verify that the updateShelterWaterLevel method correctly updates the water level of a shelter.

    This test simulates the process of updating the water level of a shelter in the database.
    It first creates a shelter with an initial water level of 100, saves it to the database, and then
    calls the updateShelterWaterLevel method to update the water level to 80.

    Steps:
        1. Add a shelter to the database.
        2. Call the `updateWaterEnergyLevel` method to update the shelter's energy level.
        3. Verify the response and the updated water level in the database.
    
    Expected Outcome:
        - The method returns a success message.
        - The shelter's water level is updated in the database.
    """

    session = setup_database
    controller = ShelterController()

    # Add a shelter
    shelter = Shelter(idShelter=1, shelterName="Main Shelter", maxPeople=50, energyLevel=100, waterLevel=100, radiationLevel=10)
    session.add(shelter)
    session.commit()

    # Update the shelter's water level
    response = controller.updateShelterWaterLevel(80, session)

    # Verify the response and databes changes
    assert response == {"status": "ok", "message": "Nivel de agua actualizado exitosamente"}
    updated_shelter = session.query(Shelter).filter(Shelter.idShelter == 1).first()
    assert updated_shelter.waterLevel == 80


def test_updateShelterRadiationLevel_success(setup_database):
    """
    Test to verify that the updateShelterRadiationLevel method correctly updates the radiation level of a shelter.

    This test simulates the process of updating the radiation level of a shelter in the database.
    It first creates a shelter with an initial radiation level of 10, saves it to the database, and then
    calls the updateShelterRadiationLevel method to update the radiation level to 8.

    Steps:
        1. Add a shelter to the database.
        2. Call the `updateShelterRadiationLevel` method to update the shelter's radiation level.
        3. Verify the response and the updated radiation level in the database.
    
    Expected Outcome:
        - The method returns a success message.
        - The shelter's radiation level is updated in the database.
    """
    
    session = setup_database
    controller = ShelterController()

    # Add a shelter
    shelter = Shelter(idShelter=1, shelterName="Main Shelter", maxPeople=50, energyLevel=100, waterLevel=100, radiationLevel=10)
    session.add(shelter)
    session.commit()

    # Update the shelter's radiation level
    response = controller.updateShelterRadiationLevel(8, session)

    # Verify the response and databes changes
    assert response == {"status": "ok", "message": "Nivel de radiación actualizado exitosamente"}
    updated_shelter = session.query(Shelter).filter(Shelter.idShelter == 1).first()
    assert updated_shelter.radiationLevel == 8