from rest_framework import serializers

from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "id", "name", "slug", "description", "image",
            "parent", "is_active", "subcategories",
        ]

    def get_subcategories(self, obj):
        return CategorySerializer(
            obj.subcategories.filter(is_active=True), many=True, context=self.context
        ).data
