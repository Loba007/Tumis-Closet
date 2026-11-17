from django.db.models import Q
from rest_framework import permissions, viewsets

from .models import Review
from .serializers import ReviewSerializer


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user or request.user.is_staff


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        qs = Review.objects.all().select_related("user", "product")
        user = self.request.user
        if not (user.is_authenticated and user.is_staff):
            approved = Q(is_approved=True)
            if user.is_authenticated:
                approved |= Q(user=user)
            qs = qs.filter(approved)
        product_id = self.request.query_params.get("product")
        if product_id:
            qs = qs.filter(product_id=product_id)
        return qs
