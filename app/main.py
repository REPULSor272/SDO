from uvicorn import run
from fastapi import FastAPI
from app.config.config import init_config
from fastapi.middleware.cors import CORSMiddleware
from app.middleware.auth import auth_middleware
from app.routers import router as app_router

app = FastAPI(title="SDO API", description="API for SDO", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def main():
    app.include_router(app_router)
    app.middleware("http")(auth_middleware)

    cfg = init_config()

    run(app, host=cfg['app']['host'], port=cfg['app']['port'])

if __name__ == '__main__':
    main()