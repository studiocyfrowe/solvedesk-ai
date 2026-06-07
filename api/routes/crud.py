from fastapi import APIRouter, Depends, HTTPException
from api.dependencies import get_current_token, get_manage_data_service
from api.requests.issue_request import IssueRequest

router = APIRouter()
    
@router.get("/get-issue/{issue_id}")
async def get_issue(issue_id: int, 
                    service = Depends(get_manage_data_service),
                    token: str = Depends(get_current_token)):
    try:
        result = service.get_single_issue(issue_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---
    
@router.post("/add-issue")
async def save_issue(request: IssueRequest, 
                    service = Depends(get_manage_data_service),
                    token: str = Depends(get_current_token)):
    try:
        service.store_new_item(request)
        return {
            "status": "Rozwiązanie zostało zapisane do bazy wektorowej",
            "issue": request.issueName
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# ---
    
@router.put("/update-issue/{issue_id}")
async def update_issue(issue_id: int,
                    request: IssueRequest, 
                    service = Depends(get_manage_data_service),
                    token: str = Depends(get_current_token)):
    try:
        service.update_single_issue(issue_id, request)
        return {
            "status": "Rozwiązanie zostało zapisane do bazy wektorowej",
            "issue": request.issueName
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# ---
    
@router.delete("/delete-issue/{issue_id}")
async def delete_issue(issue_id: int, 
                    service = Depends(get_manage_data_service),
                    token: str = Depends(get_current_token)):
    try:
        service.delete_single_issue(issue_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))