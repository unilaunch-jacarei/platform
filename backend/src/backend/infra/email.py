import asyncio
import smtplib
from email.message import EmailMessage
from urllib.parse import urlencode

from backend.config import Settings


def build_password_reset_message(settings: Settings, recipient: str, token: str) -> EmailMessage:
    query = urlencode({"token": token})
    reset_url = f"{settings.public_app_url.rstrip('/')}/reset-password?{query}"
    message = EmailMessage()
    message["Subject"] = "Redefinição de senha | UniLaunch"
    message["From"] = settings.smtp_from_email
    message["To"] = recipient
    message.set_content(
        "Recebemos uma solicitação para redefinir sua senha na UniLaunch.\n\n"
        f"Acesse o link: {reset_url}\n\n"
        "Se você não fez essa solicitação, ignore esta mensagem."
    )
    return message


async def send_password_reset_email(settings: Settings, recipient: str, token: str) -> bool:
    if not settings.smtp_host or not settings.smtp_from_email:
        return False

    message = build_password_reset_message(settings, recipient, token)

    def send() -> None:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as client:
            if settings.smtp_starttls:
                client.starttls()
            if settings.smtp_username and settings.smtp_password:
                client.login(settings.smtp_username, settings.smtp_password)
            client.send_message(message)

    await asyncio.to_thread(send)
    return True
