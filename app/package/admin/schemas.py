from pydantic import BaseModel, constr, ConfigDict

from app.utils import as_form


@as_form
class LoginSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    username: constr(max_length=50)
    password: constr(min_length=8)
