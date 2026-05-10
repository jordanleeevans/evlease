from database import VEHICLES

# TODO: Replace this with a real database repository in the future.


class VehicleRepository:
    def get_all_vehicles(self) -> list[dict]:
        """Return a list of all vehicles."""
        return VEHICLES

    def get_vehicle_by_id(self, vehicle_id: str) -> dict | None:
        """Return a vehicle by its ID, or None if not found."""
        for vehicle in VEHICLES:
            if vehicle["id"] == vehicle_id:
                return vehicle
        return None
