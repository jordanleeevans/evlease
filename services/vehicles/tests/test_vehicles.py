from main import resolve_vehicle, resolve_vehicles
from repositories import VehicleRepository


class TestVehicleRepository:
    def test_get_vehicle_by_id(self):
        repo = VehicleRepository()
        vehicle = repo.get_vehicle_by_id("1")
        assert vehicle is not None
        assert vehicle["id"] == "1"

    def test_get_all_vehicles(self):
        repo = VehicleRepository()
        vehicles = repo.get_all_vehicles()
        assert vehicles is not None
        assert len(vehicles) > 0

    def test_get_vehicle_by_id_not_found(self):
        repo = VehicleRepository()
        vehicle = repo.get_vehicle_by_id("999")
        assert vehicle is None


class TestVehicleResolvers:
    def test_resolve_vehicles(self):
        vehicles = resolve_vehicles()
        assert vehicles is not None
        assert len(vehicles) > 0

    def test_resolve_vehicle(self):
        vehicle = resolve_vehicle(id="1")
        assert vehicle is not None
        assert vehicle["id"] == "1"
