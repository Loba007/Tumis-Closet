from django.db.models import Avg, Exists, OuterRef, Prefetch, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Product, ProductImage, ProductVariant
from .serializers import (
    ProductDetailSerializer,
    ProductImageSerializer,
    ProductListSerializer,
    ProductVariantSerializer,
    ProductWriteSerializer,
)


class ProductViewSet(viewsets.ModelViewSet):
    """
    /api/products/                 -> catalog (excludes portfolio-only pieces by default)
    /api/products/?portfolio=true  -> portfolio gallery pieces
    /api/products/?category=slug   -> filter by category slug
    /api/products/?search=term     -> search name/description
    """

    queryset = Product.objects.filter(is_active=True).select_related("category").prefetch_related(
        "variants",
        Prefetch("images", queryset=ProductImage.objects.order_by("-is_primary", "order")),
    ).annotate(
        _average_rating=Avg("reviews__rating", filter=Q(reviews__is_approved=True)),
        _in_stock=Exists(
            ProductVariant.objects.filter(product=OuterRef("pk"), stock_quantity__gt=0)
        ),
    ).order_by("-created_at")
    lookup_field = "slug"
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category__slug", "is_featured"]
    search_fields = ["name", "description", "sku"]
    ordering_fields = ["price", "created_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        portfolio_param = self.request.query_params.get("portfolio")
        if portfolio_param == "true":
            return qs.filter(is_portfolio_only=True)
        if self.action == "list" and portfolio_param != "all":
            return qs.filter(is_portfolio_only=False)
        return qs

    def get_serializer_class(self):
        if self.action == "list":
            return ProductListSerializer
        if self.action in ["create", "update", "partial_update"]:
            return ProductWriteSerializer
        return ProductDetailSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def add_image(self, request, slug=None):
        product = self.get_object()
        serializer = ProductImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(product=product)
        return Response(serializer.data, status=201)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def add_variant(self, request, slug=None):
        product = self.get_object()
        serializer = ProductVariantSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(product=product)
        return Response(serializer.data, status=201)


class ProductImageViewSet(viewsets.ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [permissions.IsAdminUser]


class ProductVariantViewSet(viewsets.ModelViewSet):
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer
    permission_classes = [permissions.IsAdminUser]
