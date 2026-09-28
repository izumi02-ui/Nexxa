from fastapi import FastAPI

app = FastAPI(
    title="NEXXA API",
    description="Backend API for NEXXA, a cross-platform music application.",
    version="0.1.0",
)


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "name": "NEXXA API",
        "version": "0.1.0",
    }