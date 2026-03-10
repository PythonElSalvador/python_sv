from __future__ import annotations

import logging

import resend

from app.config import get_settings

logger = logging.getLogger("pythonsv")


def notify_signup(name: str, email: str, city: str, member_type: str, role: str) -> None:
    settings = get_settings()
    if not settings.resend_api_key or not settings.notification_to:
        return

    resend.api_key = settings.resend_api_key

    try:
        resend.Emails.send(
            {
                "from": settings.notification_from,
                "to": [settings.notification_to],
                "subject": f"New signup: {name}",
                "html": (
                    f"<p><strong>{name}</strong> ({email})</p>"
                    f"<p>City: {city}<br>Type: {member_type}<br>Role: {role}</p>"
                ),
            }
        )
    except Exception:
        logger.exception("Failed to send signup notification")
