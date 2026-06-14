from flask_mail import Mail, Message
from flask import render_template, current_app
import os

mail = Mail()


def send_email(to_email, subject, template_name, attachment_path=None, **kwargs):
    """
    Very small helper around Flask‑Mail.
    Works out of the box with MailHog/Mailtrap running on localhost:1025.
    """
    try:
        html_body = render_template(f"email/{template_name}.html", **kwargs)

        # Fallback sender so it works even if MAIL_DEFAULT_SENDER is not set.
        sender = current_app.config.get("MAIL_DEFAULT_SENDER") or "hms@example.local"

        msg = Message(
            subject=subject,
            recipients=[to_email],
            html=html_body,
            sender=sender,
        )

        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, "rb") as fp:
                msg.attach(
                    os.path.basename(attachment_path),
                    "text/csv",
                    fp.read(),
                )

        mail.send(msg)
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False