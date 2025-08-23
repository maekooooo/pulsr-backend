from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, engine
from app.api.routes import bets, health, price


def create_app() -> FastAPI:
    app = FastAPI(title="Pulsr Backend", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Create DB tables if not present (use Alembic later)
    Base.metadata.create_all(bind=engine)

    app.include_router(health.router)
    app.include_router(bets.router)
    app.include_router(price.router)

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True, reload_use_polling=True)
