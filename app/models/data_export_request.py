"""
Data export request model - tracks DSAR export jobs.

Each record represents one user-initiated data export.
Status lifecycle: pending -> processing -> completed/failed -> expired
"""

from datetime import datetime

from app.extensions import db
from app.models.user import GUID


class DataExportRequest(db.Model):
    __tablename__ = "data_export_requests"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        GUID(),
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status = db.Column(db.String(20), default="pending", index=True)
    file_path = db.Column(db.Text, nullable=True)
    file_size_bytes = db.Column(db.BigInteger, nullable=True)
    download_token = db.Column(db.String(64), unique=True, index=True)
    expires_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    error_message = db.Column(db.Text, nullable=True)

    # Relationship
    user = db.relationship(
        "User", backref=db.backref("export_requests", lazy="dynamic")
    )

    def to_dict(self):
        return {
            "id": self.id,
            "status": self.status,
            "file_size_bytes": self.file_size_bytes,
            "download_token": self.download_token
            if self.status == "completed"
            else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat()
            if self.completed_at
            else None,
        }

    def __repr__(self):
        return f"<DataExportRequest {self.id}: user={self.user_id} status={self.status}>"
