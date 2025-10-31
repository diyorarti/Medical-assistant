from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import home, health, generate, chat_comletion
from api.core.config import settings

def create_app() -> FastAPI:
    app = FastAPI(title=settings.API_NAME, version=settings.API_VERSION)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(home.router)
    app.include_router(health.router)
    app.include_router(generate.router)
    app.include_router(chat_comletion.router)

    return app

app = create_app()
