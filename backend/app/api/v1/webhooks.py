"""Webhook endpoints for external services."""

import logging
from typing import Any

from fastapi import APIRouter, Header, HTTPException, Request, status

from app.api.deps import AsyncSessionDep, SettingsDep

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/stripe", status_code=status.HTTP_200_OK)
async def stripe_webhook(
    request: Request,
    db: AsyncSessionDep,
    settings: SettingsDep,
    stripe_signature: str | None = Header(None, alias="Stripe-Signature"),
) -> dict[str, str]:
    """
    Handle Stripe webhook events.

    This endpoint receives webhook events from Stripe for subscription changes,
    payment events, etc.

    Supported events (to be implemented):
    - checkout.session.completed: Customer completed checkout
    - invoice.paid: Invoice was paid successfully
    - invoice.payment_failed: Payment failed
    - customer.subscription.updated: Subscription was modified
    - customer.subscription.deleted: Subscription was canceled

    For now, this is a stub that logs the event and returns 200 OK.
    """
    # Get raw body for signature verification
    body = await request.body()

    # Log that we received a webhook (without sensitive details)
    logger.info("Stripe webhook received (not implemented)")

    # In production, verify the signature:
    # if settings.STRIPE_WEBHOOK_SECRET:
    #     try:
    #         event = stripe.Webhook.construct_event(
    #             body,
    #             stripe_signature,
    #             settings.STRIPE_WEBHOOK_SECRET,
    #         )
    #     except ValueError:
    #         raise HTTPException(status_code=400, detail="Invalid payload")
    #     except stripe.error.SignatureVerificationError:
    #         raise HTTPException(status_code=400, detail="Invalid signature")

    # Parse the event (for logging purposes only in stub)
    try:
        import json
        event_data = json.loads(body)
        event_type = event_data.get("type", "unknown")
        logger.info(f"Stripe webhook event type: {event_type}")
    except Exception:
        event_type = "unknown"

    # Stub handlers for different event types
    # These will be implemented when Stripe is integrated
    handlers = {
        "checkout.session.completed": _handle_checkout_completed,
        "invoice.paid": _handle_invoice_paid,
        "invoice.payment_failed": _handle_invoice_payment_failed,
        "customer.subscription.updated": _handle_subscription_updated,
        "customer.subscription.deleted": _handle_subscription_deleted,
    }

    handler = handlers.get(event_type)
    if handler:
        logger.info(f"Would handle {event_type} (not implemented)")
        # In production: await handler(db, event_data)

    return {"status": "received"}


async def _handle_checkout_completed(db: AsyncSessionDep, event_data: dict[str, Any]) -> None:
    """
    Handle checkout.session.completed event.

    This is called when a customer completes the Stripe Checkout flow.
    We should:
    1. Extract the subscription ID from the session
    2. Update our Subscription record with the Stripe IDs
    3. Update the organization's tier
    4. Log a billing event
    """
    logger.info("checkout.session.completed handler (stub)")
    # session = event_data.get("data", {}).get("object", {})
    # customer_id = session.get("customer")
    # subscription_id = session.get("subscription")
    # metadata = session.get("metadata", {})
    # org_id = metadata.get("organization_id")
    pass


async def _handle_invoice_paid(db: AsyncSessionDep, event_data: dict[str, Any]) -> None:
    """
    Handle invoice.paid event.

    This is called when a recurring payment succeeds.
    We should:
    1. Update the subscription period dates
    2. Log a successful payment event
    3. Reset monthly usage if it's a new period
    """
    logger.info("invoice.paid handler (stub)")
    # invoice = event_data.get("data", {}).get("object", {})
    # subscription_id = invoice.get("subscription")
    pass


async def _handle_invoice_payment_failed(db: AsyncSessionDep, event_data: dict[str, Any]) -> None:
    """
    Handle invoice.payment_failed event.

    This is called when a payment fails.
    We should:
    1. Update subscription status to past_due
    2. Log a payment failed event
    3. Optionally notify the customer
    """
    logger.info("invoice.payment_failed handler (stub)")
    # invoice = event_data.get("data", {}).get("object", {})
    # subscription_id = invoice.get("subscription")
    pass


async def _handle_subscription_updated(db: AsyncSessionDep, event_data: dict[str, Any]) -> None:
    """
    Handle customer.subscription.updated event.

    This is called when a subscription is modified (e.g., plan change).
    We should:
    1. Update our Subscription record
    2. Update the organization's tier if changed
    3. Log the change event
    """
    logger.info("customer.subscription.updated handler (stub)")
    # subscription = event_data.get("data", {}).get("object", {})
    # subscription_id = subscription.get("id")
    # status = subscription.get("status")
    # price_id = subscription.get("items", {}).get("data", [{}])[0].get("price", {}).get("id")
    pass


async def _handle_subscription_deleted(db: AsyncSessionDep, event_data: dict[str, Any]) -> None:
    """
    Handle customer.subscription.deleted event.

    This is called when a subscription is canceled/deleted.
    We should:
    1. Mark subscription as canceled
    2. Downgrade organization to indie tier
    3. Log the cancellation event
    """
    logger.info("customer.subscription.deleted handler (stub)")
    # subscription = event_data.get("data", {}).get("object", {})
    # subscription_id = subscription.get("id")
    pass
