import logging

from database import VEHICLES

logger = logging.getLogger(__name__)

# TODO: Replace this with a real database repository in the future.


class VehicleRepository:
    def get_all_vehicles(self) -> list[dict]:
        """Return a list of all vehicles."""
        logger.info("Fetching all vehicles from the repository.")
        return VEHICLES

    def get_vehicle_by_id(self, vehicle_id: str) -> dict | None:
        """Return a vehicle by its ID, or None if not found."""
        logger.info(f"Fetching vehicle with ID {vehicle_id} from the repository.")
        for vehicle in VEHICLES:
            if vehicle["id"] == vehicle_id:
                logger.info(f"Vehicle with ID {vehicle_id} found.")
                return vehicle
        logger.info(f"Vehicle with ID {vehicle_id} not found.")
        return None
