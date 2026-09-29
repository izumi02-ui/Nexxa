from dataclasses import dataclass

import pytest

from app.providers.types import ProviderName
from app.providers.youtube.provider import YouTubeProvider


@dataclass
class FakeYouTubeVideo:
    video_id: str
    title: str
    channel_name: str
    description: str
    thumbnail_url: str | None
    duration: str | None
    url: str


class FakeYouTubeClient:
    def __init__(
        self,
        videos: list[FakeYouTubeVideo] | None = None,
        next_page_token: str | None = None,
        pages: dict[str | None, tuple[list[FakeYouTubeVideo], str | None]]
        | None = None,
        track: FakeYouTubeVideo | None = None,
    ) -> None:
        self.videos = videos or []
        self.next_page_token = next_page_token
        self.pages = pages or {}
        self.track = track
        self.search_calls: list[tuple[str, int, str | None]] = []

    async def search_videos(
        self,
        query: str,
        limit: int = 10,
        page_token: str | None = None,
    ) -> tuple[list[FakeYouTubeVideo], str | None]:
        self.search_calls.append((query, limit, page_token))

        if page_token in self.pages:
            return self.pages[page_token]

        return self.videos, self.next_page_token

    async def get_video(
        self,
        external_id: str,
    ) -> FakeYouTubeVideo | None:
        if self.track is None:
            return None

        if self.track.video_id != external_id:
            return None

        return self.track


def make_video(
    video_id: str,
    title: str = "Test Song",
    channel_name: str = "Test Artist",
    duration: str | None = "PT3M30S",
    thumbnail_url: str | None = "https://example.com/thumb.jpg",
) -> FakeYouTubeVideo:
    return FakeYouTubeVideo(
        video_id=video_id,
        title=title,
        channel_name=channel_name,
        description="Test description",
        thumbnail_url=thumbnail_url,
        duration=duration,
        url=f"https://www.youtube.com/watch?v={video_id}",
    )


def test_provider_name() -> None:
    provider = YouTubeProvider(FakeYouTubeClient())

    assert provider.name == ProviderName.YOUTUBE


@pytest.mark.asyncio
async def test_search_tracks_normalizes_metadata() -> None:
    video = make_video("abc123")

    provider = YouTubeProvider(
        FakeYouTubeClient(videos=[video]),
    )

    tracks = await provider.search_tracks("test song", limit=10)

    assert len(tracks) == 1

    track = tracks[0]

    assert track.provider == ProviderName.YOUTUBE
    assert track.external_id == "abc123"
    assert track.title == "Test Song"
    assert track.artist_name == "Test Artist"
    assert track.album_name is None
    assert track.duration_ms is None
    assert track.artwork_url == "https://example.com/thumb.jpg"
    assert track.external_url == "https://www.youtube.com/watch?v=abc123"


@pytest.mark.asyncio
async def test_search_tracks_follows_pagination() -> None:
    first_page = [make_video("first")]
    second_page = [make_video("second")]

    client = FakeYouTubeClient(
        pages={
            None: (first_page, "page-2"),
            "page-2": (second_page, None),
        },
    )

    provider = YouTubeProvider(client)

    tracks = await provider.search_tracks("test", limit=2)

    assert [track.external_id for track in tracks] == [
        "first",
        "second",
    ]

    assert client.search_calls == [
        ("test", 2, None),
        ("test", 1, "page-2"),
    ]


@pytest.mark.asyncio
async def test_search_tracks_stops_at_requested_limit() -> None:
    first_page = [
        make_video("first"),
        make_video("second"),
    ]

    client = FakeYouTubeClient(
        pages={
            None: (first_page, "page-2"),
        },
    )

    provider = YouTubeProvider(client)

    tracks = await provider.search_tracks("test", limit=1)

    assert len(tracks) == 1
    assert tracks[0].external_id == "first"

    assert client.search_calls == [
        ("test", 1, None),
    ]


@pytest.mark.asyncio
async def test_search_tracks_with_zero_limit() -> None:
    client = FakeYouTubeClient(
        videos=[make_video("abc123")],
    )

    provider = YouTubeProvider(client)

    tracks = await provider.search_tracks("test", limit=0)

    assert tracks == []
    assert client.search_calls == []


@pytest.mark.asyncio
async def test_get_track_normalizes_metadata_and_duration() -> None:
    video = make_video(
        "abc123",
        duration="PT1H2M3S",
    )

    provider = YouTubeProvider(
        FakeYouTubeClient(track=video),
    )

    track = await provider.get_track("abc123")

    assert track is not None
    assert track.provider == ProviderName.YOUTUBE
    assert track.external_id == "abc123"
    assert track.title == "Test Song"
    assert track.artist_name == "Test Artist"
    assert track.duration_ms == 3_723_000
    assert track.artwork_url == "https://example.com/thumb.jpg"
    assert track.external_url == "https://www.youtube.com/watch?v=abc123"


@pytest.mark.asyncio
async def test_get_track_returns_none_for_missing_video() -> None:
    provider = YouTubeProvider(
        FakeYouTubeClient(),
    )

    track = await provider.get_track("missing")

    assert track is None


@pytest.mark.parametrize(
    ("duration", "expected"),
    [
        ("PT3M30S", 210_000),
        ("PT1H2M3S", 3_723_000),
        ("PT45S", 45_000),
        ("PT10M", 600_000),
        (None, None),
        ("", None),
        ("INVALID", None),
        ("PT", 0),
        ("PT3X", None),
    ],
)
def test_duration_to_ms(
    duration: str | None,
    expected: int | None,
) -> None:
    assert YouTubeProvider._duration_to_ms(duration) == expected
