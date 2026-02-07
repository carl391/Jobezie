"""
Stripe Subscription Service

Handles Stripe payment integration for subscription management.
"""

import os
from datetime import datetime
from typing import Dict

import stripe
from flask import current_app

from app.extensions import db
from app.models.user import SubscriptionTier, User
from app.services.email_service import EmailService


class StripeService:
    """
    Service for Stripe subscription management.

    Handles customer creation, subscription lifecycle, and webhook processing.
    """

    # Subscription tier to Stripe Price ID mapping
    PRICE_IDS = {
        SubscriptionTier.BASIC.value: None,  # Free tier
        SubscriptionTier.PRO.value: os.getenv("STRIPE_PRICE_PRO"),
        SubscriptionTier.EXPERT.value: os.getenv("STRIPE_PRICE_EXPERT"),
        SubscriptionTier.CAREER_KEEPER.value: os.getenv("STRIPE_PRICE_CAREER_KEEPER"),
    }

    # Monthly prices (cents) - Per business plan pricing
    TIER_PRICES = {
        SubscriptionTier.BASIC.value: 0,
        SubscriptionTier.PRO.value: 1900,  # $19.00
        SubscriptionTier.EXPERT.value: 3900,  # $39.00
        SubscriptionTier.CAREER_KEEPER.value: 900,  # $9.00
    }

    @staticmethod
    def _get_stripe():
        """Initialize Stripe with API key."""
        stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
        return stripe

    @classmethod
    def create_customer(cls, user: User) -> Dict:
        """
        Create a Stripe customer for a user.

        Args:
            user: User model instance

        Returns:
            Dictionary with customer data
        """
        stripe = cls._get_stripe()

        try:
            customer = stripe.Customer.create(
                email=user.email,
                name=user.full_name,
                metadata={
                    "user_id": str(user.id),
                },
            )

            # Update user with Stripe customer ID
            user.stripe_customer_id = customer.id
            db.session.commit()

            return {
                "success": True,
                "customer_id": customer.id,
            }

        except stripe.error.StripeError as e:
            current_app.logger.error(f"Stripe customer creation error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
            }

    @classmethod
    def create_checkout_session(
        cls,
        user: User,
        tier: str,
        success_url: str,
        cancel_url: str,
    ) -> Dict:
        """
        Create a Stripe Checkout session for subscription.

        Args:
            user: User model instance
            tier: Target subscription tier
            success_url: URL to redirect on success
            cancel_url: URL to redirect on cancel

        Returns:
            Dictionary with checkout session URL
        """
        stripe = cls._get_stripe()

        # Create customer if not exists
        if not user.stripe_customer_id:
            result = cls.create_customer(user)
            if not result["success"]:
                return result

        price_id = cls.PRICE_IDS.get(tier)
        if not price_id:
            return {
                "success": False,
                "error": f"Invalid tier or price not configured: {tier}",
            }

        try:
            session = stripe.checkout.Session.create(
                customer=user.stripe_customer_id,
                payment_method_types=["card"],
                line_items=[
                    {
                        "price": price_id,
                        "quantity": 1,
                    }
                ],
                mode="subscription",
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    "user_id": str(user.id),
                    "tier": tier,
                },
            )

            return {
                "success": True,
                "checkout_url": session.url,
                "session_id": session.id,
            }

        except stripe.error.StripeError as e:
            current_app.logger.error(f"Stripe checkout error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
            }

    @classmethod
    def create_portal_session(cls, user: User, return_url: str) -> Dict:
        """
        Create a Stripe Customer Portal session.

        Args:
            user: User model instance
            return_url: URL to return to after portal

        Returns:
            Dictionary with portal session URL
        """
        stripe = cls._get_stripe()

        if not user.stripe_customer_id:
            return {
                "success": False,
                "error": "No Stripe customer found",
            }

        try:
            session = stripe.billing_portal.Session.create(
                customer=user.stripe_customer_id,
                return_url=return_url,
            )

            return {
                "success": True,
                "portal_url": session.url,
            }

        except stripe.error.StripeError as e:
            current_app.logger.error(f"Stripe portal error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
            }

    @classmethod
    def cancel_subscription(cls, user: User) -> Dict:
        """
        Cancel a user's subscription.

        Args:
            user: User model instance

        Returns:
            Dictionary with result
        """
        stripe = cls._get_stripe()

        if not user.stripe_subscription_id:
            return {
                "success": False,
                "error": "No active subscription",
            }

        try:
            # Cancel at period end (user keeps access until end of billing cycle)
            subscription = stripe.Subscription.modify(
                user.stripe_subscription_id,
                cancel_at_period_end=True,
            )

            return {
                "success": True,
                "message": "Subscription will be cancelled at end of billing period",
                "cancels_at": datetime.fromtimestamp(subscription.current_period_end).isoformat(),
            }

        except stripe.error.StripeError as e:
            current_app.logger.error(f"Stripe cancellation error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
            }

    @classmethod
    def reactivate_subscription(cls, user: User) -> Dict:
        """
        Reactivate a cancelled subscription.

        Args:
            user: User model instance

        Returns:
            Dictionary with result
        """
        stripe = cls._get_stripe()

        if not user.stripe_subscription_id:
            return {
                "success": False,
                "error": "No subscription found",
            }

        try:
            stripe.Subscription.modify(
                user.stripe_subscription_id,
                cancel_at_period_end=False,
            )

            return {
                "success": True,
                "message": "Subscription reactivated",
            }

        except stripe.error.StripeError as e:
            current_app.logger.error(f"Stripe reactivation error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
            }

    @classmethod
    def get_subscription_status(cls, user: User) -> Dict:
        """
        Get current subscription status.

        Args:
            user: User model instance

        Returns:
            Subscription status details
        """
        stripe = cls._get_stripe()

        if not user.stripe_subscription_id:
            return {
                "tier": user.subscription_tier,
                "status": (
                    "none" if user.subscription_tier == SubscriptionTier.BASIC.value else "unknown"
                ),
                "active": user.subscription_tier != SubscriptionTier.BASIC.value,
            }

        try:
            subscription = stripe.Subscription.retrieve(user.stripe_subscription_id)

            return {
                "tier": user.subscription_tier,
                "status": subscription.status,
                "active": subscription.status == "active",
                "current_period_end": datetime.fromtimestamp(
                    subscription.current_period_end
                ).isoformat(),
                "cancel_at_period_end": subscription.cancel_at_period_end,
            }

        except stripe.error.StripeError as e:
            current_app.logger.error(f"Stripe status error: {str(e)}")
            return {
                "tier": user.subscription_tier,
                "status": "error",
                "error": str(e),
            }

    @classmethod
    def handle_webhook(cls, payload: bytes, sig_header: str) -> Dict:
        """
        Handle Stripe webhook events.

        Args:
            payload: Raw webhook payload
            sig_header: Stripe signature header

        Returns:
            Processing result
        """
        stripe = cls._get_stripe()
        webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        except ValueError:
            return {"success": False, "error": "Invalid payload"}
        except stripe.error.SignatureVerificationError:
            return {"success": False, "error": "Invalid signature"}

        # Handle the event
        event_type = event["type"]
        data = event["data"]["object"]

        if event_type == "checkout.session.completed":
            return cls._handle_checkout_completed(data)

        elif event_type == "customer.subscription.updated":
            return cls._handle_subscription_updated(data)

        elif event_type == "customer.subscription.deleted":
            return cls._handle_subscription_deleted(data)

        elif event_type == "invoice.payment_failed":
            return cls._handle_payment_failed(data)

        return {"success": True, "message": f"Unhandled event: {event_type}"}

    @classmethod
    def _handle_checkout_completed(cls, session: Dict) -> Dict:
        """Handle successful checkout session."""
        user_id = session.get("metadata", {}).get("user_id")
        tier = session.get("metadata", {}).get("tier")
        subscription_id = session.get("subscription")

        if not user_id:
            return {"success": False, "error": "No user_id in metadata"}

        user = User.query.get(user_id)
        if not user:
            return {"success": False, "error": "User not found"}

        # Update user subscription
        user.subscription_tier = tier
        user.stripe_subscription_id = subscription_id
        db.session.commit()

        current_app.logger.info(f"User {user_id} subscribed to {tier}")

        # Send subscription confirmation email
        try:
            tier_features = cls.get_tier_info()["tiers"]
            features = next(
                (t["features"] for t in tier_features if t["id"] == tier),
                []
            )
            EmailService.send_subscription_confirmed_email(user, tier, features)
        except Exception as e:
            current_app.logger.error(f"Failed to send subscription email: {e}")

        return {"success": True, "message": "Subscription activated"}

    @classmethod
    def _handle_subscription_updated(cls, subscription: Dict) -> Dict:
        """Handle subscription updates."""
        customer_id = subscription.get("customer")
        status = subscription.get("status")

        user = User.query.filter_by(stripe_customer_id=customer_id).first()
        if not user:
            return {"success": False, "error": "User not found"}

        # Update subscription expiry
        if status == "active":
            user.subscription_expires_at = datetime.fromtimestamp(
                subscription.get("current_period_end", 0)
            )
        db.session.commit()

        return {"success": True, "message": "Subscription updated"}

    @classmethod
    def _handle_subscription_deleted(cls, subscription: Dict) -> Dict:
        """Handle subscription cancellation/deletion."""
        customer_id = subscription.get("customer")

        user = User.query.filter_by(stripe_customer_id=customer_id).first()
        if not user:
            return {"success": False, "error": "User not found"}

        # Downgrade to basic
        previous_tier = user.subscription_tier
        user.subscription_tier = SubscriptionTier.BASIC.value
        user.stripe_subscription_id = None
        user.subscription_expires_at = None
        db.session.commit()

        current_app.logger.info(f"User {user.id} subscription cancelled")

        # Send subscription cancelled email
        try:
            EmailService.send_subscription_cancelled_email(user, datetime.now())
        except Exception as e:
            current_app.logger.error(f"Failed to send cancellation email: {e}")

        return {"success": True, "message": "Subscription cancelled"}

    @classmethod
    def _handle_payment_failed(cls, invoice: Dict) -> Dict:
        """Handle failed payment."""
        customer_id = invoice.get("customer")

        user = User.query.filter_by(stripe_customer_id=customer_id).first()
        if not user:
            return {"success": False, "error": "User not found"}

        current_app.logger.warning(f"Payment failed for user {user.id}")

        # Send payment failed notification email
        try:
            EmailService.send_payment_failed_email(user)
        except Exception as e:
            current_app.logger.error(f"Failed to send payment failure email: {e}")

        return {"success": True, "message": "Payment failure recorded"}

    @classmethod
    def get_tier_info(cls) -> Dict:
        """Get information about available subscription tiers."""
        return {
            "tiers": [
                {
                    "id": SubscriptionTier.BASIC.value,
                    "name": "Basic",
                    "price": 0,
                    "price_dollars": 0,
                    "price_display": "Free",
                    "features": [
                        "5 recruiters",
                        "2 tailored resumes/month",
                        "10 AI messages/month",
                        "Basic ATS scoring",
                    ],
                },
                {
                    "id": SubscriptionTier.PRO.value,
                    "name": "Pro",
                    "price": cls.TIER_PRICES[SubscriptionTier.PRO.value],
                    "price_dollars": cls.TIER_PRICES[SubscriptionTier.PRO.value] / 100,
                    "price_display": "$19/month",
                    "features": [
                        "50 recruiters",
                        "10 tailored resumes/month",
                        "100 AI messages/month",
                        "Advanced ATS scoring",
                        "Interview prep",
                        "Priority support",
                    ],
                },
                {
                    "id": SubscriptionTier.EXPERT.value,
                    "name": "Expert",
                    "price": cls.TIER_PRICES[SubscriptionTier.EXPERT.value],
                    "price_dollars": cls.TIER_PRICES[SubscriptionTier.EXPERT.value] / 100,
                    "price_display": "$39/month",
                    "features": [
                        "Unlimited recruiters",
                        "Unlimited tailored resumes",
                        "Unlimited AI messages",
                        "All features",
                        "Dedicated support",
                        "Custom integrations",
                    ],
                },
                {
                    "id": SubscriptionTier.CAREER_KEEPER.value,
                    "name": "Career Keeper",
                    "price": cls.TIER_PRICES[SubscriptionTier.CAREER_KEEPER.value],
                    "price_dollars": cls.TIER_PRICES[SubscriptionTier.CAREER_KEEPER.value] / 100,
                    "price_display": "$9/month",
                    "features": [
                        "Maintain your network",
                        "5 recruiters",
                        "1 tailored resume/month",
                        "10 AI messages/month",
                        "Quarterly check-ins",
                    ],
                    "description": "For passive job seekers who want to stay ready",
                },
            ],
        }
