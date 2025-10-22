import logging
import aiosmtplib
from email.message import EmailMessage
from jinja2 import Environment, PackageLoader, select_autoescape
from ..config import config
from ..models.files import UploadInfo

# Setup Jinja2 to load templates from inside the package
env = Environment(
    loader=PackageLoader("api", "templates"),
    autoescape=select_autoescape(["html", "xml"]),
)


class Mailer:
    """Mailer service to send emails using SMTP and Jinja2 templates"""

    def __init__(self):
        self.smtp_host = config.SMTP_HOST
        self.smtp_port = config.SMTP_PORT
        self.smtp_email = config.SMTP_EMAIL
        self.smtp_name = config.SMTP_NAME
        self.smtp_password = config.SMTP_PASSWORD
        self.smtp_username = config.SMTP_USERNAME
        self.smtp_subject_prefix = config.MAIL_SUBJECT_PREFIX

    async def send_data_uploaded_email(self, info: UploadInfo):
        """Send an email to the assignee when data is uploaded"""
        subject = f"Data uploaded: {info.path}"
        context = {
            "id": info.path,
            "url": f"{config.APP_URL}/contribute",
            "contribution": info.contribution,
        }
        # Send email to all administrators
        for email in config.MAIL_ADMINISTRATORS.split(","):
            await self.send_email(email, subject, "data_uploaded.html", context)

    async def send_email(
        self, to_email: str, subject: str, template_name: str, context: dict
    ):
        """Send an email using a Jinja2 template"""
        template = env.get_template(template_name)
        body = template.render(context)

        msg = EmailMessage()
        msg.set_content(body)
        msg.add_alternative(body, subtype="html")
        msg["Subject"] = (
            f"{self.smtp_subject_prefix} {subject}"
            if self.smtp_subject_prefix
            else subject
        )
        msg["From"] = f"{self.smtp_name} <{self.smtp_email}>"
        msg["To"] = to_email

        try:
            if self.smtp_username and self.smtp_password:
                await aiosmtplib.send(
                    msg,
                    hostname=self.smtp_host,
                    port=self.smtp_port,
                    username=self.smtp_username,
                    password=self.smtp_password,
                )
            else:
                await aiosmtplib.send(msg, hostname=self.smtp_host, port=self.smtp_port)
        except aiosmtplib.SMTPException as e:
            logging.error(f"Failed to send email to {to_email}: {e}")
