"""In-memory customer store. Replace with a real database later."""

from schemas import CustomerRecord


# Keyed by customer id
_customers_by_id: dict[str, CustomerRecord] = {}
# Secondary index for login lookups
_customers_by_email: dict[str, CustomerRecord] = {}


def get_by_id(customer_id: str) -> CustomerRecord | None:
    return _customers_by_id.get(customer_id)


def get_by_email(email: str) -> CustomerRecord | None:
    return _customers_by_email.get(email)


def insert(record: CustomerRecord) -> None:
    _customers_by_id[record.id] = record
    _customers_by_email[record.email] = record
