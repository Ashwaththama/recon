import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import reconcile

app = FastAPI(title="HR Payroll Reconciliation API")

allowed_origins = [
    "http://localhost:5173",
    os.environ.get("FRONTEND_URL", ""),
]
allowed_origins = [o for o in allowed_origins if o]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)

app.include_router(reconcile.router, prefix="/api")
