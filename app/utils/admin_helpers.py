"""
Admin Utility Functions

Provides helper functions for admin operations including audit logging.
"""

import json

from flask import request

from app.extensions import db
from app.models.admin_audit_log import AdminAuditLog


def log_admin_action(
    admin_user_id: str,
    action: str,
    target_type: str = None,
    target_id: str = None,
    details: dict = None,
):
    """
    Create an audit log entry for an admin action.

    Args:
        admin_user_id: UUID string of the admin performing the action
        action: Dot-separated action identifier (e.g., 'admin_login', 'user_update')
        target_type: Type of entity acted upon (e.g., 'user', 'subscription')
        target_id: UUID string of the target entity
        details: Optional dict of additional context (stored as JSON string)
    """
    try:
        log_entry = AdminAuditLog(
            admin_user_id=admin_user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            details=json.dumps(details) if details else None,
            ip_address=request.remote_addr if request else None,
            user_agent=str(request.user_agent)[:500] if request else None,
        )
        db.session.add(log_entry)
        db.session.commit()
        return log_entry
    except Exception as e:
        import logging

        logging.getLogger(__name__).error(f"Admin audit log error: {e}")
        return None
