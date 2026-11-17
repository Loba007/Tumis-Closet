from rest_framework import serializers

from categories.serializers import CategorySerializer

from .models import Product, ProductImage, ProductVariant


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image", "alt_text", "is_primary", "order"]


class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ["id", "size", "color", "stock_quantity", "variant_sku"]


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for catalog grids."""

    primary_image = serializers.SerializerMethodField()
    category_name = serializers.CharField(source="category.name", read_only=True)
    in_stock = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id", "name", "slug", "price", "discount_price", "current_price",
            "category_name", "is_featured", "is_portfolio_only", "in_stock",
            "average_rating", "primary_image",
        ]

    def get_primary_image(self, obj):
        images = list(obj.images.all())
        primary = next((image for image in images if image.is_primary), None)
        primary = primary or (images[0] if images else None)
        if not primary:
            return None
        request = self.context.get("request")
        url = primary.image.url
        return request.build_absolute_uri(url) if request else url

    def get_in_stock(self, obj):
        if hasattr(obj, "_in_stock"):
            return obj._in_stock
        return obj.in_stock

    def get_average_rating(self, obj):
        if hasattr(obj, "_average_rating"):
            return round(obj._average_rating or 0, 1)
        return obj.average_rating


class ProductDetailSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)

    def get_category(self, obj):
        if not obj.category:
            return None
        return CategorySerializer(obj.category, context=self.context).data

    class Meta:
        model = Product
        fields = [
            "id", "name", "slug", "description", "sku", "category",
            "price", "discount_price", "current_price", "is_portfolio_only",
            "is_featured", "is_active", "in_stock", "average_rating",
            "images", "variants", "created_at", "updated_at",
        ]


class ProductWriteSerializer(serializers.ModelSerializer):
    """Used by the admin dashboard to create/update products."""

    class Meta:
        model = Product
        fields = [
            "id", "name", "description", "sku", "category", "price",
            "discount_price", "is_portfolio_only", "is_featured", "is_active",
        ]

    def validate(self, attrs):
        price = attrs.get("price", getattr(self.instance, "price", None))
        discount = attrs.get("discount_price", getattr(self.instance, "discount_price", None))
        if price is not None and price < 0:
            raise serializers.ValidationError({"price": "Price cannot be negative."})
        if discount is not None:
            if discount < 0:
                raise serializers.ValidationError(
                    {"discount_price": "Discount price cannot be negative."}
                )
            if price is not None and discount > price:
                raise serializers.ValidationError(
                    {"discount_price": "Discount price cannot exceed the regular price."}
                )
        return attrs
