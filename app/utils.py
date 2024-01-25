import inspect
from typing import Type, Annotated

from fastapi import Form
from passlib.context import CryptContext
from pydantic import BaseModel

from app.config import Config

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def as_form(cls: Type[BaseModel]) -> Type[BaseModel]:
    new_parameters = [
        inspect.Parameter(
            model_field.alias or field_name,
            inspect.Parameter.POSITIONAL_ONLY,
            default=model_field.default,
            annotation=Annotated[model_field.annotation, *model_field.metadata, Form()],
        )
        for field_name, model_field in cls.model_fields.items()
    ]

    async def as_form_method(**data):
        return cls(**data)

    model_as_form_signature = inspect.signature(as_form_method)
    model_as_form_signature = model_as_form_signature.replace(parameters=new_parameters)
    as_form_method.__signature__ = model_as_form_signature

    setattr(cls, "as_form", as_form_method)
    return cls


async def get_unusable_password() -> str:
    return pwd_context.hash(Config.unusable_password)


async def verify_unusable_password(hashed_password: str) -> bool:
    return pwd_context.verify(Config.unusable_password, hashed_password)
