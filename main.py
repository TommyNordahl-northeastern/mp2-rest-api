import io
import json
import logging
from pathlib import Path
import pandas as pd
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from src import DatasetInfo, DatasetStorage, HealthResponse, setup_logging

setup_logging(verbose=True)
logger = logging.getLogger(__name__)

app = FastAPI(title="Data Processing API", version="1.0.0")
storage = DatasetStorage()

@app.get("/health", response_model=HealthResponse)
def health_check():
    """Return the application status and version."""
    return {"status": "ok", "version": "1.0.0"}

@app.post("/upload", response_model=DatasetInfo)
async def upload_dataset(file: UploadFile = File(...)):
    """Read and store a CSV upload."""
    if Path(file.filename or "").suffix.lower() != ".csv" or not file.filename:
        logger.warning(f"Bad file type: {Path(file.filename or "").suffix.lower()}")
        raise HTTPException(status_code=400, detail="wrong filename extension/ file type")
    contents = await file.read()

    try:
        df = pd.read_csv(io.BytesIO(contents))
    except(pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError) as error:
        logger.warning(f"Cannot read CSV: {error}")
        raise HTTPException(status_code=400, detail="Cannot read the uploaded csv")

    # Save the DataFrame and return its metadata as DatasetInfo
    storage.save(df, filename=file.filename)
    logger.info(f"Dataset uploaded with ID: {storage._counter}, filename: {file.filename}, and {len(df)} rows.")
    return DatasetInfo(id=storage._counter, filename=file.filename, rows=len(df),
                       columns = len(df.columns), column_names= df.columns.to_list())

@app.get("/datasets/{dataset_id}")
def get_dataset(dataset_id: int, limit: int = Query(default=100, ge=1)):
    """Return up to limit rows from a stored dataset."""
    if dataset_id not in storage._store:
        logger.warning(f"ID {dataset_id} not found in storage.")
        raise HTTPException(status_code=404, detail="Dataset not found")

    df = storage._store[dataset_id][0].copy()
    records = json.loads(df.head(limit).to_json(orient="records"))
    dataset_values = {"id": dataset_id, "data": records, "total_rows": len(df)}
    logger.info(f"Dataset located with ID {dataset_id} and row count {len(df)}")
    return dataset_values

