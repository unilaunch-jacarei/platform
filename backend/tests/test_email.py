import pytest

from backend.config import Settings
from backend.infra.email import build_password_reset_message


def test_password_reset_message_contains_encoded_link():
    settings = Settings(
        _env_file=None,
        PUBLIC_APP_URL="https://unilaunch.org/",
        SMTP_FROM_EMAIL="contato@unilaunch.org",
    )

    message = build_password_reset_message(settings, "aluno@example.com", "token com espaços")

    assert message["To"] == "aluno@example.com"
    assert message["From"] == "contato@unilaunch.org"
    assert (
        "https://unilaunch.org/reset-password?token=token+com+espa%C3%A7os" in message.get_content()
    )


@pytest.mark.asyncio
async def test_send_password_reset_email(monkeypatch):
    from unittest.mock import MagicMock

    from backend.infra.email import send_password_reset_email

    # Unconfigured SMTP
    unconfigured_settings = Settings(
        _env_file=None,
        SMTP_HOST="",
        SMTP_FROM_EMAIL="",
    )
    result = await send_password_reset_email(unconfigured_settings, "aluno@example.com", "token123")
    assert result is False

    # Configured SMTP with starttls and auth
    configured_settings = Settings(
        _env_file=None,
        SMTP_HOST="smtp.example.com",
        SMTP_PORT=587,
        SMTP_FROM_EMAIL="contato@unilaunch.org",
        SMTP_USERNAME="smtp_user",
        SMTP_PASSWORD="smtp_password",
        SMTP_STARTTLS=True,
    )

    mock_client = MagicMock()
    mock_smtp = MagicMock(return_value=mock_client)
    mock_client.__enter__.return_value = mock_client

    import smtplib

    monkeypatch.setattr(smtplib, "SMTP", mock_smtp)

    result = await send_password_reset_email(configured_settings, "aluno@example.com", "token123")
    assert result is True
    mock_smtp.assert_called_once_with("smtp.example.com", 587, timeout=15)
    mock_client.starttls.assert_called_once()
    mock_client.login.assert_called_once_with("smtp_user", "smtp_password")
    mock_client.send_message.assert_called_once()
