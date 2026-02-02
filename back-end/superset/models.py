# back-end/superset/models.py

from django.db import models


class EmbeddedDashboard(models.Model):
    """
    Stores dashboards that are allowed to be embedded by our application.

    IMPORTANT:
    - Superset has a numeric dashboard ID (useful for some Superset API endpoints).
    - Superset Embedded mode uses a UUID for embedding / guest tokens (from Superset "Embed" panel).
    We store BOTH to avoid confusion.
    """

    name = models.CharField(max_length=255)

    # Numeric ID in Superset (optional, useful for /api/v1/dashboard/<id>)
    superset_dashboard_id = models.IntegerField(null=True, blank=True)

    # UUID used for Superset Embedded dashboard / guest token (REQUIRED for embedding)
    dashboard_uuid = models.UUIDField(unique=True)

    # Superset domain (where Superset is reachable from the browser)
    domain = models.CharField(max_length=255)

    # Optional allow-list of roles from your app (you can enforce in views if needed)
    allowed_roles = models.JSONField(default=list)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "superset_embedded_dashboards"
        verbose_name = "Embedded Dashboard"
        verbose_name_plural = "Embedded Dashboards"

    def __str__(self):
        return self.name


class GuestToken(models.Model):
    """
    Optional: stores issued guest tokens for auditing/debugging.
    You do NOT strictly need to store guest tokens in DB for embedding to work.
    """

    token = models.CharField(max_length=512, unique=True)  # JWT can be longer than 255
    dashboard = models.ForeignKey(EmbeddedDashboard, on_delete=models.CASCADE)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, null=True, blank=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "superset_guest_tokens"
        verbose_name = "Guest Token"
        verbose_name_plural = "Guest Tokens"

    def __str__(self):
        return f"Token for {self.dashboard.name}"
