import requests
import smtplib
from email.message import EmailMessage
from typing import Dict


def send_webhook_alert(url: str, payload: Dict, timeout: int = 5) -> bool:
    try:
        r = requests.post(url, json=payload, timeout=timeout)
        r.raise_for_status()
        return True
    except Exception:
        return False


def send_smtp_alert(smtp_cfg: Dict, subject: str, body: str) -> bool:
    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = smtp_cfg.get("from")
        msg["To"] = smtp_cfg.get("to")
        msg.set_content(body)

        with smtplib.SMTP(smtp_cfg.get("host"), smtp_cfg.get("port", 587)) as s:
            s.starttls()
            s.login(smtp_cfg.get("username"), smtp_cfg.get("password"))
            s.send_message(msg)
        return True
    except Exception:
        return False
