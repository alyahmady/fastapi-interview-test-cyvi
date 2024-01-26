from pydantic import BaseModel, EmailStr, constr, ConfigDict



class CustomerSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    email: EmailStr
    username: constr(max_length=50) | None = None
    phone: constr(max_length=15) | None = None

    first_name: constr(max_length=150) | None = None
    last_name: constr(max_length=150) | None = None
