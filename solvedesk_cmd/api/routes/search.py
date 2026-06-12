from solvedesk_cmd.api.requests.search_request import SearchRequest
from fastapi import APIRouter, Depends, HTTPException
from solvedesk_cmd.api.responses.solution_response import SolutionResponse
from solvedesk_cmd.api.dependencies import get_current_token
from solvedesk_cmd.application.dependencies import get_search_service

router = APIRouter()

@router.post("/search")
async def search_solutions(
        request: SearchRequest,
        service = Depends(get_search_service),
        token: str = Depends(get_current_token)):
    
    try:
        results = service.search(request.query, request.top_k)
        res = SolutionResponse.retrieve_solutions(request.query, results)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    