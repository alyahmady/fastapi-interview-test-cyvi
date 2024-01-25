from pydantic import BaseModel, EmailStr, constr

from app.utils import as_form


@as_form
class CustomerSchema(BaseModel):
    email: EmailStr
    username: constr(max_length=50) | None = None
    phone: constr(max_length=15) | None = None

    first_name: constr(max_length=150) | None = None
    last_name: constr(max_length=150) | None = None

