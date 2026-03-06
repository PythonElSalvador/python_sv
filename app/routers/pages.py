from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Form, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from pydantic import ValidationError
from pymongo.errors import DuplicateKeyError

from app.config import Settings, get_settings
import app.dependencies as deps
from app.dependencies import (
    SignupForm,
    check_rate_limit,
    new_csrf_token,
    page_content,
    templates,
    verify_csrf_token,
)
from app.notifications import notify_signup

logger = logging.getLogger("pythonsv")

router = APIRouter()


@router.get("/health")
async def health():
    try:
        await deps.db.command("ping")
        return {"status": "ok"}
    except Exception:
        return {"status": "degraded", "reason": "database unavailable"}


@router.get("/robots.txt", response_class=PlainTextResponse)
async def robots_txt(settings: Annotated[Settings, Depends(get_settings)]):
    return f"User-agent: *\nAllow: /\nSitemap: {settings.base_url}/sitemap.xml\n"


@router.get("/sitemap.xml", response_class=PlainTextResponse)
async def sitemap_xml(settings: Annotated[Settings, Depends(get_settings)]):
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        "  <url>\n"
        f"    <loc>{settings.base_url}/</loc>\n"
        "  </url>\n"
        "  <url>\n"
        f"    <loc>{settings.base_url}/codigo-de-conducta</loc>\n"
        "  </url>\n"
        "</urlset>\n"
    )


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": page_content["title"],
            "body": page_content["body"],
            "csrf_token": new_csrf_token(),
        },
    )


@router.get("/codigo-de-conducta", response_class=HTMLResponse)
async def code_of_conduct(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="codigo-de-conducta.html",
    )


@router.post("/signups", response_class=HTMLResponse)
async def signup(
    request: Request,
    background_tasks: BackgroundTasks,
    name: str = Form(),
    email: str = Form(),
    city: str = Form(),
    role: str = Form(),
    other_city: str = Form(""),
    csrf_token: str = Form(""),
):
    if not verify_csrf_token(csrf_token):
        return templates.TemplateResponse(
            request=request,
            name="partials/signup_error.html",
            context={"message": "Session expired. Reload the page and try again."},
        )

    try:
        form = SignupForm(
            name=name,
            email=email,
            city=city,
            role=role,
            other_city=other_city,
            csrf_token=csrf_token,
        )
    except ValidationError:
        return templates.TemplateResponse(
            request=request,
            name="partials/signup_error.html",
            context={"message": "Invalid email. Please check and try again."},
        )

    ip = request.client.host if request.client else "unknown"
    if not check_rate_limit(ip):
        return templates.TemplateResponse(
            request=request,
            name="partials/signup_error.html",
            context={"message": "Too many attempts. Please wait a few minutes."},
        )

    if form.city == "Other" and not form.other_city.strip():
        return templates.TemplateResponse(
            request=request,
            name="partials/signup_error.html",
            context={"message": "Please specify your city."},
        )

    doc = {
        "name": form.name.strip(),
        "email": form.email,
        "city": form.other_city.strip() if form.city == "Other" else form.city.strip(),
        "role": form.role.strip(),
        "created_at": datetime.now(timezone.utc),
    }

    try:
        await deps.db.signups.insert_one(doc)
    except DuplicateKeyError:
        return templates.TemplateResponse(
            request=request,
            name="partials/signup_exists.html",
        )

    logger.info("New signup from %s", doc["city"])
    background_tasks.add_task(
        notify_signup, doc["name"], doc["email"], doc["city"], doc["role"]
    )
    return templates.TemplateResponse(
        request=request,
        name="partials/signup_success.html",
        context={
            "name": doc["name"],
        },
    )
