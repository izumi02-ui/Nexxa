from pydantic import BaseModel, ConfigDict


class RecommendationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    artist_id: int | None = None
    album_id: int | None = None
