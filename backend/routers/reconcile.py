from fastapi import APIRouter, File, UploadFile
from fastapi.responses import StreamingResponse
from services import file_reader, reconciler, excel_writer

router = APIRouter()


@router.post("/reconcile")
async def reconcile(
    hr_file: UploadFile = File(...),
    payroll_file: UploadFile = File(...),
):
    hr_df = await file_reader.read_upload(hr_file)
    payroll_df = await file_reader.read_upload(payroll_file)

    result = reconciler.run_reconciliation(hr_df, payroll_df)

    output = excel_writer.build_workbook(result)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="reconciliation_report.xlsx"'},
    )
