import csv
import os
import time
from pathlib import Path

import resend


def main() -> None:
    resend.api_key = os.environ["RESEND_API_KEY"]
    whatsapp_invite = os.environ["WHATSAPP_ORGANIZERS_URL"]

    csv_path = Path(__file__).with_name("organizers.csv")
    with open(csv_path) as f:
        organizers = list(csv.DictReader(f))

    for row in organizers:
        first_name = row["name"].split()[0]
        email = row["email"]

        html = (
            '<div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; color: #333;">'
            f'<h1 style="color: #306998;">Hola, {first_name}!</h1>'
            "<p>Gracias por querer ser parte de la organizacion de <strong>Python SV</strong>. "
            "Nos alegra mucho contar contigo.</p>"
            "<p>Como organizador, puedes ayudar con cosas como sugerir temas para charlas, "
            "buscar espacios para meetups, o simplemente correr la voz en tu circulo.</p>"
            '<h2 style="color: #306998;">Siguiente paso</h2>'
            "<p>Unite a nuestro grupo de WhatsApp donde estamos coordinando el proximo meetup:</p>"
            '<p style="text-align: center;">'
            f'<a href="{whatsapp_invite}" '
            'style="display: inline-block; background-color: #25D366; color: white; '
            'padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: bold;">'
            "Unirme al grupo de WhatsApp</a></p>"
            "<p>Si tienes ideas o preguntas, escribinos ahi. Nos vemos pronto!</p>"
            "<p><strong>— Python SV</strong></p></div>"
        )

        try:
            result = resend.Emails.send(
                {
                    "from": "Python SV <organizadores@pythonsv.com>",
                    "to": [email],
                    "subject": "Bienvenido al equipo de Python SV",
                    "html": html,
                }
            )
            print(f"OK: {first_name} <{email}> -> {result['id']}")
        except Exception as e:
            print(f"FAILED: {first_name} <{email}> -> {e}")

        time.sleep(1)


if __name__ == "__main__":
    main()
