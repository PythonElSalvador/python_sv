import os

import resend

resend.api_key = os.environ["RESEND_API_KEY"]
AUDIENCE_ID = os.environ["RESEND_AUDIENCE_ID"]

html = (
    '<div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; color: #333;">'
    '<h1 style="color: #306998;">Hola, {{{FIRST_NAME}}}!</h1>'
    "<p>El primer meetup de <strong>Python SV</strong> es mañana. Aqui van los detalles:</p>"
    '<div style="background: #fff3cd; border-left: 4px solid #FFD43B; padding: 16px; margin: 20px 0; border-radius: 4px;">'
    '<p style="margin: 0;">Sabemos que ya te registraste en nuestra pagina — gracias por eso. '
    "Te pedimos que tambien confirmes en Meetup porque la <strong>Python Software Foundation (PSF)</strong> "
    "apoya a las comunidades cubriendo los costos de Meetup.com. Este programa estuvo en pausa desde 2025 "
    "y justo hoy se reactivo, por eso el doble registro. Disculpa la molestia.</p>"
    "</div>"
    '<div style="background: #f4f4f4; border-left: 4px solid #306998; padding: 16px; margin: 20px 0; border-radius: 4px;">'
    '<p style="margin: 0 0 8px;"><strong>Fecha:</strong> Sabado 14 de marzo, 2PM - 5PM</p>'
    '<p style="margin: 0;"><strong>Lugar:</strong> Alveare, Piso 4, Paseo General Escalon #3675, Millennium Plaza, San Salvador</p>'
    "</div>"
    "<p>Confirma tu asistencia en Meetup para que tengamos un mejor conteo:</p>"
    '<p style="text-align: center;">'
    '<a href="https://www.meetup.com/san-salvador-python-meetup-group/events/313772673/" '
    'style="display: inline-block; background-color: #FFD43B; color: #306998; '
    'padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: bold;">'
    "Confirmar en Meetup</a></p>"
    "<p>No necesitas traer nada — solo ganas de conocer a la comunidad. Nos vemos ahi.</p>"
    "<p><strong>— Python SV</strong></p></div>"
)

broadcast = resend.Broadcasts.create(
    {
        "audience_id": AUDIENCE_ID,
        "from": "Python SV <hola@pythonsv.com>",
        "subject": "Nos vemos mañana — Primer meetup de Python SV",
        "html": html,
    }
)
broadcast_id = broadcast["id"]
print(f"Broadcast created: {broadcast_id}")

result = resend.Broadcasts.send({"broadcast_id": broadcast_id})
print(f"Broadcast sent: {result}")
