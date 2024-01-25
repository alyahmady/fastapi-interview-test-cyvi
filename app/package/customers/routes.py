from typing import Annotated, Iterable

from fastapi import APIRouter, Query, status
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, insert, update, true, CursorResult, Result
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import UserRole
from app.models import User
from app.package.customers.schemas import CustomerSchema

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def customers_list(
    *,
    request: Request,
    db: AsyncSession,
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=0, le=50)] = 10,
):
    customers: Iterable[User] = await db.scalars(
        select(User)
        .where(User.is_active == true(), User.role == UserRole.CUSTOMER)
        .offset((page - 1) * size)
        .limit(size)
    )
    return templates.TemplateResponse(
        request=request, name="customers/list.html", context={"customers": customers}
    )


@router.get("/{customer_id}/", response_class=HTMLResponse)
async def customer_detail(
    *,
    request: Request,
    db: AsyncSession,
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
            name="customer_detail.html",
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
    db: AsyncSession,
    customer: CustomerSchema,
):
    await db.execute(
        insert(User).values(
            **customer.model_dump(), is_active=True, role=UserRole.CUSTOMER
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
    db: AsyncSession,
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
    db: AsyncSession,
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
    db: AsyncSession,
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
