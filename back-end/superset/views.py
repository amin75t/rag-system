# back-end/superset/views.py

from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from django.shortcuts import get_object_or_404

from .models import EmbeddedDashboard, GuestToken
from .serializers import (
    EmbeddedDashboardSerializer,
    GuestTokenSerializer,
    GuestTokenRequestSerializer,
)
from .services import SupersetService, SupersetServiceError  # make sure your services.py exports SupersetServiceError


class EmbeddedDashboardList(APIView):
    """
    List/Create dashboards that are allowed to be embedded by the app.
    This is an internal allow-list; it is NOT Superset's own dashboard listing.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        dashboards = EmbeddedDashboard.objects.all()
        serializer = EmbeddedDashboardSerializer(dashboards, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = EmbeddedDashboardSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmbeddedDashboardDetail(APIView):
    """Retrieve/Update/Delete an embeddable dashboard record."""
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(EmbeddedDashboard, pk=pk)

    def get(self, request, pk):
        dashboard = self.get_object(pk)
        serializer = EmbeddedDashboardSerializer(dashboard)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        dashboard = self.get_object(pk)
        serializer = EmbeddedDashboardSerializer(dashboard, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        dashboard = self.get_object(pk)
        dashboard.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def generate_guest_token(request):
    """
    Generate a Superset Guest Token for embedding.

    Security:
    - App has login -> only authenticated users can request a guest token.
    - Never accept user_id from client (prevents impersonation).
    - Only dashboards in our allow-list (EmbeddedDashboard table) can be embedded.
    """
    serializer = GuestTokenRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    dashboard_uuid = serializer.validated_data["dashboard_uuid"]
    resources = serializer.validated_data.get("resources")
    rls = serializer.validated_data.get("rls")

    # Enforce allow-list (already validated in serializer, but we fetch the dashboard record here too)
    dashboard = get_object_or_404(EmbeddedDashboard, dashboard_uuid=dashboard_uuid)

    # Use authenticated user from Django session/JWT/etc.
    user = request.user

    try:
        superset_service = SupersetService()
        guest_token = superset_service.generate_guest_token(
            dashboard_uuid=str(dashboard_uuid),  # make sure it's a string UUID for Superset payload
            user=user,
            resources=resources,
            rls=rls,
        )

        # React embedded SDK only needs the guest token + dashboard UUID + superset domain
        return Response(
            {
                "token": guest_token,
                "dashboard_uuid": str(dashboard_uuid),
                "superset_domain": dashboard.domain,  # keep as stored (e.g. https://superset.example.com)
            },
            status=status.HTTP_200_OK,
        )

    except SupersetServiceError as e:
        return Response({"error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)
    except Exception:
        return Response({"error": "Failed to generate guest token"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def validate_guest_token(request, token):
    """
    Validate a guest token using local DB record (optional debugging endpoint).
    Note: This does not validate with Superset; it checks our stored expires_at.
    """
    superset_service = SupersetService()
    is_valid = superset_service.is_token_valid(token)

    if not is_valid:
        return Response({"valid": False}, status=status.HTTP_200_OK)

    guest_token = get_object_or_404(GuestToken, token=token)
    serializer = GuestTokenSerializer(guest_token)
    return Response({"valid": True, "token_info": serializer.data}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def dashboard_info(request, superset_dashboard_id: int):
    """
    Optional: Fetch dashboard metadata from Superset.

    WARNING:
    Superset's /api/v1/dashboard/<id> typically expects numeric dashboard ID (not UUID).
    So we keep this endpoint separate from embedding UUID.
    """
    try:
        superset_service = SupersetService()
        info = superset_service.get_dashboard_info(superset_dashboard_id)
        return Response(info, status=status.HTTP_200_OK)
    except SupersetServiceError as e:
        return Response({"error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)
    except Exception:
        return Response({"error": "Failed to get dashboard info"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def sync_embedded_dashboards(request):
    """
    Admin helper: sync allow-listed dashboards from settings into DB.

    Expected settings format example:
    SUPERSET_CONFIG = {
      "EMBEDDABLE_DASHBOARDS": {
        "sales_dashboard": {
          "superset_dashboard_id": 12,
          "dashboard_uuid": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
          "domain": "https://superset.example.com",
          "allowed_roles": ["admin", "manager"]
        }
      }
    }
    """
    from django.conf import settings

    config_dashboards = settings.SUPERSET_CONFIG.get("EMBEDDABLE_DASHBOARDS", {})

    for dashboard_key, dashboard_config in config_dashboards.items():
        EmbeddedDashboard.objects.update_or_create(
            dashboard_uuid=dashboard_config["dashboard_uuid"],
            defaults={
                "name": dashboard_key.replace("_", " ").title(),
                "superset_dashboard_id": dashboard_config.get("superset_dashboard_id"),
                "domain": dashboard_config["domain"],
                "allowed_roles": dashboard_config.get("allowed_roles", []),
            },
        )

    return Response(
        {"message": "Embedded dashboards synced successfully", "count": len(config_dashboards)},
        status=status.HTTP_200_OK,
    )
