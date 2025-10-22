from mailjet_rest import Client

from app.core.config import settings
from app.domain.services import EmailService


class MailJetEmailService(EmailService):
    """
    Email service implementation using MailJet API.
    """

    def __init__(self, api_key: str, api_secret: str, from_email: str, from_name: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.from_email = from_email
        self.from_name = from_name
        self.mailjet = Client(auth=(api_key, api_secret), version="v3.1")

    async def send_verification_email(
        self, to_email: str, verification_code: str
    ) -> bool:
        """
        Send verification email to user using MailJet.

        Args:
            to_email: Recipient email address
            verification_code: Verification code to include in email

        Returns:
            True if email was sent successfully, False otherwise
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

        # In production, send actual email via MailJet

        # TODO: In a real production environment,
        # this should be handled by a background task
        # to avoid blocking the API response.
        # Consider using Celery
        # or similar task queue.
        try:
            data = {
                "Messages": [
                    {
                        "From": {"Email": self.from_email, "Name": self.from_name},
                        "To": [{"Email": to_email, "Name": to_email.split("@")[0]}],
                        "Subject": "Verify your Coffee Shop account",
                        "TextPart": f"Your verification code is: {verification_code}",  # noqa: E501
                        "HTMLPart": f"""
                        <html>
                            <body style="font-family: Arial, sans-serif; padding: 20px;">
                                <h2>Welcome to Coffee Shop!</h2>
                                <p>
                                    Thank you for registering.
                                    Please use the verification code below
                                    to verify your email address:
                                </p>
                                <div style="background-color: #f4f4f4; padding: 15px; margin: 20px 0; border-radius: 5px;">
                                    <h1 style="color: #333; margin: 0; letter-spacing: 5px;">
                                        {verification_code}
                                    </h1>
                                </div>
                                <p>This code will expire in 48 hours.</p>
                                <p>
                                    If you didn't create an account,
                                    please ignore this email.
                                </p>
                                <p>Best regards,<br>The Coffee Shop Team</p>
                            </body>
                        </html>
                        """,  # noqa: E501
                    }
                ]
            }

            result = self.mailjet.send.create(data=data)
            return result.status_code == 200

        except Exception as e:
            print(f"Failed to send email via MailJet: {e}")
            return False
