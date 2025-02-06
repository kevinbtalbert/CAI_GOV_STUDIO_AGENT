from textwrap import dedent
from typing import Type, Literal, Optional, List
from pydantic import BaseModel, Field
from pydantic import BaseModel as StudioBaseTool
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os


# UserParameters Model to hold SMTP configuration
class UserParameters(BaseModel):
    """
    Args:
        smtp_server (str): The SMTP server address.
        smtp_port (int): The SMTP server port.
        smtp_password (Optional[str]): The password for the SMTP server (optional).
    """
    smtp_server: str
    smtp_port: str
    smtp_password: Optional[str] = None


# Refactored EmailSenderTool to send email using SMTP
class EmailSenderTool(StudioBaseTool):
    class ToolParameters(BaseModel):
        action: Literal["sendMail"] = Field(description="Action type specifying the operation to perform on Email: 'send email'")
        sender_email: str = Field(description="The sender's email address")
        recipients: List[str] = Field(description="List of primary recipient email addresses")
        subject: str = Field(description="The subject of the email")
        body: str = Field(description="The body content of the email")
        cc: List[str] = Field(description="List of CC email addresses, empty list is acceptable if there are no cc email addresses specified")
        bcc: List[str] = Field(description="List of BCC email addresses, empty list is acceptable if there are no bcc email addresses specified")
        attachments: List[str] = Field(description="List of file paths to attach, empty list is acceptable if there are no files to attach")

    name: str = "Email Sender Tool"
    description: str = dedent(
        """
        Tool to send an email to the specified receivers.
        """
    )
    args_schema: Type[BaseModel] = ToolParameters
    user_parameters: UserParameters
    def _run(
        self,
        action: Literal["sendMail"],
        sender_email: str,
        recipients: List[str],
        subject: str,
        body: str,
        cc: [List[str]],
        bcc: [List[str]],
        attachments: [List[str]]
    ) -> str:
        """
        Sends an email using the specified SMTP server.
        """
        try:
            if action == "sendMail":
            # Prepare the email message
                message = MIMEMultipart()
                message["From"] = sender_email
                message["To"] = ", ".join(recipients)  # Join multiple recipients for the To field
                message["Subject"] = subject

                # Add CC recipients if provided
                if cc:
                    message["Cc"] = ", ".join(cc)

                # Attach the body content
                message.attach(MIMEText(body, "plain"))

                # Add attachments if provided
                if attachments:
                    for file_path in attachments:
                        if os.path.exists(file_path):
                            with open(file_path, "rb") as file:
                                part = MIMEBase("application", "octet-stream")
                                part.set_payload(file.read())
                                encoders.encode_base64(part)
                                part.add_header(
                                    "Content-Disposition",
                                    f"attachment; filename={os.path.basename(file_path)}",
                                )
                                message.attach(part)
                        else:
                            return f"Attachment file not found: {file_path}"

                # Combine all recipients (To, CC, BCC)
                all_recipients = recipients[:]  # Start with primary recipients
                if cc:
                    all_recipients.extend(cc)
                if bcc:
                    all_recipients.extend(bcc)

                # Connect to the SMTP server
                with smtplib.SMTP(self.user_parameters.smtp_server, int(self.user_parameters.smtp_port)) as server:
                    server.starttls()  # Enable encryption (STARTTLS)

                    # Authenticate if an SMTP password is provided
                    if self.user_parameters.smtp_password:
                        server.login(sender_email, self.user_parameters.smtp_password)

                    # Send the email
                    server.sendmail(sender_email, all_recipients, message.as_string())

                return f"Email sent successfully to {', '.join(recipients)}!"

            return "Invalid action type. Available action is 'sendMail'."
        except Exception as e:
            return f"Failed to send email: {e}"