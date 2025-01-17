from pydantic import BaseModel, EmailStr, constr


class UserRegisterSchema(BaseModel):
    username: str
    phone_number: str = None  # Optional for Gmail users
    email: EmailStr  # Ensure email is a valid email address
    password: constr(min_length=6)
    repeat_password: str

    def validate_passwords(self):
        if self.password != self.repeat_password:
            raise ValueError("Passwords do not match.")


class UserLoginSchema(BaseModel):
    phone_number: str
    password: str
