from app.controllers.resident_controller import ResidentController
from app.controllers.room_controller import RoomController
from app.controllers.family_controller import FamilyController
from app.controllers.shelter_controller import ShelterController
from app.controllers.machine_controller import MachineController
from app.controllers.alarm_controller import AlarmController
from app.controllers.admin_controller import AdminController


# Crear instancias de los controladores
resident_controller = ResidentController()
room_controller = RoomController()
family_controller = FamilyController()
shelter_controller = ShelterController()
machine_controller = MachineController()
alarm_controller = AlarmController()
admin_controller = AdminController()


class Controllers:
    def __init__(self) -> None:
        pass

    def healthz(self):
        """
        Checks server status
        """
        return {"status": "ok"}
    
    def create_resident(self, body, session=None):
        return resident_controller.create_resident(body, session)

    def delete_resident(self, idResident, session=None):
        return resident_controller.delete_resident(idResident, session)

    def update_resident(self, idResident, updates, session=None):
        return resident_controller.update_resident(idResident, updates, session)

    def create_room(self, body, session=None):
        return room_controller.create_room(body, session)

    def list_rooms_with_resident_count(self, session=None):
        return room_controller.list_rooms_with_resident_count(session)

    def access_room(self, idResident, idRoom, session=None):
        return room_controller.access_room(idResident, idRoom, session)

    def create_family(self, body, session=None):
        return family_controller.create_family(body, session)

    def get_shelter_energy_level(self, session=None):
        return shelter_controller.get_shelter_energy_level(session)

    def get_shelter_water_level(self, session=None):
        return shelter_controller.get_shelter_water_level(session)

    def get_shelter_radiation_level(self, session=None):
        return shelter_controller.get_shelter_radiation_level(session)

    def create_machine(self, body, session=None):
        return machine_controller.create_machine(body, session)

    def create_alarm(self, body, session=None):
        return alarm_controller.create_alarm(body, session)

    def create_admin(self, admin_data, session=None):
        return admin_controller.create_admin(admin_data, session)

    def list_residents_in_room(self, idRoom, session=None):
        return resident_controller.list_residents_in_room(idRoom, session)
    
    def list_residents(self, session=None):
        return resident_controller.list_residents(session)

    def login(self, name, surname, session=None):
        return resident_controller.login(name, surname, session)

    def loginAdmin(self, email, password, session=None):
        return admin_controller.loginAdmin(email, password,session)
    
    def list_rooms(self, session=None):
        return room_controller.list_rooms(session)
    
    def deleteAdmin(self, admin_id, session=None):
        return admin_controller.deleteAdmin(admin_id, session)
    
    def listAdmins(self, session=None):
        return admin_controller.listAdmins(session)

    def getAdminById(self, admin_id, session=None):
        return admin_controller.getAdminById(admin_id, session)
    
    def updateAdminPassword(self, idAdmin, new_password, session=None):
        return admin_controller.updateAdminPassword(idAdmin, new_password, session)
    
    def updateAdminEmail(self, idAdmin, new_email, session=None):
        return admin_controller.updateAdminEmail(idAdmin, new_email, session)
    
    def updateAdminName(self, idAdmin, new_name, session=None):
        return admin_controller.updateAdminName(idAdmin, new_name, session)
    
    def updateShelterEnergyLevel(self, new_energy_level, session=None):
        return shelter_controller.updateShelterEnergyLevel(new_energy_level, session)
    
    def updateShelterWaterLevel(self, new_water_level, session=None):
        return shelter_controller.updateShelterWaterLevel(new_water_level, session)
    
    def updateShelterRadiationLevel(self, new_radiation_level, session=None):
        return shelter_controller.updateShelterRadiationLevel(new_radiation_level, session)
    
    def updateMachineStatus(self, machine_name, session=None):
        return machine_controller.updateMachineStatus(machine_name)
    
    def updateMachineStatusOn(self, machine_name, session=None):
        return machine_controller.updateMachineStatusOn(machine_name)
    
    def updateResidentRoom(self, resident_id, new_room_id, session=None):
        return resident_controller.updateResidentRoom(resident_id, new_room_id)
    
    def getResidentById(self, idResident, session=None):
        return resident_controller.getResidentById(idResident, session)
    
    def create_alarmLevel(self, body, session=None):
        return alarm_controller.create_alarmLevel(body, session)
    
    def updateAlarmEndDate(self, idAlarm, new_enddate, session=None):
        return alarm_controller.updateAlarmEndDate(idAlarm, new_enddate)
    
    def list_alarms(self, session=None):
        return alarm_controller.list_alarms(session)
    
    def list_machines(self, session=None):
        return machine_controller.list_machines(session)

    def deleteMachine(self, machine_id, session=None):
        return machine_controller.deleteMachine(machine_id,session)
    
    def updateMachineDate(self, machine_name, session=None):
        return machine_controller.updateMachineDate(machine_name,session)

    def updateRoomName(self, idRoom, new_name, session=None):
        return room_controller.updateRoomName(idRoom, new_name)