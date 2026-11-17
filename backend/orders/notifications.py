from django.conf import settings
from django.core.mail import send_mail


def send_order_confirmation(order):
    """Email the customer (and studio, when configured) a simple receipt."""
    if not order.user.email:
        return
    item_lines = [
        f"{item.quantity} x {item.product_name} ({item.size or 'One size'}) — ₦{item.subtotal:,.2f}"
        for item in order.items.all()
    ]
    body = "\n".join(
        [
            f"Thank you for your order, {order.shipping_full_name}.",
            "",
            f"Order: {order.order_number}",
            f"Status: {order.get_status_display()}",
            *item_lines,
            "",
            f"Subtotal: ₦{order.subtotal:,.2f}",
            f"Shipping: ₦{order.shipping_fee:,.2f}",
            f"Total: ₦{order.total_amount:,.2f}",
            "",
            "We will notify you when your piece is on its way.",
            "— Tunmis Closet",
        ]
    )
    recipients = [order.user.email]
    studio_email = getattr(settings, "CONTACT_EMAIL", "")
    if studio_email:
        recipients.append(studio_email)
    send_mail(
        subject=f"Order {order.order_number} received — Tunmis Closet",
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipients,
        fail_silently=False,
    )
