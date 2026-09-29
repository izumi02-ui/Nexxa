import pytest
from pydantic import ValidationError

from app.validation.common import NEXXABaseModel


class TestModel(NEXXABaseModel):
    name: str


def test_validation_strips_whitespace() -> None:
    model = TestModel(name="  NEXXA  ")

    assert model.name == "NEXXA"


def test_validation_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError):
        TestModel(
            name="NEXXA",
            unexpected="value",
        )