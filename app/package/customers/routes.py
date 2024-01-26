import math
from typing import Annotated, Iterable

from fastapi import APIRouter, Query, status, Depends
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, insert, update, true, CursorResult, Result, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import Password
from app.config import Config
from app.db import get_db
from app.enums import UserRole
from app.models import User
from app.package.customers.schemas import CustomerSchema

router = APIRouter()

templates = Jinja2Templates(directory=Config.base_directory / "templates")


@router.get("/", response_class=HTMLResponse)
async def customers_list(
    *,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=0, le=50)] = 10,
):
    customers: Iterable[User] = await db.scalars(
        select(User)
        .where(User.is_active == true(), User.role == UserRole.CUSTOMER)
        .order_by(User.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    )

    customers_count: int = await db.scalar(
        select(func.count("*"))
        .select_from(User)
        .where(User.is_active == true(), User.role == UserRole.CUSTOMER)
    )
    pages_count = math.ceil(customers_count / size)

    return templates.TemplateResponse(
        request=request,
        name="customers/list.html",
        context={
            "customers": customers,
            "pages_count": pages_count,
            "current_page": page,
            "current_size": size,
        },
    )


@router.get("/{customer_id}/", response_class=HTMLResponse)
async def customer_detail(
    *,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    customer_id: int,
):
    customer: User = await db.scalar(
        select(User).where(
            User.is_active == true(),
            User.role == UserRole.CUSTOMER,
            User.id == customer_id,
        )
    )
    if not customer:
        return templates.TemplateResponse(
            request=request,
            name="customers/detail.html",
            context={"customer": None},
            status_code=404,
        )
    return templates.TemplateResponse(
        request=request, name="customers/detail.html", context={"customer": customer}
    )


@router.get("/create/", response_class=HTMLResponse)
async def customer_create(
    *,
    request: Request,
):
    return templates.TemplateResponse(
        request=request, name="customers/create.html", context={}
    )


@router.post("/create/", response_class=HTMLResponse)
async def customer_create_form(
    *,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    customer: CustomerSchema,
):
    await db.execute(
        insert(User).values(
            **customer.model_dump(),
            is_active=True,
            role=UserRole.CUSTOMER,
            hashed_password=await Password.get_unusable(),
        )
    )
    await db.commit()

    return templates.TemplateResponse(
        request=request,
        name="customers/list.html",
        context={"message": "Customer created successfully."},
    )


@router.get("/{customer_id}/update/", response_class=HTMLResponse)
async def customer_update(
    *,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    customer_id: int,
):
    customer: User = await db.scalar(
        select(User).where(
            User.is_active == true(),
            User.role == UserRole.CUSTOMER,
            User.id == customer_id,
        )
    )
    if not customer:
        return templates.TemplateResponse(
            request=request,
            name="404.html",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return templates.TemplateResponse(
        request=request, name="customers/update.html", context={"customer": customer}
    )


@router.put("/{customer_id}/update/", response_class=HTMLResponse)
async def customer_update_form(
    *,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    customer_id: int,
    customer: CustomerSchema,
):
    updated_customer: User = await db.scalar(
        update(User)
        .returning(User)
        .where(
            User.id == customer_id,
            User.is_active == true(),
            User.role == UserRole.CUSTOMER,
        )
        .values(**customer.model_dump(exclude_none=True))
    )
    if not updated_customer:
        return templates.TemplateResponse(
            request=request,
            name="404.html",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    await db.commit()

    return templates.TemplateResponse(
        request=request,
        name="customers/detail.html",
        context={
            "message": "Customer updated successfully.",
            "customer": updated_customer,
        },
    )


@router.delete("/{customer_id}/delete/", response_class=HTMLResponse)
async def customer_delete(
    *,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    customer_id: int,
):
    result: Result | CursorResult = await db.scalar(
        update(User)
        .where(
            User.id == customer_id,
            User.is_active == true(),
            User.role == UserRole.CUSTOMER,
        )
        .values(is_active=False)
    )
    if not result.rowcount:
        return templates.TemplateResponse(
            request=request,
            name="404.html",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    await db.commit()

    return templates.TemplateResponse(
        request=request,
        name="customers/list.html",
        context={"message": "Customer deleted successfully."},
    )
