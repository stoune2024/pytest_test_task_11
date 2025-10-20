import re
from pydantic import (
    BaseModel,
    Field,
    EmailStr,
    field_validator,
    ConfigDict,
)
from pydantic.alias_generators import to_camel

unique_user_ids_list = []


class UserPublic(BaseModel):
    id: int | None = Field(
        default=None,
        title="Уникальный идентификатор пользователя",
        description="Позволяет упорядочить пользователей",
    )
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
        title="Имя пользователя",
        description="Имя пользователя",
    )
    age: int | None = Field(
        default=None, gt=0, title="Возраст", description="Возраст пользователя"
    )
    is_supervisor: bool | None = Field(
        default=None,
        title="Является ли админом",
        description="Проверка на суперпользователя",
    )
    email: EmailStr | None = Field(
        default=None, title="Электронная почта", description="Электронная почта"
    )
    phone_number: str | None = Field(
        default=None, title="Номер телефона", description="Номер телефона"
    )

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: str) -> str:
        if not re.match(r"^\+\d{1} \(\d{3}\) \d{3}-\d{2}-\d{2}$", value):
            raise ValueError(
                "Номер телефона должен соответствовать формату: +7 (000) 000-00-00"
            )
        return value


class User(UserPublic):
    username: str = Field(
        title="Никнейм пользователя",
        description="Используется Oauth",
    )
    hashed_password: str = Field(
        title="Хеш пользовательского пароля",
        description="Нужен для Oauth. Хранится в БД",
    )


class UserCreate(UserPublic):
    username: str = Field(
        title="Никнейм пользователя",
        description="Используется Oauth",
    )
    password: str = Field(
        title="Пароль пользователя",
        description="Используется Oauth",
    )


class UserUpdate(UserPublic):
    username: str | None = None
    password: str | None = None
