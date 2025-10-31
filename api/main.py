from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import health


def create_app():

    app = FastAPI(title="Medical-LLM", version="0.1.0")
    
    # cors 
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    # routers 
    app.include_router(health.router)

    return app

app = create_app()