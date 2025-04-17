from project.users.models import User
from django.db import transaction


@transaction.atomic
def create_user(
    first_name: str,
    last_name: str,
    password: str,
    username: str,
    key_password: str | None = None,
    patronymic: str | None = None,
    email: str | None = None,
) -> User:
    user = User(
        first_name=first_name,
        last_name=last_name,
        username=username,
        patronymic=patronymic,
        email=email
    )
    user.save()
    user.set_password(password)
    if key_password:
        user.generate_keys(key_password)
    return user
