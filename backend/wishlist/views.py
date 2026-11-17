from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from products.models import Product

from .models import Wishlist, WishlistItem
from .serializers import WishlistItemSerializer


class WishlistView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        items = wishlist.items.select_related("product").prefetch_related("product__images")
        return Response(
            WishlistItemSerializer(items, many=True, context={"request": request}).data
        )

    def post(self, request):
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        product = Product.objects.filter(
            id=request.data.get("product"), is_active=True
        ).first()
        if not product:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
        item, created = WishlistItem.objects.get_or_create(wishlist=wishlist, product=product)
        return Response(
            WishlistItemSerializer(item, context={"request": request}).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    def delete(self, request):
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        wishlist.items.filter(product_id=request.data.get("product")).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
