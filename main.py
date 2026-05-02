from fastapi import FastAPI
from app.api.error_handlers import register_exception_handlers
from app.api.v1 import users


app = FastAPI(
    title="Markethub API"
)
register_exception_handlers(app)
app.include_router(users.router, prefix="/api/v1")
@app.get("/")
def read_root():
    return {"message": "Welcome to Markethub API"}

@app.get("/health")
def health():
    return {"status": "ok"}