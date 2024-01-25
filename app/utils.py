import inspect
from typing import Type

from fastapi import Form
from pydantic import BaseModel
from pydantic.fields import FieldInfo


def as_form(cls: Type[BaseModel]):
    new_parameters = []

    for _, field in cls.model_fields.items():
        field: FieldInfo

        default_value = Form(field.default)
        if field.is_required():
            default_value = Form(...)

        new_parameters.append(
            inspect.Parameter(
                field.alias,
                inspect.Parameter.POSITIONAL_ONLY,
                default=default_value,
                annotation=field.annotation,
            )
        )

    async def as_form_func(**data):
        return cls(**data)

    sig = inspect.signature(as_form_func)
    sig = sig.replace(parameters=new_parameters)
    as_form_func.__signature__ = sig

    setattr(cls, "as_form", as_form_func)

    return cls
