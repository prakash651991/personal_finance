import csv
import io
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse

from ..security.auth import get_current_user_id, get_user_client

router = APIRouter(tags=["imports-exports"])


@router.get("/exports/transactions")
def export_transactions(user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    rows = client.table("transactions").select("*").eq("user_id", user_id).order("transaction_date", desc=True).execute().data or []
    buf = io.StringIO()
    if rows:
        writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    buf.seek(0)
    return StreamingResponse(iter([buf.getvalue()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=transactions.csv"})


@router.post("/imports/csv")
async def import_csv(file: UploadFile = File(...), user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    content = await file.read()
    text = content.decode("utf-8", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    batch = client.table("import_batches").insert({"user_id": user_id, "source": file.filename or "csv", "row_count": 0, "status": "processing"}).execute().data
    batch_id = (batch or [{}])[0].get("id")
    count = 0
    errors = []
    for i, row in enumerate(reader):
        try:
            payload = {
                "user_id": user_id,
                "transaction_type": row.get("transaction_type") or row.get("type") or "expense",
                "amount": float(row.get("amount") or 0),
                "transaction_date": row.get("transaction_date") or row.get("date"),
                "description": row.get("description") or row.get("merchant"),
                "status": "posted",
            }
            if not payload["transaction_date"] or payload["amount"] <= 0:
                raise ValueError("invalid row")
            client.table("transactions").insert(payload).execute()
            count += 1
        except Exception as ex:
            errors.append({"row": i + 2, "error": str(ex)})
    if batch_id:
        client.table("import_batches").update({"row_count": count, "status": "completed"}).eq("id", batch_id).execute()
    return {"imported": count, "errors": errors, "batch_id": batch_id}
