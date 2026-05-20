from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.error_handlers import register_exception_handlers
from app.api.v1 import admin, auth, conversations, order, review, services, transaction, users, ws

app = FastAPI(title="Markethub API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
register_exception_handlers(app)
app.include_router(users.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")

app.include_router(services.router, prefix="/api/v1")

app.include_router(order.router, prefix="/api/v1")

app.include_router(transaction.router, prefix="/api/v1")

app.include_router(review.router, prefix="/api/v1")

app.include_router(admin.router, prefix="/api/v1")

app.include_router(conversations.router, prefix="/api/v1")

app.include_router(ws.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to Markethub API"}


@app.get("/api/v1/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)