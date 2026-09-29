from pydantic import BaseModel, ConfigDict


class NEXXABaseModel(BaseModel):
    """Base model for validated NEXXA API data."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )