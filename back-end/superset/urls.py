# back-end/superset/urls.py

from django.urls import path
from . import views

app_name = "superset"

urlpatterns = [
    # Allow-list CRUD for embeddable dashboards (internal to your app)
    path("dashboards/", views.EmbeddedDashboardList.as_view(), name="dashboard-list"),
    path("dashboards/<int:pk>/", views.EmbeddedDashboardDetail.as_view(), name="dashboard-detail"),

    # Guest token issuance for Superset Embedded SDK (authenticated users only)
    path("guest-token/", views.generate_guest_token, name="generate-guest-token"),
    path("guest-token/<str:token>/validate/", views.validate_guest_token, name="validate-guest-token"),

    # Optional: fetch Superset dashboard metadata (numeric Superset dashboard id)
    path("dashboard/<int:superset_dashboard_id>/", views.dashboard_info, name="dashboard-info"),

    # Admin-only: sync allow-listed dashboards from settings into DB
    path("sync/", views.sync_embedded_dashboards, name="sync-dashboards"),
]
