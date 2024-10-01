import pytest


@pytest.fixture
def password():
    return '1234567'


@pytest.fixture
def user(django_user_model, password):
    return django_user_model.objects.create_user(
        email='test@mail.ru',
        username='TestUser',
        first_name='TestFirstName',
        last_name='TestLastName',
        password=password,
    )


@pytest.fixture
def another_user(django_user_model, password):
    return django_user_model.objects.create_user(
        email='another_user@mail.ru',
        username='AnotherTestUser',
        first_name='TestFirstName',
        last_name='TestLastName',
        password=password,
    )


@pytest.fixture
def admin(django_user_model, password):
    return django_user_model.objects.create_user(
        email='admin@mail.ru',
        username='Admin',
        first_name='AdminFirstName',
        last_name='AdminLastName',
        password=password,
        is_staff=True
    )


@pytest.fixture
def token(user):
    from rest_framework.authtoken.models import Token
    token, _ = Token.objects.get_or_create(user=user)
    return token.key


@pytest.fixture
def another_token(another_user):
    from rest_framework.authtoken.models import Token
    token, _ = Token.objects.get_or_create(user=another_user)
    return token.key


@pytest.fixture
def admin_token(admin):
    from rest_framework.authtoken.models import Token
    token, _ = Token.objects.get_or_create(user=admin)
    return token.key


@pytest.fixture
def user_client(token):
    from rest_framework.test import APIClient

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
    return client


@pytest.fixture
def another_user_client(another_token):
    from rest_framework.test import APIClient

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Token {another_token}')
    return client


@pytest.fixture
def admin_user_client(admin_token):
    from rest_framework.test import APIClient

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Token {admin_token}')
    return client
