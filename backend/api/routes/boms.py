import io

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from core.database import get_db
from schemas import BOMCreate, BOMItemCreate
from services import bom_service
from services.export_service import export_csv_bytes, export_excel_buffer
from utils.serializers import bom_to_dict, item_to_dict


router = APIRouter(prefix="/boms", tags=["boms"])


@router.post("")
def create_bom(payload: BOMCreate, db: Session = Depends(get_db)):
    return bom_to_dict(bom_service.create_bom(db, payload.name))


@router.get("")
def list_boms(db: Session = Depends(get_db)):
    return [bom_to_dict(bom) for bom in bom_service.list_boms(db)]


@router.get("/{bom_id}")
def get_bom(bom_id: int, db: Session = Depends(get_db)):
    return bom_to_dict(bom_service.get_bom(db, bom_id), include_items=True)


@router.delete("/{bom_id}")
def delete_bom(bom_id: int, db: Session = Depends(get_db)):
    bom_service.delete_bom(db, bom_id)
    return {"message": "BOM deleted"}


@router.post("/{bom_id}/items")
def add_bom_item(bom_id: int, payload: BOMItemCreate, db: Session = Depends(get_db)):
    return item_to_dict(bom_service.add_bom_item(db, bom_id, payload))


@router.get("/{bom_id}/items")
def get_bom_items(bom_id: int, db: Session = Depends(get_db)):
    return [item_to_dict(item) for item in bom_service.list_bom_items(db, bom_id)]


@router.delete("/{bom_id}/items/{item_id}")
def delete_bom_item(bom_id: int, item_id: int, db: Session = Depends(get_db)):
    bom_service.delete_bom_item(db, bom_id, item_id)
    return {"message": "Item deleted"}


@router.post("/{bom_id}/import")
async def import_bom_items(bom_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    bom, missing_items = bom_service.import_bom_items(db, bom_id, await file.read(), file.filename)
    return {
        "bom": bom_to_dict(bom, include_items=True),
        "missing_items": missing_items,
    }


@router.get("/{bom_id}/export/csv")
def export_bom_csv(bom_id: int, db: Session = Depends(get_db)):
    bom = bom_service.get_bom(db, bom_id)
    return StreamingResponse(
        io.BytesIO(export_csv_bytes(bom)),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="bom-{bom.id}.csv"'},
    )


@router.get("/{bom_id}/export/excel")
def export_bom_excel(bom_id: int, db: Session = Depends(get_db)):
    bom = bom_service.get_bom(db, bom_id)
    return StreamingResponse(
        export_excel_buffer(bom),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="bom-{bom.id}.xlsx"'},
    )
