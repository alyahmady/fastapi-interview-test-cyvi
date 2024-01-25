import inspect
from typing import Type, Annotated

from fastapi import Form
from pydantic import BaseModel


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
