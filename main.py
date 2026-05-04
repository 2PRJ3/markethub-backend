from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.error_handlers import register_exception_handlers
from app.api.v1 import auth, services, users

app = FastAPI(title="Markethub API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
register_exception_handlers(app)
app.include_router(users.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")

app.include_router(services.router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {"message": "Welcome to Markethub API"}


@app.get("/health")
def health():
    return {"status": "ok"}
