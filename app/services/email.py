import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.EMAILS_FROM_EMAIL or settings.SMTP_USER
        self.from_name = settings.EMAILS_FROM_NAME

    def send_email(self, recipient: str, subject: str, body: str):
        """Send a simple plain-text email using SMTP."""
        if not self.smtp_user or not self.smtp_password:
            logger.warning(f"SMTP credentials missing. Logging email to {recipient} instead.")
            logger.info(f"Subject: {subject}\nBody:\n{body}")
            return True

        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["From"] = f"{self.from_name} <{self.from_email}>"
        msg["To"] = recipient

        msg.attach(MIMEText(body, "plain"))

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {recipient}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {recipient}: {str(e)}")
            return False

    def send_verification_otp(self, email: str, name: str, otp: str):
        """Send minimal email verification OTP."""
        subject = f"Verify your {settings.APP_NAME} account"
        body = (
            f"Hello {name},\n\n"
            f"Your verification code is: {otp}\n\n"
            "This code will expire in 10 minutes. If you did not request this, please ignore this email.\n\n"
            "Regards,\n"
            f"The {settings.APP_NAME} Team"
        )
        return self.send_email(email, subject, body)

    def send_password_reset_otp(self, email: str, otp: str):
        """Send minimal password reset OTP."""
        subject = f"Reset your {settings.APP_NAME} password"
        body = (
            f"Hello,\n\n"
            f"You requested a password reset. Your reset code is: {otp}\n\n"
            "This code will expire in 1 hour. If you did not request this, please ignore this email.\n\n"
            "Regards,\n"
            f"The {settings.APP_NAME} Team"
        )
        return self.send_email(email, subject, body)

    def send_appointment_confirmed(self, email: str, name: str, appointment_data: dict):
        """Send minimal appointment confirmation email."""
        subject = f"Appointment Confirmed - {settings.APP_NAME}"
        body = (
            f"Hello {name},\n\n"
            f"Your appointment has been confirmed for {appointment_data.get('date')} at {appointment_data.get('time')}.\n"
            f"Specialist: {appointment_data.get('specialist_name')}\n"
            f"Type: {appointment_data.get('type')}\n"
        )
        if appointment_data.get('meeting_link'):
            body += f"Meeting Link: {appointment_data.get('meeting_link')}\n"
        
        body += (
            "\nPlease log in to your dashboard for more details.\n\n"
            "Regards,\n"
            f"The {settings.APP_NAME} Team"
        )
        return self.send_email(email, subject, body)

# Global instances
email_service = EmailService()
