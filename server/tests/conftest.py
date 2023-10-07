import pytest
from fixtures import *


@pytest.fixture
def alembic_config() -> dict[str, str]:
    return {'file': 'alembic/alembic.ini'}
