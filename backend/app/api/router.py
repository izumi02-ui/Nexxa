from fastapi import APIRouter

from app.api.health import router as health_router
from app.api.search import router as search_router
from app.music.favorite_routes import router as favorite_router
from app.music.history_routes import router as history_router
from app.music.playlist_routes import router as playlist_router
from app.music.album_routes import router as album_router


api_router = APIRouter(
    prefix="/api/v1",
)


api_router.include_router(health_router)
api_router.include_router(search_router)
api_router.include_router(album_router)
api_router.include_router(favorite_router)
api_router.include_router(playlist_router)
api_router.include_router(history_router)
