"""
Admin Audit Log Model

Tracks administrative actions for accountability and security auditing.
"""

import json
from datetime import datetime

from app.extensions import db


class AdminAuditLog(db.Model):
    """Audit log for admin actions."""

    __tablename__ = "admin_audit_log"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    admin_user_id = db.Column(
        db.String(36),
        db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    action = db.Column(db.String(100), nullable=False)
    target_type = db.Column(db.String(50), nullable=True)
    target_id = db.Column(db.String(36), nullable=True)
    details = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Relationship
    admin_user = db.relationship(
        "User",
        backref=db.backref("admin_audit_logs", lazy="dynamic"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "admin_user_id": self.admin_user_id,
            "action": self.action,
            "target_type": self.target_type,
            "target_id": self.target_id,
            "details": json.loads(self.details) if self.details else {},
            "ip_address": self.ip_address,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<AdminAuditLog {self.id} action={self.action}>"
