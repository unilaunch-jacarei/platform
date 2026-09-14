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
