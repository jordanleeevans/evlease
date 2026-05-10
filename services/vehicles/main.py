import logging
import os

from ariadne import QueryType, load_schema_from_path
from ariadne.asgi import GraphQL
from ariadne.contrib.federation import FederatedObjectType, make_federated_schema
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from repositories import VehicleRepository

logging.basicConfig(level=logging.INFO)

_otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://jaeger:4317")
_resource = Resource.create({"service.name": "vehicles"})
_provider = TracerProvider(resource=_resource)
_provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint=_otlp_endpoint))
)
trace.set_tracer_provider(_provider)

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
FastAPIInstrumentor.instrument_app(app)


@app.get("/health")
def health():
    return {"status": "ok"}


app.mount("/graphql/", GraphQL(schema, debug=True))
