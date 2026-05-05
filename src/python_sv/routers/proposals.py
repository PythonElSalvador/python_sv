from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from pydantic import EmailStr

from python_sv.dependencies import templates
from python_sv.notifications import notify_proposal

logger = logging.getLogger("pythonsv")

router = APIRouter(prefix="/api")


@router.post("/proposal", response_class=HTMLResponse)
async def proposal(
    request: Request,
    name: str = Form(),
    email: EmailStr = Form(),
    topic: str = Form(),
    description: str = Form(),
    level: str = Form(),
) -> HTMLResponse:
    db = request.app.state.db

    if db is None:
        return templates.TemplateResponse(
            request=request,
            name="partials/signup_error.html",
            context={"message": "Las propuestas no están disponibles en este momento."},
            status_code=503,
        )

    doc = {
        "name": name,
        "email": email,
        "topic": topic,
        "description": description,
        "level": level,
        "created_at": datetime.now(timezone.utc),
    }

    try:
        await db.proposals.insert_one(doc)
    except Exception:
        logger.exception("Proposal insert failed")
        return templates.TemplateResponse(
            request=request,
            name="partials/signup_error.html",
            context={"message": "Algo salió mal. Intenta de nuevo."},
            status_code=500,
        )

    try:
        notify_proposal(
            name=name,
            email=email,
            topic=topic,
            description=description,
            level=level,
        )
    except Exception:
        logger.exception("Proposal notification failed (non-fatal)")

    return templates.TemplateResponse(
        request=request,
        name="partials/proposal_success.html",
        context={"name": name},
    )
