import requests
import time
from dotenv import load_dotenv
import os

from solvedesk_cmd.api.requests.search_request import SearchRequest
from fastapi import APIRouter, Depends, HTTPException
from solvedesk_cmd.api.responses.solution_response import SolutionResponse
from solvedesk_cmd.api.dependencies import get_current_token
from solvedesk_cmd.application.dependencies import get_search_service


load_dotenv()

router = APIRouter()

URL = os.getenv("LLM_URL")
MODEL = os.getenv("LLM_MODEL")

@router.post("/explain")
async def explain_solutions(
        request: SearchRequest,
        service = Depends(get_search_service),
        token: str = Depends(get_current_token)):

    try:
        results = service.search(request.query, request.top_k)
        res = SolutionResponse.retrieve_solutions(request.query, results)

        context = "\n\n".join(
            f"""Rozwiązanie {i+1}
                Problem: {r['issue_sympthoms']}
                Rozwiązanie: {r['issue_solution']}"""
            for i, r in enumerate(res["solutions"])
        )

        prompt = f"""
            You are an IT helpdesk assistant.

            Use ONLY the context to answer.
            If no solution: "No solution in the SolveDesk database."

            CONTEXT:
            {context}

            QUESTION:
            {request.query}

            ANSWER:
        """

        start = time.perf_counter()
        response = requests.post(
            URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": 360,
                    "temperature": 0.3
                }
            },
            timeout=240
        )
        end = time.perf_counter()
        elapsed = round(end - start, 2)

        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="LLM error")

        answer = response.json()["response"]

        return {
            "answer": answer,
            "response_time": elapsed
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    