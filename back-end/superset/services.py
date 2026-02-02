# back-end/superset/services.py

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import requests
import jwt
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

# NOTE: If these models do not exist in your project, you can remove the DB-saving part safely.
from .models import EmbeddedDashboard, GuestToken  # optional persistence


logger = logging.getLogger(__name__)


class SupersetServiceError(Exception):
    """Raised when Superset API calls fail in a controlled/meaningful way."""


class SupersetService:
    """
    Service responsible for talking to Apache Superset security endpoints.

    Key responsibilities:
    - Authenticate against Superset and obtain an access token (cached)
    - Create a Guest Token for embedding dashboards (using the cached access token)
    - Optionally store issued guest tokens in DB (audit/debug)
    """

    ACCESS_TOKEN_CACHE_KEY = "superset:access_token"
    REFRESH_TOKEN_CACHE_KEY = "superset:refresh_token"
    # Default TTL for access token cache. Adjust if your Superset access token lifetime differs.
    ACCESS_TOKEN_CACHE_TTL_SECONDS = 50 * 60  # 50 minutes

    def __init__(self) -> None:
        cfg = getattr(settings, "SUPERSET_CONFIG", None)
        if not cfg:
            raise SupersetServiceError(
                "Missing settings.SUPERSET_CONFIG. Please define SUPERSET_CONFIG in Django settings."
            )

        # Superset base URL, e.g. http://localhost:8088 or https://superset.example.com
        self.superset_url: str = cfg["SUPERSET_URL"].rstrip("/")
        self.username: str = cfg["SUPERSET_USERNAME"]
        self.password: str = cfg["SUPERSET_PASSWORD"]

        # Guest token expiry is usually controlled by Superset, but we keep this setting for DB persistence / fallback.
        self.guest_token_expiry_seconds: int = int(cfg.get("GUEST_TOKEN_EXPIRY", 600))

        # Session object reuses TCP connections and allows setting default headers.
        self.session = requests.Session()

    # ----------------------------
    # Internal helpers
    # ----------------------------

    def _login(self) -> Dict[str, Any]:
        """
        Login to Superset and return the token payload.
        We request refresh_token as well (refresh=True) so we can refresh access token without re-sending password.
        """
        auth_url = f"{self.superset_url}/api/v1/security/login"
        payload = {
            "username": self.username,
            "password": self.password,
            "provider": "db",
            "refresh": True,  # ask Superset to issue refresh_token too
        }

        try:
            r = self.session.post(auth_url, json=payload, timeout=15)
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            logger.exception("Superset login failed.")
            raise SupersetServiceError(f"Superset login failed: {e}") from e

    def _set_auth_header(self, access_token: str) -> None:
        """Attach access token to session headers for subsequent API calls."""
        self.session.headers.update({"Authorization": f"Bearer {access_token}"})

    def _decode_jwt_exp(self, token: str) -> Optional[datetime]:
        """
        Decode JWT without verifying signature, only to extract the 'exp' claim.
        This is safe for *expiry bookkeeping* but must NOT be used for trusting identity/roles.
        """
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            exp = payload.get("exp")
            if not exp:
                return None
            return datetime.fromtimestamp(exp, tz=timezone.get_current_timezone())
        except Exception:
            # If token is not a JWT or decode fails, just return None
            return None

    # ----------------------------
    # Access token management
    # ----------------------------

    def get_access_token(self) -> str:
        """
        Return a cached Superset access token.
        If missing/expired, login again and cache tokens.
        """
        cached = cache.get(self.ACCESS_TOKEN_CACHE_KEY)
        if cached:
            self._set_auth_header(cached)
            return cached

        token_data = self._login()
        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")

        if not access_token:
            raise SupersetServiceError("Superset login response did not contain access_token.")

        cache.set(self.ACCESS_TOKEN_CACHE_KEY, access_token, self.ACCESS_TOKEN_CACHE_TTL_SECONDS)
        if refresh_token:
            # Store refresh token longer; it typically lasts longer than access token
            cache.set(self.REFRESH_TOKEN_CACHE_KEY, refresh_token, 24 * 60 * 60)

        self._set_auth_header(access_token)
        return access_token

    def refresh_access_token(self) -> str:
        """
        Attempt to refresh access token using cached refresh token.
        If refresh token is missing/invalid, fallback to login.
        """
        refresh_token = cache.get(self.REFRESH_TOKEN_CACHE_KEY)
        if not refresh_token:
            # No refresh token available; do full login.
            return self.get_access_token()

        refresh_url = f"{self.superset_url}/api/v1/security/refresh"
        try:
            r = self.session.post(refresh_url, json={"refresh_token": refresh_token}, timeout=15)
            r.raise_for_status()
            token_data = r.json()
            access_token = token_data.get("access_token")
            if not access_token:
                raise SupersetServiceError("Superset refresh response did not contain access_token.")

            cache.set(self.ACCESS_TOKEN_CACHE_KEY, access_token, self.ACCESS_TOKEN_CACHE_TTL_SECONDS)
            self._set_auth_header(access_token)
            return access_token
        except requests.RequestException as e:
            logger.warning("Superset token refresh failed, falling back to login. Error=%s", e)
            # fallback
            cache.delete(self.ACCESS_TOKEN_CACHE_KEY)
            cache.delete(self.REFRESH_TOKEN_CACHE_KEY)
            return self.get_access_token()

    # ----------------------------
    # Guest token
    # ----------------------------

    def generate_guest_token(
        self,
        dashboard_uuid: str,
        user=None,
        resources: Optional[List[Dict[str, Any]]] = None,
        rls: Optional[List[Dict[str, Any]]] = None,
        persist_to_db: bool = True,
    ) -> str:
        """
        Generate a Superset Guest Token for embedding.

        IMPORTANT:
        - dashboard_uuid should be the UUID used by Superset embed (not numeric dashboard id).
        - This method will retry once if access token is expired (401/403).
        """
        # Ensure we have an access token (cached or newly obtained)
        self.get_access_token()

        guest_token_url = f"{self.superset_url}/api/v1/security/guest_token/"  # trailing slash is important

        # Default resources if not provided
        if resources is None:
            resources = [{"type": "dashboard", "id": dashboard_uuid}]

        # Default RLS (Row Level Security) if not provided
        if rls is None:
            rls = []

        user_payload = {
            "username": getattr(user, "username", "guest") if user else "guest",
            "first_name": getattr(user, "first_name", "Guest") if user else "Guest",
            "last_name": getattr(user, "last_name", "User") if user else "User",
        }

        body = {"user": user_payload, "resources": resources, "rls": rls}

        def _request_token() -> requests.Response:
            return self.session.post(guest_token_url, json=body, timeout=15)

        try:
            resp = _request_token()

            # If token expired/invalid, refresh access token and retry once.
            if resp.status_code in (401, 403):
                logger.info("Guest token request got %s; refreshing access token and retrying once.", resp.status_code)
                cache.delete(self.ACCESS_TOKEN_CACHE_KEY)
                self.refresh_access_token()
                resp = _request_token()

            resp.raise_for_status()
            token_data = resp.json()
            guest_token = token_data.get("token")
            if not guest_token:
                raise SupersetServiceError("Superset guest_token response did not contain token.")

            # Determine expiry from JWT (preferred), otherwise fallback to settings-based expiry
            exp_dt = self._decode_jwt_exp(guest_token)
            if not exp_dt:
                exp_dt = timezone.now() + timedelta(seconds=self.guest_token_expiry_seconds)

            # Optional: store issued token to DB for auditing
            if persist_to_db:
                try:
                    dashboard = EmbeddedDashboard.objects.filter(dashboard_id=dashboard_uuid).first()
                    if dashboard:
                        GuestToken.objects.create(
                            token=guest_token,
                            dashboard=dashboard,
                            user=user if user and getattr(user, "is_authenticated", False) else None,
                            expires_at=exp_dt,
                        )
                except Exception:
                    # Never fail the request just because DB persistence failed
                    logger.exception("Failed to persist GuestToken to DB (ignored).")

            return guest_token

        except requests.RequestException as e:
            logger.exception("Failed to generate guest token from Superset.")
            raise SupersetServiceError(f"Failed to generate guest token: {e}") from e

    # ----------------------------
    # Optional helpers
    # ----------------------------

    def get_dashboard_info(self, dashboard_id_or_uuid: str) -> Dict[str, Any]:
        """
        Fetch dashboard metadata from Superset.
        NOTE: This endpoint typically expects numeric dashboard ID in Superset.
        Use this only if you really need metadata from Superset for your own UI.
        """
        self.get_access_token()
        url = f"{self.superset_url}/api/v1/dashboard/{dashboard_id_or_uuid}"

        try:
            r = self.session.get(url, timeout=15)
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            logger.exception("Failed to get dashboard info from Superset.")
            raise SupersetServiceError(f"Failed to get dashboard info: {e}") from e

    def is_token_valid(self, token: str) -> bool:
        """
        Check whether a guest token is still valid based on our DB record.
        NOTE: This does not verify with Superset; it's a local check only.
        """
        try:
            obj = GuestToken.objects.get(token=token)
            return obj.expires_at > timezone.now()
        except GuestToken.DoesNotExist:
            return False
