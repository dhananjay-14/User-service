from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    access_token: str
    token_type:   str

class TokenData(BaseModel):
    user_id: int | None = None

class UserLogin(BaseModel):
    email:    EmailStr
    password: str
