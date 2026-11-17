from rest_framework import serializers

from orders.models import OrderItem

from .models import Review

PAID_STATUSES = ("paid", "processing", "shipped", "delivered")


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.username", read_only=True)
    comment = serializers.CharField(required=False, allow_blank=True, max_length=2000)

    class Meta:
        model = Review
        fields = [
            "id", "product", "user", "user_name", "rating", "comment",
            "is_approved", "is_verified_purchase", "created_at",
        ]
        read_only_fields = ["user", "is_approved", "is_verified_purchase", "created_at"]

    def create(self, validated_data):
        user = self.context["request"].user
        product = validated_data["product"]
        validated_data["user"] = user
        validated_data["is_approved"] = user.is_staff
        validated_data["is_verified_purchase"] = OrderItem.objects.filter(
            order__user=user,
            order__status__in=PAID_STATUSES,
            variant__product=product,
        ).exists()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        user = self.context["request"].user
        product = validated_data.get("product", instance.product)

        if not user.is_staff:
            validated_data["is_approved"] = False
            if product != instance.product:
                validated_data["is_verified_purchase"] = OrderItem.objects.filter(
                    order__user=user,
                    order__status__in=PAID_STATUSES,
                    variant__product=product,
                ).exists()

        return super().update(instance, validated_data)
