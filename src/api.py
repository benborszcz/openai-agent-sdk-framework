from fastapi import FastAPI
from src.routes.agent_routes import router as agent_router

app = FastAPI()

app.include_router(agent_router, prefix="/agent")


@app.get("/")
async def root():
    return {"message": "Template Agentic Framework v0.0.1-alpha"}