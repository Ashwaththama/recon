import io
import pandas as pd
from fastapi import HTTPException, UploadFile

EMPLOYEE_ID_ALIASES = {"employee_id", "emp_id", "employee id", "employeeid", "empid"}


MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


async def read_upload(upload_file: UploadFile) -> pd.DataFrame:
    raw = await upload_file.read()

    if len(raw) > MAX_FILE_SIZE:
        size_mb = len(raw) / (1024 * 1024)
        raise HTTPException(
            status_code=413,
            detail=(
                f"'{upload_file.filename}' is {size_mb:.1f} MB, which exceeds the 10 MB limit. "
                "Please reduce the file size and try again."
            ),
        )

    buffer = io.BytesIO(raw)

    filename = (upload_file.filename or "").lower()
    if filename.endswith(".csv"):
        df = pd.read_csv(buffer)
    elif filename.endswith((".xlsx", ".xls")):
        df = pd.read_excel(buffer, engine="openpyxl")
    else:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported file format for '{upload_file.filename}'. Please upload a .csv or .xlsx file.",
        )

    df.columns = df.columns.str.strip()

    id_col = None
    for col in df.columns:
        if col.strip().lower().replace(" ", "_") in EMPLOYEE_ID_ALIASES or col.strip().lower() in EMPLOYEE_ID_ALIASES:
            id_col = col
            break

    if id_col is None:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Could not find an Employee ID column in '{upload_file.filename}'. "
                "Expected a column named 'Employee_ID', 'Emp_ID', or similar."
            ),
        )

    df = df.rename(columns={id_col: "Employee_ID"})
    df["Employee_ID"] = df["Employee_ID"].astype(str).str.strip()

    return df
