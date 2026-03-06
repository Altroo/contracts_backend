import logging

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CompanyConfig
from .serializers import CompanyConfigSerializer

logger = logging.getLogger(__name__)


class CompanyConfigListView(APIView):
    """GET all company configurations (read-only)."""

    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def get(request, *args, **kwargs):
        configs = CompanyConfig.objects.all().order_by("id")
        serializer = CompanyConfigSerializer(configs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
