from pydantic import BaseModel

class SignUpSchema(BaseModel):
    email:str
    password:str

class LogininSchema(BaseModel):
    email:str
    password:str

# class Student(BaseModel):
#     name: str
#     age: int
#     grade: int
    
class TokenSchema(BaseModel):
    token: str

class UserSchema(BaseModel):
    uid: str
    email: str
    user_type: str
    name: str
    age: int
    organization: str

