```python
"""
API Ingestion and Risk Scoring Service

This module implements a minimal FastAPI backend with endpoints to ingest KYC documents,
financials, and transactions, and to trigger risk scoring based on ingested data.

Endpoints:
- POST   /api/ingest/kyc          : Upload KYC PDF
- POST   /api/ingest/financials   : Upload financials CSV
- POST   /api/ingest/transactions : Upload transactions JSON
- GET    /api/risk/score/{ingestion_id} : Retrieve risk score

All endpoints return JSON responses and use in-memory storage for demonstration.
"""

import os
import uuid
from typing import Dict, Any, Optional

from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.status import (
    HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_415_UNSUPPORTED_MEDIA_TYPE, HTTP_404_NOT_FOUND
)
import csv
import json

# ------------------------
# In-memory Data Storage
# ------------------------

class IngestionStore:
    """
    Stores ingested file metadata and contents in-memory.
    """
    def __init__(self):
        # ingestion_id: {"type": str, "content": Any}
        self._store: Dict[str, Dict[str, Any]] = {}

    def add(self, ingestion_type: str, content: Any) -> str:
        """
        Add a new ingestion record.

        Args:
            ingestion_type (str): Type of the ingestion ('kyc', 'financials', 'transactions')
            content (Any): The ingested file content or parsed data

        Returns:
            str: The generated ingestion_id
        """
        ingestion_id = uuid.uuid4().hex
        self._store[ingestion_id] = {
            "type": ingestion_type,
            "content": content
        }
        return ingestion_id

    def get(self, ingestion_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve an ingestion record by ID.

        Args:
            ingestion_id (str): The ingestion ID

        Returns:
            Optional[Dict[str, Any]]: The ingestion record or None if not found
        """
        return self._store.get(ingestion_id)

    def exists(self, ingestion_id: str) -> bool:
        """
        Check if an ingestion_id exists.

        Args:
            ingestion_id (str): The ingestion ID

        Returns:
            bool: True if exists, False otherwise
        """
        return ingestion_id in self._store

# Instantiate the store
ingestion_store = IngestionStore()

# ------------------------
# Risk Scoring Function
# ------------------------

def calculate_risk_score(ingestion: Dict[str, Any]) -> int:
    """
    Dummy risk scoring logic based on ingestion type and content.

    Args:
        ingestion (Dict[str, Any]): The ingestion record

    Returns:
        int: A risk score between 1 and 100
    """
    ingestion_type = ingestion["type"]
    if ingestion_type == "kyc":
        # Just a dummy: lower risk for valid PDF
        return 10
    elif ingestion_type == "financials":
        # Dummy: risk based on amount
        content = ingestion["content"]
        try:
            reader = csv.DictReader(content.decode().splitlines())
            amounts = [float(row["amount"]) for row in reader]
            avg_amount = sum(amounts) / len(amounts) if amounts else 0
            return 50 if avg_amount > 500 else 30
        except Exception:
            return 90
    elif ingestion_type == "transactions":
        # Dummy: risk based on number of transactions
        txs = ingestion["content"]
        return min(20 + 2 * len(txs), 100)
    else:
        return 99

# ------------------------
# FastAPI App Initialization
# ------------------------

app = FastAPI(
    title="Ingestion & Risk Scoring API",
    version="1.0.0",
    docs_url="/docs"
)

# Allow CORS for local testing if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = "/api"

# ------------------------
# Helper Functions
# ------------------------

def is_pdf(file: UploadFile) -> bool:
    """
    Check if uploaded file is a PDF by extension and content-type.

    Args:
        file (UploadFile): The uploaded file

    Returns:
        bool: True if PDF, False otherwise
    """
    ext = os.path.splitext(file.filename)[1].lower()
    return (ext == ".pdf") and (file.content_type == "application/pdf")

def is_csv(file: UploadFile) -> bool:
    """
    Check if uploaded file is a CSV by extension and content-type.

    Args:
        file (UploadFile): The uploaded file

    Returns:
        bool: True if CSV, False otherwise
    """
    ext = os.path.splitext(file.filename)[1].lower()
    return (ext == ".csv") and (file.content_type == "text/csv")

def is_json(file: UploadFile) -> bool:
    """
    Check if uploaded file is a JSON by extension and content-type.

    Args:
        file (UploadFile): The uploaded file

    Returns:
        bool: True if JSON, False otherwise
    """
    ext = os.path.splitext(file.filename)[1].lower()
    return (ext == ".json") and (file.content_type == "application/json")

# ------------------------
# API Endpoints
# ------------------------

@app.post(f"{API_PREFIX}/ingest/kyc", status_code=HTTP_201_CREATED)
async def ingest_kyc(file: UploadFile = File(...)):
    """
    Ingest a KYC PDF file.

    Args:
        file (UploadFile): The uploaded PDF file

    Returns:
        JSONResponse: {"ingestion_id": str}
    """
    if not is_pdf(file):
        return JSONResponse(
            status_code=HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            content={"error": "Invalid file type. Only PDF accepted for KYC."}
        )
    try:
        content = await file.read()
        if not content.startswith(b"%PDF"):
            return JSONResponse(
                status_code=HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                content={"error": "Uploaded file is not a valid PDF."}
            )
    except Exception:
        return JSONResponse(
            status_code=HTTP_400_BAD_REQUEST,
            content={"error": "Failed to read uploaded file."}
        )

    ingestion_id = ingestion_store.add("kyc", content)
    return {"ingestion_id": ingestion_id}

@app.post(f"{API_PREFIX}/ingest/financials", status_code=HTTP_201_CREATED)
async def ingest_financials(file: UploadFile = File(...)):
    """
    Ingest a financials CSV file.

    Args:
        file (UploadFile): The uploaded CSV file

    Returns:
        JSONResponse: {"ingestion_id": str}
    """
    if not file:
        return JSONResponse(
            status_code=HTTP_400_BAD_REQUEST,
            content={"error": "No file uploaded."}
        )

    if not is_csv(file):
        return JSONResponse(
            status_code=HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            content={"error": "Invalid file type. Only CSV accepted for financials."}
        )
    try:
        content = await file.read()
        # Validate CSV by trying to parse header
        csv_string = content.decode()
        reader = csv.DictReader(csv_string.splitlines())
        # Check at least header exists
        _ = reader.fieldnames
    except Exception:
        return JSONResponse(
            status_code=HTTP_400_BAD_REQUEST,
            content={"error": "Failed to parse CSV file."}
        )

    ingestion_id = ingestion_store.add("financials", content)
    return {"ingestion_id": ingestion_id}

@app.post(f"{API_PREFIX}/ingest/transactions", status_code=HTTP_201_CREATED)
async def ingest_transactions(file: UploadFile = File(...)):
    """
    Ingest a transactions JSON file.

    Args:
        file (UploadFile): The uploaded JSON file

    Returns:
        JSONResponse: {"ingestion_id": str}
    """
    if not is_json(file):
        return JSONResponse(
            status_code=HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            content={"error": "Invalid file type. Only JSON accepted for transactions."}
        )
    try:
        content = await file.read()
        parsed = json.loads(content.decode())
        if not isinstance(parsed, list):
            raise ValueError("JSON must be a list of transactions")
    except Exception:
        return JSONResponse(
            status_code=HTTP_400_BAD_REQUEST,
            content={"error": "Failed to parse JSON file."}
        )

    ingestion_id = ingestion_store.add("transactions", parsed)
    return {"ingestion_id": ingestion_id}

@app.get(f"{API_PREFIX}/risk/score/{{ingestion_id}}")
async def get_risk_score(ingestion_id: str):
    """
    Retrieve risk score for an ingested file.

    Args:
        ingestion_id (str): The ingestion ID

    Returns:
        JSONResponse: {"risk_score": int}
    """
    ingestion = ingestion_store.get(ingestion_id)
    if not ingestion:
        return JSONResponse(
            status_code=HTTP_404_NOT_FOUND,
            content={"error": "Ingestion ID not found."}
        )

    try:
        risk_score = calculate_risk_score(ingestion)
    except Exception:
        return JSONResponse(
            status_code=HTTP_400_BAD_REQUEST,
            content={"error": "Could not calculate risk score."}
        )
    return {"risk_score": risk_score}

# ------------------------
# Exception Handlers
# ------------------------

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Custom HTTPException handler to return JSON error messages.

    Args:
        request (Request): The request object
        exc (HTTPException): The exception

    Returns:
        JSONResponse
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

# ------------------------
# Example Usage (Run Server)
# ------------------------

# To run the server, save this file as `main.py` and use:
#     uvicorn main:app --reload --host 0.0.0.0 --port 8000
#
# The API will then be accessible at http://localhost:8000/api/
```
