import logging

from ariadne import QueryType, load_schema_from_path
from ariadne.asgi import GraphQL
from ariadne.contrib.federation import FederatedObjectType, make_federated_schema
from fastapi import FastAPI

from repositories import VehicleRepository

logging.basicConfig(level=logging.INFO)

schema = load_schema_from_path("schema.graphql")

query = QueryType()
vehicle_type = FederatedObjectType("Vehicle")


@query.field("vehicles")
def resolve_vehicles(*_):
    repo = VehicleRepository()
    return repo.get_all_vehicles()


@query.field("vehicle")
def resolve_vehicle(*_, id):
    repo = VehicleRepository()
    return repo.get_vehicle_by_id(id)


@vehicle_type.reference_resolver
def resolve_vehicle_reference(_, _info, representation):
    repo = VehicleRepository()
    return repo.get_vehicle_by_id(representation["id"])


# Create executable schema instance
schema = make_federated_schema(schema, query, vehicle_type, convert_names_case=True)

# Mount Ariadne GraphQL as sub-application for FastAPI
app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


app.mount("/graphql/", GraphQL(schema, debug=True))
