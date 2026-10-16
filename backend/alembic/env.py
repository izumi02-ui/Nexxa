from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.config import get_settings
from app.database.base import Base

# Register every SQLAlchemy model before Alembic inspects metadata.
from app.auth.models import User
from app.music.album_models import Album
from app.music.artist_models import Artist
from app.music.artist_provider_models import ArtistProviderProfile
from app.music.favorite_models import Favorite
from app.music.history_models import HistoryEntry
from app.music.models import Track
from app.music.playback_models import PlaybackState
from app.music.playlist_models import Playlist, PlaylistTrack
from app.music.queue_models import Queue
from app.music.spotify_artist_stats_models import SpotifyArtistStats


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

settings = get_settings()

config.set_main_option(
    "sqlalchemy.url",
    settings.database_url.replace("%", "%%"),
)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Generate migration SQL without opening a database connection."""
    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations using a live database connection."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()