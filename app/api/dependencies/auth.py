"""
Модуль с зависимостями аутентификации
"""

from typing import Annotated

import pydantic_core
from fastapi import Cookie, Depends, Header, HTTPException
from jwt import InvalidTokenError, decode
from pydantic import BaseModel, Field
from starlette import status

from client.c300.models.employee import EmployeeC300, ExternalControl
from client.c300.models.tenant import TenantC300
from config import settings


class AuthPayload(BaseModel):
    user_number: str = Field(
        validation_alias="profile",
        title="Лицевой счет пользователя",
    )
    external_control_number: str = Field(
        validation_alias="username",
        title="Лицевой счет человека, который зашел под внешнее управление",
    )
    is_superuser: bool = Field(
        title="Суперпользователь?",
    )
    user_type: int = Field(
        validation_alias="type",
        title="Тип пользователя, 0 - Tenant, 1 - Employee",
    )


class Auth:
    """
    Класс с функциями аутентификации
    """

    @classmethod
    async def tenant(cls, access_token: str | None = Cookie(None)) -> TenantC300:
        """
        Функция для аутентификации жителя

        Args:
            access_token (str, None): Токен авторизации. Defaults to None.

        Raises:
            HTTPException: При неуспешной авторизации

        Returns:
            TenantC300: Житель
        """
        payload = await cls._parse_token(access_token)
        if payload.user_type != 0:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid account type")
        tenant = await TenantC300.get_by_number(payload.user_number)
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tenant not found",
            )
        return tenant

    @classmethod
    async def employee(cls, access_token: str | None = Cookie(None)) -> EmployeeC300:
        """
        Функция для аутентификации работника

        Args:
            access_token (str, None): Токен авторизации. Defaults to None.

        Raises:
            HTTPException: При неуспешной авторизации

        Returns:
            EmployeeC300: Работник
        """

        payload = await cls._parse_token(access_token)
        if payload.user_type != 1:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid account type")
        employee = await EmployeeC300.get_by_number(payload.user_number)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Employee not found",
            )
        if payload.external_control_number != payload.user_number:
            external_control_employee = await EmployeeC300.get_by_number(payload.external_control_number)
            if not external_control_employee:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="External control employee not found",
                )
            external_control = ExternalControl(
                _id=external_control_employee.id,
                number=external_control_employee.number,
                short_name=external_control_employee.short_name,
                full_name=external_control_employee.full_name,
                provider_id=external_control_employee.provider.id,
            )
            employee.external_control = external_control
        return employee

    @staticmethod
    async def gateway(token: str = Header(alias="Authorization")):
        """
        Функция для аутентификации обращения через шлюз

        Args:
            token (str, optional): Токен авторизации. Defaults to None.

        Raises:
            HTTPException: При неуспешной авторизации
        """

        if token != settings.SECURITY_TOKEN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have authorization",
            )

    @staticmethod
    async def _parse_token(auth_token: str | None) -> AuthPayload:
        if auth_token is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Auth token was not passed in the request",
            )
        try:
            payload: dict = decode(
                jwt=auth_token,
                key=settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
        except InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid authorization token",
            ) from e
        try:
            payload.setdefault("username", payload.get("profile"))
            auth_payload = AuthPayload.model_validate(payload)
        except pydantic_core.ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid authorization token payload",
            ) from e
        return auth_payload


# Зависимости для авторизации
TenantDep = Annotated[TenantC300, Depends(Auth.tenant)]
EmployeeDep = Annotated[EmployeeC300, Depends(Auth.employee)]
GatewayDep = Annotated[EmployeeC300, Depends(Auth.gateway)]
