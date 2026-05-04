from __future__ import annotations

import secrets

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from python_sv.config import get_settings
from python_sv.dependencies import templates

security = HTTPBasic()


def verify_admin(credentials: HTTPBasicCredentials = Depends(security)) -> None:
    settings = get_settings()
    if not settings.admin_username or not settings.admin_password:
        raise HTTPException(status_code=403, detail="Admin not configured")
    username_ok = secrets.compare_digest(
        credentials.username.encode(), settings.admin_username.encode()
    )
    password_ok = secrets.compare_digest(
        credentials.password.encode(), settings.admin_password.encode()
    )
    if not (username_ok and password_ok):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )


router = APIRouter(prefix="/admin", dependencies=[Depends(verify_admin)])


@router.get("/signups", response_class=HTMLResponse)
async def signups(request: Request) -> HTMLResponse:
    db = request.app.state.db

    if db is None:
        return templates.TemplateResponse(
            request=request,
            name="admin/signups.html",
            context={"db_unavailable": True},
        )

    total = await db.signups.count_documents({})

    by_city_cursor = db.signups.aggregate(
        [
            {"$group": {"_id": "$city", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10},
        ]
    )
    by_city = [doc async for doc in by_city_cursor]

    by_member_type_cursor = db.signups.aggregate(
        [
            {"$group": {"_id": "$member_type", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]
    )
    by_member_type = [doc async for doc in by_member_type_cursor]

    by_role_cursor = db.signups.aggregate(
        [
            {"$group": {"_id": "$role", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]
    )
    by_role = [doc async for doc in by_role_cursor]

    recent_cursor = (
        db.signups.find(
            {},
            {"name": 1, "email": 1, "city": 1, "created_at": 1, "_id": 0},
        )
        .sort("created_at", -1)
        .limit(20)
    )
    recent = [doc async for doc in recent_cursor]

    return templates.TemplateResponse(
        request=request,
        name="admin/signups.html",
        context={
            "db_unavailable": False,
            "total": total,
            "by_city": by_city,
            "by_member_type": by_member_type,
            "by_role": by_role,
            "recent": recent,
        },
    )
