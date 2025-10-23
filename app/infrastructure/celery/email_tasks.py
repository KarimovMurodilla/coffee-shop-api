import traceback

from mailjet_rest import Client

from app.core.config import settings
from app.infrastructure.celery.worker import celery_app


@celery_app.task(name="app.infrastructure.celery.email_tasks.send_verification_email")
def send_verification_email(to_email: str, verification_code: str) -> dict:
    """
    Celery task to send a verification email via MailJet.

    Returns a dict with the send result.
    """
    # In development, just print the code to console
    if settings.environment == "development":
        print(f"\n{'=' * 60}")
        print("VERIFICATION EMAIL (queued)")
        print(f"{'=' * 60}")
        print(f"To: {to_email}")
        print(f"Verification Code: {verification_code}")
        print(f"{'=' * 60}\n")
        return {"ok": True, "queued": True}

    try:
        mailjet = Client(
            auth=(settings.mailjet_api_key, settings.mailjet_api_secret),
            version="v3.1",
        )

        data = {
            "Messages": [
                {
                    "From": {
                        "Email": settings.mailjet_from_email,
                        "Name": settings.mailjet_from_name,
                    },
                    "To": [{"Email": to_email, "Name": to_email.split("@")[0]}],
                    "Subject": "Verify your Coffee Shop account",
                    "TextPart": f"Your verification code is: {verification_code}",
                    "HTMLPart": f"""
                    <html>
                        <body style="font-family: Arial, sans-serif; padding: 20px;">
                            <h2>Welcome to Coffee Shop!</h2>
                            <p>
                                Thank you for registering.
                                Please use the verification code below
                                to verify your email address:
                            </p>
                            <div style="background-color: #f4f4f4; padding: 15px;
                                margin: 20px 0;
                                border-radius: 5px;">
                                <h1 style="color: #333; margin: 0;
                                letter-spacing: 5px;">
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
                    """,
                }
            ]
        }

        result = mailjet.send.create(data=data)
        return {"ok": result.status_code == 200, "status_code": result.status_code}

    except Exception as exc:  # pragma: no cover - best-effort reporting
        traceback.print_exc()
        return {"ok": False, "error": str(exc)}
