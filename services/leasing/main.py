import logging

from ariadne import QueryType, load_schema_from_path
from ariadne.asgi import GraphQL
from ariadne.contrib.federation import make_federated_schema
from fastapi import FastAPI

from repositories import LeasingRepository

logging.basicConfig(level=logging.INFO)

schema_str = load_schema_from_path("schema.graphql")
query = QueryType()
repo = LeasingRepository()


@query.field("leaseQuote")
def resolve_lease_quote(*_, vehicle_id, term_months, annual_mileage_miles):
    return repo.calculate_quote(vehicle_id, term_months, annual_mileage_miles)


@query.field("leasePlans")
def resolve_lease_plans(*_, vehicle_id):
    return repo.get_lease_plans(vehicle_id)


# LeaseQuote.vehicle must return an object with __typename so the router
# can resolve the full Vehicle fields via the vehicles subgraph.
def resolve_lease_quote_vehicle(quote, *_):
    return {"__typename": "Vehicle", "id": quote["vehicle_id"]}


schema = make_federated_schema(
    schema_str,
    [query],
    convert_names_case=True,
)

# Bind the vehicle field resolver manually (LeaseQuote is not a federated
# entity, so we can't use FederatedObjectType for this)
schema.type_map["LeaseQuote"].fields["vehicle"].resolve = resolve_lease_quote_vehicle

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


app.mount("/graphql/", GraphQL(schema, debug=True))
