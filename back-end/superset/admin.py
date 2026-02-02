# back-end/superset/admin.py

from django.contrib import admin
from .models import EmbeddedDashboard, GuestToken


@admin.register(EmbeddedDashboard)
class EmbeddedDashboardAdmin(admin.ModelAdmin):
    """
    Admin view for managing dashboards that are allowed to be embedded.

    We show BOTH:
    - dashboard_uuid: required for Superset embedded SDK / guest tokens
    - superset_dashboard_id: optional numeric id (useful for Superset metadata endpoints)
    """

    list_display = [
        "name",
        "dashboard_uuid",
        "superset_dashboard_id",
        "domain",
        "created_at",
        "updated_at",
    ]
    list_filter = ["domain", "created_at"]
    search_fields = ["name", "domain", "dashboard_uuid"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        ("Dashboard Information", {
            "fields": ("name", "dashboard_uuid", "superset_dashboard_id", "domain")
        }),
        ("Access Control", {
            "fields": ("allowed_roles",)
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )


@admin.register(GuestToken)
class GuestTokenAdmin(admin.ModelAdmin):
    """Admin view for issued guest tokens (optional auditing/debugging)."""

    list_display = ["dashboard", "user", "token_preview", "expires_at", "created_at"]
    list_filter = ["dashboard", "created_at", "expires_at"]
    search_fields = ["dashboard__name", "user__username"]
    readonly_fields = ["token", "created_at"]

    def token_preview(self, obj):
        """Show a safe preview of the token (first 20 characters)."""
        return obj.token[:20] + "..." if obj.token and len(obj.token) > 20 else (obj.token or "")

    token_preview.short_description = "Token Preview"

    fieldsets = (
        ("Token Information", {
            "fields": ("token", "dashboard", "user")
        }),
        ("Expiration", {
            "fields": ("expires_at",)
        }),
        ("Timestamps", {
            "fields": ("created_at",),
            "classes": ("collapse",),
        }),
    )
