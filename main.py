from fastapi import FastAPI

app = FastAPI(
    title="Markethub API"
)

@app.get("/")
def read_root():
    return {"message": "Welcome to Markethub API"}

@app.get("/health")
def health():
    return {"status": "ok"}