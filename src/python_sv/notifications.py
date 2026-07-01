from __future__ import annotations

import logging

import resend

from python_sv.config import get_settings

logger = logging.getLogger("pythonsv")

MEMBER_TYPE_LABELS = {
    "student": "Estudiante",
    "professional": "Profesional",
    "other": "Otro",
}

ROLE_LABELS = {
    "attend": "Asistir a eventos",
    "speak": "Dar charlas",
    "organize": "Ayudar a organizar",
}


def notify_signup(
    name: str, email: str, city: str, member_type: str, role: str
) -> None:
    settings = get_settings()
    if not settings.resend_api_key or not settings.notification_to:
        return

    resend.api_key = settings.resend_api_key
    member_type_label = MEMBER_TYPE_LABELS.get(member_type, member_type)
    role_label = ROLE_LABELS.get(role, role)

    try:
        resend.Emails.send(
            {
                "from": settings.notification_from,
                "to": [settings.notification_to],
                "html": (
                    f"<p><strong>{name}</strong> ({email})</p>"
                    f"<p>Ciudad: {city}<br>Tipo: {member_type_label}<br>Rol: {role_label}</p>"
                ),
            }
        )
    except Exception:
        logger.exception("No se pudo enviar la notificación de registro")


def notify_proposal(
    name: str, email: str, topic: str, description: str, level: str
) -> None:
    settings = get_settings()
    if not settings.resend_api_key or not settings.notification_to:
        return

    resend.api_key = settings.resend_api_key

    try:
        resend.Emails.send(
            {
                "from": settings.notification_from,
                "to": [settings.notification_to],
                "subject": f"Propuesta de charla: {topic}",
                "html": (
                    f"<p><strong>{name}</strong> ({email})</p>"
                    f"<p>Tema: {topic}<br>Nivel: {level}</p>"
                    f"<p>Descripción: {description}</p>"
                ),
            }
        )
    except Exception:
        logger.exception("No se pudo enviar la notificación de propuesta")
