from ariadne import QueryType, load_schema_from_path, make_executable_schema
from ariadne.asgi import GraphQL
from fastapi import FastAPI

from repositories import VehicleRepository

schema = load_schema_from_path("schema.graphql")

query = QueryType()


@query.field("vehicles")
def resolve_vehicles(*_):
    repo = VehicleRepository()
    return repo.get_all_vehicles()


@query.field("vehicle")
def resolve_vehicle(*_, id):
    repo = VehicleRepository()
    return repo.get_vehicle_by_id(id)


# Create executable schema instance
schema = make_executable_schema(schema, query, convert_names_case=True)

# Mount Ariadne GraphQL as sub-application for FastAPI
app = FastAPI()

app.mount("/graphql/", GraphQL(schema, debug=True))
