"""Mock customer-support tools for Sunrise Outfitters.

These tools use in-memory fake data so the workshop agent needs no external
services or databases. They are intentionally simple but realistic enough to
produce interesting traces (tool calls, arguments, and results) in Arize.
"""

from __future__ import annotations

from langchain_core.tools import tool

# --- Fake backend data ------------------------------------------------------

_ORDERS: dict[str, dict] = {
    "A1001": {
        "status": "shipped",
        "item": "Trailblazer Rain Jacket (M, Forest Green)",
        "carrier": "DHL",
        "tracking": "DHL-SG-77123",
        "ordered_days_ago": 3,
        "delivered": False,
        "price_usd": 129.00,
    },
    "A1002": {
        "status": "delivered",
        "item": "Summit Hiking Boots (US 9)",
        "carrier": "SingPost",
        "tracking": "SP-99812",
        "ordered_days_ago": 20,
        "delivered": True,
        "price_usd": 159.00,
    },
    "A1003": {
        "status": "processing",
        "item": "Coastline Windbreaker (L, Navy)",
        "carrier": None,
        "tracking": None,
        "ordered_days_ago": 1,
        "delivered": False,
        "price_usd": 89.00,
    },
}

_FAQ: list[dict] = [
    {
        "keywords": ["shipping", "ship", "delivery", "deliver", "how long", "arrive"],
        "answer": (
            "Standard shipping within Singapore takes 2-4 business days. "
            "International orders take 7-14 business days. You receive a "
            "tracking number by email once your order ships."
        ),
    },
    {
        "keywords": ["return", "returns", "refund", "exchange", "money back"],
        "answer": (
            "You can return unworn items within 30 days of delivery for a full "
            "refund. Items must have original tags. Start a return from your "
            "account page or ask support to open one for you."
        ),
    },
    {
        "keywords": ["size", "sizing", "fit", "measurements", "chart"],
        "answer": (
            "Our jackets run true to size; boots run about half a size large. "
            "A full size chart is available on every product page under the "
            "'Size & Fit' tab."
        ),
    },
    {
        "keywords": ["payment", "pay", "card", "paynow", "installment"],
        "answer": (
            "We accept all major credit cards, PayNow, and Atome installments. "
            "Payment is charged when your order ships."
        ),
    },
]


@tool
def lookup_order(order_id: str) -> str:
    """Look up the current status and details of a customer order by its ID.

    Args:
        order_id: The order identifier, e.g. "A1001".
    """
    order = _ORDERS.get(order_id.strip().upper())
    if not order:
        return (
            f"No order found with ID '{order_id}'. Ask the customer to "
            "double-check the ID from their confirmation email."
        )
    parts = [
        f"Order {order_id.upper()}: {order['item']}",
        f"Status: {order['status']}",
        f"Placed: {order['ordered_days_ago']} day(s) ago",
        f"Price: ${order['price_usd']:.2f}",
    ]
    if order["tracking"]:
        parts.append(f"Carrier: {order['carrier']} (tracking {order['tracking']})")
    return ". ".join(parts) + "."


@tool
def check_refund_eligibility(order_id: str) -> str:
    """Check whether an order is eligible for a refund under the return policy.

    Policy: delivered items can be refunded within 30 days of the order date.
    Undelivered items can be cancelled for a full refund while still processing.

    Args:
        order_id: The order identifier, e.g. "A1002".
    """
    order = _ORDERS.get(order_id.strip().upper())
    if not order:
        return f"No order found with ID '{order_id}', so eligibility cannot be checked."

    if order["status"] == "processing":
        return (
            f"Order {order_id.upper()} is still processing and can be cancelled "
            "now for a full refund."
        )
    if order["delivered"]:
        if order["ordered_days_ago"] <= 30:
            return (
                f"Order {order_id.upper()} was delivered and is within the 30-day "
                "window, so it IS eligible for a full refund."
            )
        return (
            f"Order {order_id.upper()} was delivered more than 30 days ago, so it "
            "is NOT eligible for a standard refund. Offer store credit instead."
        )
    return (
        f"Order {order_id.upper()} has shipped but is not yet delivered. The "
        "customer can refuse delivery or return it within 30 days of arrival."
    )


@tool
def search_faq(query: str) -> str:
    """Search the help center / FAQ for shipping, returns, sizing, and payment info.

    Args:
        query: A natural-language question or keywords from the customer.
    """
    q = query.lower()
    for entry in _FAQ:
        if any(keyword in q for keyword in entry["keywords"]):
            return entry["answer"]
    return (
        "No exact FAQ match. General help: we ship in 2-4 business days locally, "
        "accept returns within 30 days, and our sizing runs true to size. For "
        "anything else, escalate to a human agent."
    )


@tool
def escalate_to_human(reason: str) -> str:
    """Escalate the conversation to a human support agent and open a ticket.

    Use this only when the customer is unhappy, the issue is complex, or the
    other tools cannot resolve the request.

    Args:
        reason: A short summary of why the issue needs a human.
    """
    ticket_id = f"TCK-{abs(hash(reason)) % 90000 + 10000}"
    return (
        f"Escalated to a human agent. Ticket {ticket_id} created with note: "
        f"'{reason}'. A specialist will reply by email within 24 hours."
    )


SUPPORT_TOOLS = [lookup_order, check_refund_eligibility, search_faq, escalate_to_human]
