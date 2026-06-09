from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from solvedesk_cmd.api.dependencies import get_data_sync_service
from solvedesk_cmd.domain.enums.import_status import ImportStatus
import os

router = APIRouter()

@router.post("/import")
async def import_data(
    file: UploadFile = File(...),
    service = Depends(get_data_sync_service)
):
    try:
        filename = file.filename
        if not filename:
            raise HTTPException(status_code=400, detail='Brak nazwy pliku')
        
        _, ext = os.path.splitext(filename)
        ext = ext.lower()

        allowed = ['.csv', '.json', '.xlsx']
        if ext not in allowed:
            raise HTTPException(
                status_code=400,
                detail=f"Nieobsługiwany format pliku: {ext}"
            )
        
        content = await file.read()
        
        count = service.sync(content=content, extension=ext)
        return {
            "status" : ImportStatus.LOADED.value,
            "count" : count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sync")
async def sync_data(
    service = Depends(get_data_sync_service)):
    
    try:
        count = service.sync()
        return {
            "status" : "Zaimportowano dane do bazy wektorowej",
            "count" : count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))