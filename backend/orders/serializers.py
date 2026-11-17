from rest_framework import serializers

from accounts.models import Address

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product_name", "size", "color", "quantity", "price_at_purchase", "subtotal"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "order_number", "status", "shipping_method", "shipping_full_name",
            "shipping_phone_number", "shipping_line1", "shipping_line2", "shipping_city",
            "shipping_state", "shipping_country", "subtotal", "shipping_fee", "total_amount",
            "refund_required", "refunded_at", "items", "created_at",
        ]
        read_only_fields = fields

    def to_representation(self, instance):
        data = super().to_representation(instance)
        payment = getattr(instance, "payment", None)
        data["payment_reference"] = getattr(payment, "reference", None)
        data["payment_status"] = getattr(payment, "status", None)
        return data


class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["status"]
        validators = []


class CheckoutSerializer(serializers.Serializer):
    """Accepts either an existing address id, or a fresh address inline."""

    address_id = serializers.IntegerField(required=False)
    full_name = serializers.CharField(required=False, max_length=150)
    phone_number = serializers.CharField(required=False, max_length=20)
    line1 = serializers.CharField(required=False, max_length=255)
    line2 = serializers.CharField(required=False, allow_blank=True, max_length=255)
    city = serializers.CharField(required=False, max_length=100)
    state = serializers.CharField(required=False, max_length=100)
    country = serializers.CharField(required=False, default="Nigeria", max_length=100)
    shipping_method = serializers.ChoiceField(
        choices=["delivery", "pickup"], required=False, default="delivery"
    )

    def validate(self, data):
        if data.get("address_id") or data.get("shipping_method") == "pickup":
            return data
        required = ["full_name", "phone_number", "line1", "city", "state"]
        missing = [field for field in required if not data.get(field)]
        if missing:
            raise serializers.ValidationError(
                {field: "This field is required when no address is selected." for field in missing}
            )
        return data

    def resolve_address(self, user):
        data = self.validated_data
        address = None
        if data.get("address_id"):
            address = Address.objects.filter(id=data["address_id"], user=user).first()
            if not address:
                raise serializers.ValidationError({"address_id": "Address not found."})

        if data.get("shipping_method") == "pickup":
            return {
                "shipping_full_name": (
                    data.get("full_name") or user.get_full_name() or user.username
                ),
                "shipping_phone_number": (
                    data.get("phone_number") or user.phone_number
                ),
                "shipping_line1": "Tunmis Closet Studio pickup",
                "shipping_line2": "Igbogbo, Ikorodu",
                "shipping_city": "Ikorodu",
                "shipping_state": "Lagos",
                "shipping_country": "Nigeria",
            }

        if address:
            return {
                "shipping_full_name": address.full_name,
                "shipping_phone_number": address.phone_number,
                "shipping_line1": address.line1,
                "shipping_line2": address.line2,
                "shipping_city": address.city,
                "shipping_state": address.state,
                "shipping_country": address.country,
            }
        return {
            "shipping_full_name": data["full_name"],
            "shipping_phone_number": data["phone_number"],
            "shipping_line1": data["line1"],
            "shipping_line2": data.get("line2", ""),
            "shipping_city": data["city"],
            "shipping_state": data["state"],
            "shipping_country": data.get("country", "Nigeria"),
        }


class ShippingQuoteSerializer(serializers.Serializer):
    state = serializers.CharField(required=False, allow_blank=True, max_length=100)
    city = serializers.CharField(required=False, allow_blank=True, max_length=100)
    shipping_method = serializers.ChoiceField(
        choices=["delivery", "pickup"], required=False, default="delivery"
    )

