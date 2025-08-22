from fastapi import FastAPI
from app.core.database import Base, engine
from app.api.routes import bets, health

def create_app() -> FastAPI:
    app = FastAPI(title="Pulsr Backend", version="0.1.0")
    # Create DB tables if not present (use Alembic later)
    Base.metadata.create_all(bind=engine)

    app.include_router(health.router)
    app.include_router(bets.router)

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True, reload_use_polling=True)
