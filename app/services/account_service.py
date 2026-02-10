"""
Account deletion and data export service for Jobezie.

Handles:
  - Soft-delete with 30-day grace period (CCPA/state law compliant)
  - Hard-delete cascade across all user tables + file cleanup
  - DSAR data export to downloadable ZIP
  - Email notifications for each stage

Design: Synchronous now. When Celery arrives (Phase 2), wrap
create_data_export() and process_expired_deletions() in @celery.task.
The logic stays identical - only the invocation changes.
"""

import json
import logging
import os
import uuid
import zipfile
from datetime import datetime, timedelta

from app.extensions import db
from app.models.data_export_request import DataExportRequest
from app.models.user import User

logger = logging.getLogger(__name__)

# ───────────────────────────────────────────
# Configuration
# ───────────────────────────────────────────

GRACE_PERIOD_DAYS = 30
EXPORT_EXPIRY_DAYS = 7
EXPORT_DIR = os.environ.get("EXPORT_DIR", "data/exports")
RESUME_DIR = os.environ.get("RESUME_DIR", "data/resumes/uploads")

os.makedirs(EXPORT_DIR, exist_ok=True)


# ───────────────────────────────────────────
# ACCOUNT DELETION
# ───────────────────────────────────────────


def request_account_deletion(user_id) -> dict:
    """
    Soft-delete: mark account for deletion after 30-day grace period.
    User can cancel within the window. Subscription is cancelled immediately.
    """
    user = User.query.get(user_id)
    if not user:
        return {"error": "User not found", "status_code": 404}

    if user.is_deleted:
        return {"error": "Account already deleted", "status_code": 400}

    if user.deletion_requested_at:
        return {"error": "Deletion already requested", "status_code": 400}

    now = datetime.utcnow()
    scheduled_for = now + timedelta(days=GRACE_PERIOD_DAYS)

    user.deletion_requested_at = now
    user.deletion_scheduled_for = scheduled_for

    # Cancel Stripe subscription immediately
    _cancel_subscription(user)

    db.session.commit()

    # Confirmation email (best-effort)
    _send_deletion_requested_email(user, scheduled_for)

    return {
        "message": "Account scheduled for deletion",
        "deletion_requested_at": now.isoformat(),
        "deletion_scheduled_for": scheduled_for.isoformat(),
        "grace_period_days": GRACE_PERIOD_DAYS,
    }


def cancel_account_deletion(user_id) -> dict:
    """Cancel a pending deletion request within the grace period."""
    user = User.query.get(user_id)
    if not user:
        return {"error": "User not found", "status_code": 404}

    if not user.deletion_requested_at:
        return {"error": "No pending deletion request", "status_code": 400}

    if user.is_deleted:
        return {"error": "Account already permanently deleted", "status_code": 400}

    user.deletion_requested_at = None
    user.deletion_scheduled_for = None
    db.session.commit()

    return {"message": "Deletion cancelled. Your account is active."}


def hard_delete_user(user_id) -> dict:
    """
    Permanently delete ALL user data from PostgreSQL + files.

    Deletion order (children before parent):
      1. Resume files on disk (or S3)
      2. Export ZIP files on disk (or S3)
      3. Child table records (explicit SQL for safety)
      4. User record itself

    Called by:
      - Scheduled task after grace period expires
      - Admin action (immediate)
    """
    user = User.query.get(user_id)
    if not user:
        return {"error": "User not found", "status_code": 404}

    user_email = user.email
    warnings = []

    # -- Step 1: Delete resume files --
    try:
        _delete_user_resume_files(user_id)
    except Exception as e:
        logger.warning(f"Resume file cleanup for user {user_id}: {e}")
        warnings.append(f"Resume file cleanup: {str(e)}")

    # -- Step 2: Delete export ZIP files --
    try:
        _delete_user_export_files(user_id)
    except Exception as e:
        logger.warning(f"Export file cleanup for user {user_id}: {e}")
        warnings.append(f"Export file cleanup: {str(e)}")

    # -- Step 3: Delete child table records --
    child_tables = [
        "user_milestones",
        "user_streaks",
        "data_export_requests",
        "coach_conversations",
        "activities",
        "messages",
        "resumes",
        "recruiters",
        "subscriptions",
        "notifications",
    ]

    for table in child_tables:
        try:
            db.session.execute(
                db.text(f"DELETE FROM {table} WHERE user_id = :uid"),
                {"uid": str(user_id)},
            )
        except Exception as e:
            err_str = str(e).lower()
            if "does not exist" in err_str or "relation" in err_str:
                pass  # Table not created yet
            else:
                db.session.rollback()
                logger.warning(f"Delete from {table} for user {user_id}: {e}")
                warnings.append(f"{table}: {str(e)[:100]}")

    # -- Step 4: Delete user record --
    try:
        db.session.delete(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to delete user {user_id}: {e}")
        return {
            "error": "Failed to delete user record",
            "details": str(e),
            "status_code": 500,
        }

    # -- Step 5: Final confirmation email --
    _send_deletion_complete_email(user_email)

    result = {"message": "Account permanently deleted"}
    if warnings:
        result["warnings"] = warnings
    return result


def process_expired_deletions():
    """
    Batch job: hard-delete all accounts past their grace period.

    Call this from:
      - Celery beat (Phase 2): daily at 2 AM UTC
      - Admin manual trigger: POST /api/admin/data/process-deletions
      - CLI: flask process-deletions
    """
    now = datetime.utcnow()
    expired_users = User.query.filter(
        User.deletion_scheduled_for <= now,
        User.deletion_requested_at.isnot(None),
        User.is_deleted == False,  # noqa: E712
    ).all()

    results = []
    for user in expired_users:
        result = hard_delete_user(user.id)
        results.append({"user_id": str(user.id), **result})

    return {
        "processed": len(results),
        "results": results,
    }


# ───────────────────────────────────────────
# DATA EXPORT (DSAR)
# ───────────────────────────────────────────


def create_data_export(user_id) -> dict:
    """
    Generate a ZIP containing all user data.

    Contents:
      profile.json, recruiters.json, messages.json, activities.json,
      resumes/ (metadata + files), scores.json, coach_history.json,
      subscriptions.json, engagement.json, metadata.json

    Returns dict with download_token on success.
    """
    user = User.query.get(user_id)
    if not user:
        return {"error": "User not found", "status_code": 404}

    # Throttle: one active export at a time
    active = DataExportRequest.query.filter_by(user_id=user_id, status="processing").first()
    if active:
        return {"error": "An export is already in progress", "status_code": 409}

    # Create tracking record
    download_token = uuid.uuid4().hex
    export_req = DataExportRequest(
        user_id=user_id,
        status="processing",
        download_token=download_token,
        expires_at=datetime.utcnow() + timedelta(days=EXPORT_EXPIRY_DAYS),
    )
    db.session.add(export_req)
    db.session.commit()

    try:
        zip_name = f'jobezie_export_{user_id}_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.zip'
        zip_path = os.path.join(EXPORT_DIR, zip_name)

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            # Profile
            profile = _export_profile(user)
            zf.writestr("profile.json", _to_json(profile))

            # Recruiters
            recruiters = _query_table("recruiters", user_id)
            zf.writestr("recruiters.json", _to_json(recruiters))

            # Messages
            messages = _query_table("messages", user_id)
            zf.writestr("messages.json", _to_json(messages))

            # Activities
            activities = _query_table("activities", user_id)
            zf.writestr("activities.json", _to_json(activities))

            # Resume files + metadata
            resumes = _query_table("resumes", user_id)
            zf.writestr("resumes/resume_metadata.json", _to_json(resumes))
            _add_resume_files_to_zip(user_id, zf)

            # Score history (from resume records)
            scores = _export_scores(user_id)
            zf.writestr("scores.json", _to_json(scores))

            # Coach conversations
            coach = _query_table("coach_conversations", user_id)
            zf.writestr("coach_history.json", _to_json(coach))

            # Subscriptions
            subs = _query_table("subscriptions", user_id)
            zf.writestr("subscriptions.json", _to_json(subs))

            # Streaks + milestones
            streaks = _query_table("user_streaks", user_id)
            milestones = _query_table("user_milestones", user_id)
            zf.writestr(
                "engagement.json",
                _to_json({"streaks": streaks, "milestones": milestones}),
            )

            # Export metadata
            metadata = {
                "export_date": datetime.utcnow().isoformat(),
                "platform": "Jobezie (jobezie.com)",
                "user_id": str(user_id),
                "data_categories": [
                    "profile",
                    "recruiters",
                    "messages",
                    "activities",
                    "resumes",
                    "scores",
                    "coach_history",
                    "subscriptions",
                    "streaks",
                    "milestones",
                ],
                "record_counts": {
                    "recruiters": len(recruiters),
                    "messages": len(messages),
                    "activities": len(activities),
                    "resumes": len(resumes),
                    "coach_messages": len(coach),
                },
                "expires_at": export_req.expires_at.isoformat(),
                "note": "AI provider (Anthropic/OpenAI) conversation logs are not retained by Jobezie.",
            }
            zf.writestr("metadata.json", _to_json(metadata))

        # Finalize record
        file_size = os.path.getsize(zip_path)
        export_req.status = "completed"
        export_req.file_path = zip_path
        export_req.file_size_bytes = file_size
        export_req.completed_at = datetime.utcnow()
        db.session.commit()

        _send_export_ready_email(user, download_token)

        return {
            "message": "Data export ready for download",
            "download_token": download_token,
            "expires_at": export_req.expires_at.isoformat(),
            "file_size_bytes": file_size,
        }

    except Exception as e:
        logger.error(f"Data export failed for user {user_id}: {e}")
        export_req.status = "failed"
        export_req.error_message = str(e)[:500]
        db.session.commit()
        return {"error": f"Export failed: {str(e)}", "status_code": 500}


def get_export_status(user_id) -> dict:
    """Return status of the user's most recent export request."""
    export = (
        DataExportRequest.query.filter_by(user_id=user_id)
        .order_by(DataExportRequest.created_at.desc())
        .first()
    )

    if not export:
        return {"status": "none"}

    return export.to_dict()


def get_export_download(download_token: str) -> dict:
    """
    Validate a download token and return the file path.
    Token-based auth - no JWT needed (link from email).
    """
    export = DataExportRequest.query.filter_by(
        download_token=download_token,
        status="completed",
    ).first()

    if not export:
        return {"error": "Export not found or not yet ready", "status_code": 404}

    if datetime.utcnow() > export.expires_at:
        export.status = "expired"
        db.session.commit()
        return {
            "error": "Download link has expired. Request a new export.",
            "status_code": 410,
        }

    if not export.file_path or not os.path.exists(export.file_path):
        return {"error": "Export file no longer available", "status_code": 404}

    return {"file_path": export.file_path, "user_id": str(export.user_id)}


# ───────────────────────────────────────────
# INTERNAL HELPERS
# ───────────────────────────────────────────


def _query_table(table_name: str, user_id) -> list:
    """Generic query: SELECT * FROM table WHERE user_id = :uid."""
    try:
        rows = db.session.execute(
            db.text(f"SELECT * FROM {table_name} WHERE user_id = :uid ORDER BY id"),
            {"uid": str(user_id)},
        ).fetchall()
        return [dict(row._mapping) for row in rows]
    except Exception:
        return []


def _export_profile(user) -> dict:
    """Export user profile, stripping sensitive internal fields."""
    data = user.to_dict(include_private=True)
    for key in [
        "password_hash",
        "is_admin",
        "deletion_requested_at",
        "deletion_scheduled_for",
        "is_deleted",
    ]:
        data.pop(key, None)
    return data


def _export_scores(user_id) -> dict:
    """Extract score data from resume records."""
    scores = {"ats_scores": [], "readiness_history": []}
    try:
        rows = db.session.execute(
            db.text(
                """
                SELECT id, title, ats_score, ats_breakdown, created_at, updated_at
                FROM resumes
                WHERE user_id = :uid AND ats_score IS NOT NULL
                ORDER BY created_at
            """
            ),
            {"uid": str(user_id)},
        ).fetchall()
        scores["ats_scores"] = [dict(r._mapping) for r in rows]
    except Exception:
        pass
    return scores


def _add_resume_files_to_zip(user_id, zf: zipfile.ZipFile):
    """Add actual resume files (PDF/DOCX) to the ZIP."""
    try:
        rows = db.session.execute(
            db.text(
                """
                SELECT file_path, original_filename, saved_filename
                FROM resumes WHERE user_id = :uid
            """
            ),
            {"uid": str(user_id)},
        ).fetchall()

        for row in rows:
            r = dict(row._mapping)
            filename = r.get("saved_filename") or r.get("file_path")
            if not filename:
                continue

            full_path = os.path.join(RESUME_DIR, os.path.basename(filename))
            if os.path.exists(full_path):
                archive_name = r.get("original_filename") or os.path.basename(filename)
                zf.write(full_path, f"resumes/{archive_name}")
    except Exception:
        pass


def _to_json(data) -> str:
    """Serialize to pretty JSON, handling datetimes."""
    return json.dumps(data, indent=2, default=str, ensure_ascii=False)


# -- File Cleanup --


def _delete_user_resume_files(user_id):
    """Delete all resume files from disk for a user."""
    rows = db.session.execute(
        db.text("SELECT file_path, saved_filename FROM resumes WHERE user_id = :uid"),
        {"uid": str(user_id)},
    ).fetchall()

    for row in rows:
        r = dict(row._mapping)
        filename = r.get("saved_filename") or r.get("file_path")
        if filename:
            full_path = os.path.join(RESUME_DIR, os.path.basename(filename))
            if os.path.exists(full_path):
                os.remove(full_path)
                logger.info(f"Deleted resume file: {full_path}")
    # TODO Phase 2: s3.delete_objects(Bucket='jobezie-resumes', ...)


def _delete_user_export_files(user_id):
    """Delete all export ZIPs from disk for a user."""
    rows = db.session.execute(
        db.text("SELECT file_path FROM data_export_requests WHERE user_id = :uid"),
        {"uid": str(user_id)},
    ).fetchall()

    for row in rows:
        path = dict(row._mapping).get("file_path")
        if path and os.path.exists(path):
            os.remove(path)
            logger.info(f"Deleted export file: {path}")


# -- Subscription --


def _cancel_subscription(user):
    """Cancel active Stripe subscription."""
    try:
        import stripe

        sub_id = getattr(user, "stripe_subscription_id", None)
        if sub_id:
            stripe.Subscription.cancel(sub_id)
            logger.info(f"Cancelled Stripe subscription {sub_id} for user {user.id}")
    except Exception as e:
        logger.warning(f"Stripe cancellation failed for user {user.id}: {e}")


# -- Emails --


def _send_deletion_requested_email(user, scheduled_for):
    """Notify user their account is scheduled for deletion."""
    try:
        from app.services.email_service import EmailService

        EmailService.send_email(
            to_email=user.email,
            subject="Jobezie - Account Deletion Requested",
            content=f"""
Hi {user.first_name or user.email},

We received your request to delete your Jobezie account.

Your account and all associated data will be permanently deleted on {scheduled_for.strftime('%B %d, %Y')}.

You have {GRACE_PERIOD_DAYS} days to cancel this request. To cancel, log in and visit your Settings page.

If you did not request this, please contact support@jobezie.com immediately.

- The Jobezie Team
            """.strip(),
        )
    except Exception as e:
        logger.warning(f"Deletion email failed for {user.email}: {e}")


def _send_deletion_complete_email(email: str):
    """Final notice: account has been permanently deleted."""
    try:
        from app.services.email_service import EmailService

        EmailService.send_email(
            to_email=email,
            subject="Jobezie - Account Deleted",
            content="""
Your Jobezie account has been permanently deleted. All associated data has been removed from our systems.

If you have any questions, please contact support@jobezie.com.

- The Jobezie Team
            """.strip(),
        )
    except Exception as e:
        logger.warning(f"Deletion complete email failed for {email}: {e}")


def _send_export_ready_email(user, download_token: str):
    """Send download link for completed data export."""
    try:
        from app.services.email_service import EmailService

        frontend_url = os.environ.get("FRONTEND_URL", "https://jobezie.com")
        download_url = f"{frontend_url}/api/profile/export/download/{download_token}"
        EmailService.send_email(
            to_email=user.email,
            subject="Jobezie - Your Data Export is Ready",
            content=f"""
Hi {user.first_name or user.email},

Your Jobezie data export is ready for download.

Download your data: {download_url}

This link will expire in {EXPORT_EXPIRY_DAYS} days. If you need a new export after that, you can request one from your Settings page.

- The Jobezie Team
            """.strip(),
        )
    except Exception as e:
        logger.warning(f"Export email failed for {user.email}: {e}")
