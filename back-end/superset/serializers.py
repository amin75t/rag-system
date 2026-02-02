# back-end/superset/serializers.py

from rest_framework import serializers
from .models import EmbeddedDashboard, GuestToken


class EmbeddedDashboardSerializer(serializers.ModelSerializer):
    """
    Serializer for EmbeddedDashboard model.

    We expose:
    - dashboard_uuid: the UUID from Superset Embed panel (REQUIRED for embedding)
    - superset_dashboard_id: numeric Superset dashboard id (optional, for metadata APIs)
    """

    class Meta:
        model = EmbeddedDashboard
        fields = [
            "id",
            "name",
            "superset_dashboard_id",
            "dashboard_uuid",
            "domain",
            "allowed_roles",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class GuestTokenSerializer(serializers.ModelSerializer):
    """Serializer for GuestToken model (mostly for debugging/auditing)."""

    dashboard_name = serializers.CharField(source="dashboard.name", read_only=True)

    class Meta:
        model = GuestToken
        fields = ["id", "token", "dashboard", "dashboard_name", "user", "expires_at", "created_at"]
        read_only_fields = ["id", "token", "created_at"]


class GuestTokenRequestSerializer(serializers.Serializer):
    """
    Request serializer for issuing a Superset Guest Token.

    IMPORTANT security note:
    - We DO NOT accept user_id from the client, because the app has login.
      The backend must use request.user to prevent impersonation.
    """

    # Superset embedded UUID (string UUID) - this is what Superset expects in guest_token "resources"
    dashboard_uuid = serializers.UUIDField(required=True)

    # Optional advanced inputs (usually not needed for first version)
    resources = serializers.JSONField(required=False, default=None)
    rls = serializers.JSONField(required=False, default=None)

    def validate_dashboard_uuid(self, value):
        """
        Ensure the requested dashboard is in our allow-list (EmbeddedDashboard table).
        This prevents embedding any random Superset dashboard UUID.
        """
        if not EmbeddedDashboard.objects.filter(dashboard_uuid=value).exists():
            raise serializers.ValidationError("Dashboard not found or not configured for embedding.")
        return value
