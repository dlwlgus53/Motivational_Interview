# email_utils.py
import os
import smtplib, ssl
from email.message import EmailMessage
import traceback

SMTP_HOST     = "smtp.gmail.com"
SMTP_PORT     = 465
FROM_ADDRESS  = os.environ["SMTP_FROM"]
FROM_PW       = os.environ["SMTP_PW"]
TO_ADDRESS    = os.environ["SMTP_TO"]

def send_error_mail(subject: str, body: str) -> None:
    """Send a plain-text e-mail alert."""
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"]    = FROM_ADDRESS
    msg["To"]      = TO_ADDRESS
    msg.set_content(body)

    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=ctx) as server:
        server.login(FROM_ADDRESS, FROM_PW)
        server.send_message(msg)

def format_trace_email(idx, prompt_text, model_name, exception):
    """Format full traceback email content for LLM failure."""
    return {
        "subject": "[LLM-Retry] All attempts failed",
        "body": f"""\
Index: {idx}
Model: {model_name}

Prompt:
{prompt_text}

Exception:
{exception}

Traceback:
{traceback.format_exc()}
"""
    }
