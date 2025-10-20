import pytest
from apps.user.repository import UsersStore
from apps.user.schemas import UserPublic, User, UserCreate
from apps.user.services import AsyncDatabaseConnection
from apps.auth.schemas import Token, TokenData
from apps.auth.services import (
    CryptContext,
    OAuth2PasswordBearerWithCookie,
    verify_password,
)
from pydantic import ValidationError


def test_users_store_success():
    users_store = UsersStore()
    assert users_store is not None


def test_users_store_singletone_success():
    users_store = UsersStore()
    users_store_2 = UsersStore()
    assert users_store is users_store_2


def test_users_store_enter_data_success():
    users_store_instance = UsersStore()
    users_store_instance({"id": 1, "name": "Alex"})
    users_store_instance({"id": 2, "name": "Sam"})
    list_of_users = users_store_instance.users_store
    assert list_of_users[0]["id"] == 1
    assert list_of_users[1]["id"] == 2


def test_user_public_instance_success():
    user = UserPublic(
        id=1,
        name="John",
        age=35,
        is_supervisor=True,
        email="johndoe@mail.com",
        phone_number="+8 (800) 555-35-35",
    )
    assert user.age == 35
    assert user.is_supervisor


def test_user_public_instance_wrong_email():
    with pytest.raises(ValidationError):
        UserPublic(
            id=1,
            name="John",
            age=35,
            is_supervisor=True,
            email="johndoemail.com",
            phone_number="+8 (800) 555-35-35",
        )


def test_user_public_instance_wrong_name_length():
    with pytest.raises(ValidationError):
        UserPublic(
            id=1,
            name="",
            age=35,
            is_supervisor=True,
            email="johndo@email.com",
            phone_number="+8 (800) 555-35-35",
        )


def test_user_public_instance_wrong_age():
    with pytest.raises(ValidationError):
        UserPublic(
            id=1,
            name="John",
            age=0,
            is_supervisor=True,
            email="johndo@email.com",
            phone_number="+8 (800) 555-35-35",
        )


def test_user_public_instance_wrong_type_is_supervisor():
    with pytest.raises(ValidationError):
        UserPublic(
            id=1,
            name="John",
            age=0,
            is_supervisor=123,
            email="johndo@email.com",
            phone_number="+8 (800) 555-35-35",
        )


def test_user_public_instance_wrong_phone_number():
    with pytest.raises(ValidationError):
        UserPublic(
            id=1,
            name="John",
            age=0,
            is_supervisor=True,
            email="johndo@email.com",
            phone_number="+8 (800)-555-35-35",
        )


def test_user_instance_success(user_public):
    user = User(**user_public, username="johndoe", hashed_password="qwe123")
    assert user.username == "johndoe"
    assert user.hashed_password == "qwe123"


def test_user_create_instance_success(user_public):
    user = UserCreate(**user_public, username="johndoe", password="qwe123")
    assert user.username == "johndoe"
    assert user.password == "qwe123"


def test_async_database_connection():
    connection = AsyncDatabaseConnection(db_url="some_url")
    assert connection.db_url == "some_url"


def test_token_instance_success():
    token = Token(access_token="johndoe", token_type="bearer")
    assert token.access_token == "johndoe"
    assert token.token_type == "bearer"


def test_token_data_instance_success():
    token = TokenData(username="johndoe")
    assert token.username == "johndoe"


def test_cryptcontext_instance_success():
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    assert pwd_context.schemes() == ("bcrypt",)


def test_oauth2passwordbearer_instance_success():
    oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="token")
    assert oauth2_scheme is not None
    assert oauth2_scheme.__dict__["model"].flows.password.tokenUrl == "token"


def test_verify_password_success(mocker):
    mocker.patch("apps.auth.services.CryptContext.verify", return_value=True)
    result = verify_password("password", "hashed_password")
    assert result
