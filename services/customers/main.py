import logging
import os

from ariadne import MutationType, QueryType, load_schema_from_path
from ariadne.asgi import GraphQL
from ariadne.contrib.federation import FederatedObjectType, make_federated_schema
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from repositories import CustomerRepository
from repositories.customers import AuthError

logging.basicConfig(level=logging.INFO)

_otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://jaeger:4317")
_resource = Resource.create({"service.name": "customers"})
_provider = TracerProvider(resource=_resource)
_provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint=_otlp_endpoint))
)
trace.set_tracer_provider(_provider)

schema_str = load_schema_from_path("schema.graphql")

query = QueryType()
mutation = MutationType()
customer_type = FederatedObjectType("Customer")
repo = CustomerRepository()


@query.field("me")
def resolve_me(*_):
    return None


@mutation.field("register")
def resolve_register(*_, email, password, name):
    try:
        return {"payload": repo.register(email, password, name)}
    except AuthError as e:
        raise ValueError(str(e)) from e


@mutation.field("login")
def resolve_login(*_, email, password):
    try:
        return {"payload": repo.login(email, password)}
    except AuthError as e:
        raise ValueError(str(e)) from e


@customer_type.reference_resolver
def resolve_customer_reference(_, _info, representation):
    return repo.get_customer_by_id(representation["id"])


schema = make_federated_schema(
    schema_str, query, mutation, customer_type, convert_names_case=True
)

app = FastAPI()
FastAPIInstrumentor.instrument_app(app)


@app.get("/health")
def health():
    return {"status": "ok"}


app.mount("/graphql", GraphQL(schema, debug=True))
