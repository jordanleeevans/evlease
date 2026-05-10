from fastapi.testclient import TestClient

from main import app, resolve_vehicle, resolve_vehicles
from repositories import VehicleRepository

client = TestClient(app)


class TestVehicleRepository:
    def test_get_vehicle_by_id(self):
        repo = VehicleRepository()
        vehicle = repo.get_vehicle_by_id("1")
        assert vehicle is not None
        assert vehicle["id"].isnumeric()

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
        assert vehicle["id"].isnumeric()


class TestFederation:
    def test_service_sdl(self):
        """Subgraph must expose _service { sdl } for Apollo Router to compose it."""
        response = client.post(
            "/graphql/",
            json={"query": "{ _service { sdl } }"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data
        sdl = data["data"]["_service"]["sdl"]
        assert "Vehicle" in sdl
        assert "@key" in sdl

    def test_entities_reference_resolver(self):
        """Gateway uses _entities to resolve a Vehicle by its @key."""
        response = client.post(
            "/graphql/",
            json={
                "query": """
                    query($representations: [_Any!]!) {
                        _entities(representations: $representations) {
                            ... on Vehicle {
                                id
                                make
                                model
                            }
                        }
                    }
                """,
                "variables": {
                    "representations": [{"__typename": "Vehicle", "id": "1"}]
                },
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data
        entity = data["data"]["_entities"][0]
        assert entity["id"].isnumeric()
        assert entity["make"] not in ["", None]
