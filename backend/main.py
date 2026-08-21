"""
main.py — FastAPI application entrypoint
"""
from __future__ import annotations

import os
import sys

# Make sure local packages are importable regardless of CWD
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from api.routes import router

app = FastAPI(
    title="CAP College Preference Advisor",
    description=(
        "ML-powered platform that predicts MHT-CET CAP round cutoffs and generates "
        "a correctly ordered college preference list (Reach → Match → Safe) for students."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — allow React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/", include_in_schema=False)
def root():
    return JSONResponse({"message": "CAP Preference Advisor API", "docs": "/docs"})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
