from sqlalchemy.orm import Session
from datetime import datetime

def log_event(db: Session, user_id: int, action: str, resource: str = None, metadata: dict | None = None):
    # TODO: persist audit record to DB
    record = {
        "id": 1,
        "user_id": user_id,
        "action": action,
        "resource": resource,
        "metadata": metadata or {},
        "timestamp": datetime.utcnow().isoformat()
    }
    # For now, just return the record
    return record
