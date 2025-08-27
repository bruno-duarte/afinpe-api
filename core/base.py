from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response

class BaseModelViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = "__all__"
    ordering_fields = "__all__"

class OptionalPaginationViewSet(BaseModelViewSet):
    """
    ViewSet que retorna todos os registros se 'page' não estiver na query string,
    caso contrário aplica a paginação configurada.
    """
    def list(self, request, *args, **kwargs):
        if 'page' not in request.query_params:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        return super().list(request, *args, **kwargs)