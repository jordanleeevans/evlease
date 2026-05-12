import os
import uuid
from datetime import UTC, datetime, timedelta

import jwt
from passlib.context import CryptContext

import database
from schemas import Customer, AuthPayload, CustomerLogin, CustomerRegister, CustomerRecord

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

_JWT_SECRET = os.environ.get("JWT_SECRET", "change-me-in-production")
_JWT_ALGORITHM = "HS256"
_JWT_EXPIRY_HOURS = 24


class AuthError(Exception):
    """Raised when authentication fails."""
    pass


class CustomerRepository:
    def get_customer_by_id(self, customer_id: str) -> Customer | None:
        record = database.get_by_id(customer_id)
        if record is None:
            return None
        return Customer(id=record.id, email=record.email, name=record.name)

    def register(self, customer: CustomerRegister) -> AuthPayload:
        if database.get_by_email(customer.email) is not None:
            raise AuthError("An account with that email already exists.")

        record = CustomerRecord(
            id=uuid.uuid4(),
            email=customer.email,
            name=customer.name,
            hashed_password=_pwd_context.hash(customer.password.get_secret_value()),
        )
        database.insert(record)
        return self._build_payload(record)

    def login(self, customer: CustomerLogin) -> AuthPayload:
        record = database.get_by_email(customer.email)

        if record is None:
            raise AuthError("Invalid email.")

        password_verified = _pwd_context.verify(customer.password.get_secret_value(), record.hashed_password)

        if not password_verified:
            raise AuthError("Invalid password.")

        return self._build_payload(record)

    def _build_payload(self, record: CustomerRecord) -> AuthPayload:
        customer = Customer(id=record.id, email=record.email, name=record.name)
        token = jwt.encode(
            {
                "sub": str(record.id),
                "exp": datetime.now(UTC) + timedelta(hours=_JWT_EXPIRY_HOURS),
            },
            _JWT_SECRET,
            algorithm=_JWT_ALGORITHM,
        )
        return AuthPayload(token=token, customer=customer)

