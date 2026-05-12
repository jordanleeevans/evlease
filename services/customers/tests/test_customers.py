import uuid
import jwt
import pytest
from repositories.customers import _JWT_ALGORITHM, _JWT_SECRET, CustomerRepository
from schemas import AuthPayload, CustomerLogin, CustomerRecord
class TestCustomerRepository:

    def test_build_payload_returns_token_and_customer(self):
        customer_record = CustomerRecord(
            id=uuid.uuid4(),
            email="john.doe@email.com",
            name="John Doe",
            hashed_password="some-hashed-password"
        )

        result = CustomerRepository()._build_payload(customer_record)

        assert isinstance(result, AuthPayload)

        encoded_token = result.token
        decoded_token = jwt.decode(encoded_token, _JWT_SECRET, algorithms=[_JWT_ALGORITHM])

        assert decoded_token.get("sub") == str(customer_record.id)
        
    
    @pytest.mark.skip(reason="TODO")
    def test_login_with_no_record_raises_auth_error(self):
        pass

    @pytest.mark.skip(reason="TODO")
    def test_login_with_wrong_password_raises_auth_error(self):
        pass

    def test_get_customer_by_id_returns_none_for_unknown_id(self):
        repo = CustomerRepository()
        assert repo.get_customer_by_id("nonexistent") is None
    
    @pytest.mark.skip(reason="TODO")
    def test_get_customer_by_id_returns_customer(self):
        pass