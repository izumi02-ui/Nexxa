from fastapi import APIRouter, Query, Request

from app.search.service import SearchService
from app.search.types import SearchQuery
from app.validation.common import NEXXABaseModel


router = APIRouter()


class SearchResponseTrack(NEXXABaseModel):
    provider: str
    external_id: str
    title: str
    artist_name: str
    album_name: str | None
    duration_ms: int | None
    external_url: str | None


class SearchResponse(NEXXABaseModel):
    tracks: list[SearchResponseTrack]
    total: int
    offset: int
    limit: int


@router.get(
    "/search",
    response_model=SearchResponse,
)
async def search(
    request: Request,
    query: str = Query(
        min_length=1,
        max_length=500,
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=50,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
) -> SearchResponse:
    search_query = SearchQuery(
        query=query,
        limit=limit,
        offset=offset,
    )

    registry = request.app.state.provider_registry

    service = SearchService(registry)

    result = await service.search_tracks(
        search_query,
    )

    return SearchResponse(
        tracks=[
            SearchResponseTrack(
                provider=track.provider.value,
                external_id=track.external_id,
                title=track.title,
                artist_name=track.artist_name,
                album_name=track.album_name,
                duration_ms=track.duration_ms,
                external_url=track.external_url,
            )
            for track in result.tracks
        ],
        total=result.total,
        offset=result.offset,
        limit=result.limit,
    )
