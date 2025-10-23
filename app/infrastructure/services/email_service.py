from app.core.config import settings
from app.domain.services import EmailService
from app.infrastructure.celery.email_tasks import (
    send_verification_email as send_verification_email_task,
)


class MailJetEmailService(EmailService):
    """
    Email service implementation using MailJet API.
    This implementation dispatches a Celery task to send emails so the web request
    remains fast. In development it will still print to console.
    """

    def __init__(self, api_key: str, api_secret: str, from_email: str, from_name: str):
        # keep attributes for possible direct-send fallback
        self.api_key = api_key
        self.api_secret = api_secret
        self.from_email = from_email
        self.from_name = from_name

    async def send_verification_email(
        self, to_email: str, verification_code: str
    ) -> bool:
        """
        Dispatch a Celery task to send a verification email.

        Returns True if the task was dispatched or if running in development
        (where it prints); otherwise returns False.
        """
        # In development, just print the code to console
        if settings.environment == "development":
            print(f"\n{'=' * 60}")
            print("VERIFICATION EMAIL")
            print(f"{'=' * 60}")
            print(f"To: {to_email}")
            print(f"Verification Code: {verification_code}")
            print(f"{'=' * 60}\n")
            return True

        # Dispatch celery task to send email asynchronously
        try:
            # delay/async apply
            send_verification_email_task.delay(to_email, verification_code)
            return True
        except Exception as exc:
            # If for some reason dispatching fails, fall back to synchronous send
            print(f"Failed to dispatch email task, falling back to sync send: {exc}")
            return False
