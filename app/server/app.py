from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
from server.routes.factCheck import router as factCheckRouter

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(factCheckRouter, tags=["FactCheck"], prefix="/factCheck")


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to this fantastic app!"}
