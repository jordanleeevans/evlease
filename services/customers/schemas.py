from uuid import UUID
from pydantic import BaseModel, EmailStr, SecretStr
from pydantic import EmailStr

class CustomerLogin(BaseModel):
    email: EmailStr
    password: SecretStr
    name: str

class CustomerRegister(BaseModel):
    email: EmailStr
    password: SecretStr
    name: str

class Customer(BaseModel):
    id: UUID
    email: EmailStr
    name: str

class AuthPayload(BaseModel):
    token: str
    customer: Customer

class CustomerRecord(BaseModel):
    id: UUID
    email: EmailStr
    name: str
    hashed_password: str