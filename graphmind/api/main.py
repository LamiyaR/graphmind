from fastapi import FastAPI

from graphmind.api.routes import router


app = FastAPI(
    title="GraphMind API",
    description="Biomedical Question Answering using GraphRAG",
    version="1.0.0"
)

app.include_router(router)


@app.get("/")
def home():
    return {
        "message": "GraphMind API is running"
    }