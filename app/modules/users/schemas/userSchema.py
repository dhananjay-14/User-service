from pydantic import BaseModel, EmailStr, constr, IPvAnyAddress
from enum import Enum

# supported gender identities
class GenderEnum(str, Enum):
    male = "Male"
    female = "Female"
    non_binary = "Non-binary"
    agender = "Agender"
    bigender = "Bigender"
    genderqueer = "Genderqueer"
    polygender = "Polygender"
    genederfluid = "Genderfluid"


# user roles and permissions
class RoleEnum(str, Enum):
    user        = "user"
    admin       = "admin"
    superadmin  = "superadmin"


# Base schema with common user fields and validation
class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    gender: GenderEnum
    ip_address: str
    password: str

# Schema for creating new users, includes default role assignment
class UserCreate(UserBase):
    password: str
    role: RoleEnum = RoleEnum.user


# Schema for updating existing users; all fields are optional
class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name:  str | None = None
    gender:     str | None       = None
    email:      EmailStr | None = None
    ip_address: str | None = None
    password: str | None = None


# Schema for returning user data via API responses
class UserOut(BaseModel):
    id:         int
    first_name: str
    last_name:  str
    email:      EmailStr
    gender:     str
    ip_address: str
    role:       RoleEnum

    model_config = {
        "from_attributes": True  
    }
