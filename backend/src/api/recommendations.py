"""HTTP boundary for the server-side OpenAI recommendation workflow."""

from __future__ import annotations

import os
from dataclasses import asdict
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.models.recommand_agent import AgentsSdkUnavailableError, run_recommend_agent_with_openai_agents
from src.services.recommendation_service import (
    ProgrammeNotFoundError,
    agent_inputs_from_transcript,
    load_school_catalogue,
    select_programmes,
)


class ProgrammeSelector(BaseModel):
    school: str
    program: str


class RecommendationRequest(BaseModel):
    transcript: dict[str, Any]
    programmes: list[ProgrammeSelector] = Field(min_length=1, max_length=12)


app = FastAPI(title="UniCompass recommendation API", version="v1")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        os.environ.get("UNICOMPASS_FRONTEND_ORIGIN", "http://localhost:3000"),
        "http://127.0.0.1:3000",
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/recommendations")
def recommend(request: RecommendationRequest) -> dict[str, Any]:
    if not os.environ.get("OPENAI_API_KEY"):
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY is not configured on the backend.")

    try:
        schools = select_programmes(
            load_school_catalogue(), [selector.model_dump() for selector in request.programmes]
        )
        grades, subjects, preferences = agent_inputs_from_transcript(request.transcript)
        result = run_recommend_agent_with_openai_agents(grades, subjects, preferences, schools)
        return asdict(result)
    except AgentsSdkUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ProgrammeNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=f"Invalid recommendation request: {exc}") from exc
