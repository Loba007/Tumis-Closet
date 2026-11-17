from rest_framework import serializers

from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id", "order", "reference", "amount", "status", "authorization_url",
            "refund_reference", "refunded_at", "created_at", "paid_at",
        ]
        read_only_fields = fields
