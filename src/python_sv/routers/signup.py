from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from pydantic import EmailStr

from python_sv.config import get_settings
from python_sv.dependencies import templates
from python_sv.notifications import notify_signup

logger = logging.getLogger("pythonsv")

router = APIRouter(prefix="/api")


@router.post("/signup", response_class=HTMLResponse)
async def signup(
    request: Request,
    name: str = Form(),
    email: EmailStr = Form(),
    city: str = Form(),
    member_type: str = Form(),
    role: str = Form(),
) -> HTMLResponse:
    settings = get_settings()
    db = request.app.state.db

    if db is None:
        return templates.TemplateResponse(
            request=request,
            name="partials/signup_error.html",
            context={"message": "El registro no está disponible en este momento."},
            status_code=503,
        )

    doc = {
        "name": name,
        "email": email,
        "city": city,
        "member_type": member_type,
        "role": role,
        "created_at": datetime.now(timezone.utc),
    }

    try:
        await db.signups.insert_one(doc)
    except Exception as exc:
        if "duplicate key" in str(exc).lower() or "E11000" in str(exc):
            return templates.TemplateResponse(
                request=request,
                name="partials/signup_exists.html",
                context={"whatsapp_url": settings.whatsapp_url},
            )
        logger.exception("Signup insert failed")
        return templates.TemplateResponse(
            request=request,
            name="partials/signup_error.html",
            context={"message": "Algo salió mal. Intenta de nuevo."},
            status_code=500,
        )

    try:
        notify_signup(
            name=name,
            email=email,
            city=city,
            member_type=member_type,
            role=role,
        )
    except Exception:
        logger.exception("Signup notification failed (non-fatal)")

    return templates.TemplateResponse(
        request=request,
        name="partials/signup_success.html",
        context={"name": name, "whatsapp_url": settings.whatsapp_url},
    )
