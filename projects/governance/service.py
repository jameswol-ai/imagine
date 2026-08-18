from sqlalchemy.orm import Session
from .models import GovernanceRule

def create_rule(db: Session, project_id: int, rule_name: str, description: str = None):
    rule = GovernanceRule(project_id=project_id, rule_name=rule_name, description=description)
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule

def list_rules(db: Session, project_id: int):
    return db.query(GovernanceRule).filter(GovernanceRule.project_id == project_id).all()