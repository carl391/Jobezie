"""
Subscription Routes

Handles subscription management endpoints.
"""

import os

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.models.user import User
from app.services.stripe_service import StripeService

subscription_bp = Blueprint("subscription", __name__, url_prefix="/api/subscription")


@subscription_bp.route("/tiers", methods=["GET"])
def get_tiers():
    """
    Get available subscription tiers.

    Returns:
        200: List of subscription tiers with pricing
    """
    tiers = StripeService.get_tier_info()

    return jsonify({"success": True, "data": tiers}), 200


@subscription_bp.route("/status", methods=["GET"])
@jwt_required()
def get_status():
    """
    Get current subscription status.

    Returns:
        200: Current subscription status
        404: User not found
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return (
            jsonify({"success": False, "error": "not_found", "message": "User not found"}),
            404,
        )

    status = StripeService.get_subscription_status(user)

    return jsonify({"success": True, "data": status}), 200


@subscription_bp.route("/checkout", methods=["POST"])
@jwt_required()
def create_checkout():
    """
    Create a checkout session for subscription.

    Request Body:
        tier: Target subscription tier (required)
        success_url: Redirect URL on success (optional)
        cancel_url: Redirect URL on cancel (optional)

    Returns:
        200: Checkout session URL
        400: Missing tier or invalid tier
        404: User not found
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return (
            jsonify({"success": False, "error": "not_found", "message": "User not found"}),
            404,
        )

    data = request.get_json() or {}

    tier = data.get("tier")
    if not tier:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "validation_error",
                    "message": "Tier is required",
                }
            ),
            400,
        )

    base_url = os.getenv("FRONTEND_URL", "https://app.jobezie.com")
    success_url = data.get("success_url", f"{base_url}/subscription/success")
    cancel_url = data.get("cancel_url", f"{base_url}/subscription/cancel")

    result = StripeService.create_checkout_session(
        user=user,
        tier=tier,
        success_url=success_url,
        cancel_url=cancel_url,
    )

    if not result["success"]:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "checkout_error",
                    "message": result.get("error", "Failed to create checkout"),
                }
            ),
            400,
        )

    return (
        jsonify(
            {
                "success": True,
                "data": {
                    "checkout_url": result["checkout_url"],
                    "session_id": result["session_id"],
                },
            }
        ),
        200,
    )


@subscription_bp.route("/portal", methods=["POST"])
@jwt_required()
def create_portal():
    """
    Create a customer portal session for subscription management.

    Request Body:
        return_url: URL to return to after portal (optional)

    Returns:
        200: Portal session URL
        400: No Stripe customer
        404: User not found
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return (
            jsonify({"success": False, "error": "not_found", "message": "User not found"}),
            404,
        )

    data = request.get_json() or {}

    base_url = os.getenv("FRONTEND_URL", "https://app.jobezie.com")
    return_url = data.get("return_url", f"{base_url}/settings/billing")

    result = StripeService.create_portal_session(user, return_url)

    if not result["success"]:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "portal_error",
                    "message": result.get("error", "Failed to create portal session"),
                }
            ),
            400,
        )

    return (
        jsonify(
            {
                "success": True,
                "data": {
                    "portal_url": result["portal_url"],
                },
            }
        ),
        200,
    )


@subscription_bp.route("/cancel", methods=["POST"])
@jwt_required()
def cancel_subscription():
    """
    Cancel current subscription.

    Returns:
        200: Cancellation confirmed
        400: No active subscription
        404: User not found
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return (
            jsonify({"success": False, "error": "not_found", "message": "User not found"}),
            404,
        )

    result = StripeService.cancel_subscription(user)

    if not result["success"]:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "cancellation_error",
                    "message": result.get("error", "Failed to cancel subscription"),
                }
            ),
            400,
        )

    return (
        jsonify(
            {
                "success": True,
                "data": {
                    "message": result["message"],
                    "cancels_at": result.get("cancels_at"),
                },
            }
        ),
        200,
    )


@subscription_bp.route("/reactivate", methods=["POST"])
@jwt_required()
def reactivate_subscription():
    """
    Reactivate a cancelled subscription.

    Returns:
        200: Reactivation confirmed
        400: No subscription to reactivate
        404: User not found
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return (
            jsonify({"success": False, "error": "not_found", "message": "User not found"}),
            404,
        )

    result = StripeService.reactivate_subscription(user)

    if not result["success"]:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "reactivation_error",
                    "message": result.get("error", "Failed to reactivate subscription"),
                }
            ),
            400,
        )

    return (
        jsonify(
            {
                "success": True,
                "data": {
                    "message": result["message"],
                },
            }
        ),
        200,
    )


@subscription_bp.route("/webhook", methods=["POST"])
def handle_webhook():
    """
    Handle Stripe webhook events.

    Returns:
        200: Webhook processed
        400: Invalid webhook
    """
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature")

    if not sig_header:
        return jsonify({"success": False, "error": "Missing signature header"}), 400

    result = StripeService.handle_webhook(payload, sig_header)

    if not result["success"]:
        return jsonify(result), 400

    return jsonify(result), 200
