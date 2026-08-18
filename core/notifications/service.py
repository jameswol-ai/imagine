from sqlalchemy.orm import Session

def send_email(to: str, subject: str, body: str):
    # TODO: integrate with real email provider
    return {"status": "queued", "to": to, "subject": subject}

def create_notification(db: Session, to: str, subject: str, body: str, send_email: bool = True, send_in_app: bool = True):
    # TODO: persist notification and optionally send email
    if send_email:
        send_email(to, subject, body)
    return {"id": 1, "to": to, "subject": subject, "body": body}
