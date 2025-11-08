from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.v1.router import api_router
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME, version=settings.API_VERSION)

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount static directories
    app.mount("/books", StaticFiles(directory="books"), name="books")
    app.mount("/thumbnails", StaticFiles(directory="thumbnails"), name="thumbnails")

    # Include API routers
    app.include_router(api_router, prefix=f"/api/{settings.API_VERSION}")

    @app.get("/")
    def root():
        return {"message": "Bookshelf Backend is Running!"}

    return app


app = create_app()