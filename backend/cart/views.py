from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from products.models import ProductVariant

from .models import Cart, CartItem
from .serializers import CartSerializer


def get_or_create_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


def parse_quantity(value):
    try:
        quantity = int(value)
    except (TypeError, ValueError):
        return None
    return quantity if quantity > 0 else None


class CartView(APIView):
    """GET the current user's cart."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cart = get_or_create_cart(request.user)
        return Response(CartSerializer(cart).data)


class CartItemView(APIView):
    """POST to add an item, PATCH to update quantity, DELETE to remove."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        cart = get_or_create_cart(request.user)
        variant_id = request.data.get("variant")
        quantity = parse_quantity(request.data.get("quantity", 1))
        if quantity is None:
            return Response(
                {"detail": "Quantity must be a positive whole number."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        variant = (
            ProductVariant.objects.select_related("product")
            .filter(id=variant_id, product__is_active=True)
            .first()
        )
        if not variant:
            return Response({"detail": "Variant not found."}, status=status.HTTP_404_NOT_FOUND)
        if variant.product.is_portfolio_only:
            return Response(
                {"detail": "This piece is portfolio-only and cannot be purchased."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        existing = cart.items.filter(variant=variant).first()
        new_quantity = quantity + (existing.quantity if existing else 0)
        if new_quantity > variant.stock_quantity:
            return Response(
                {"detail": "Not enough stock available."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        item, created = CartItem.objects.get_or_create(
            cart=cart, variant=variant, defaults={"quantity": quantity}
        )
        if not created:
            item.quantity = new_quantity
            item.save(update_fields=["quantity"])
        return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)

    def patch(self, request, item_id=None):
        cart = get_or_create_cart(request.user)
        item = cart.items.select_related("variant").filter(id=item_id).first()
        if not item:
            return Response({"detail": "Item not in cart."}, status=status.HTTP_404_NOT_FOUND)

        quantity = parse_quantity(request.data.get("quantity", item.quantity))
        if quantity is None:
            return Response(
                {"detail": "Quantity must be a positive whole number."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if quantity > item.variant.stock_quantity:
            return Response(
                {"detail": "Not enough stock available."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        item.quantity = quantity
        item.save(update_fields=["quantity"])
        return Response(CartSerializer(cart).data)

    def delete(self, request, item_id=None):
        cart = get_or_create_cart(request.user)
        cart.items.filter(id=item_id).delete()
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)
