import axios, { type InternalAxiosRequestConfig } from "axios";

const API_BASE_URL = "http://127.0.0.1:8080";

/**
 * Request payload for guest token creation.
 * IMPORTANT:
 * - dashboard_uuid must be the UUID from Superset "Embed" panel.
 * - user_id is NOT accepted/needed (backend uses request.user).
 */
export interface GuestTokenRequest {
  dashboard_uuid: string;
  resources?: Record<string, unknown>[];
  rls?: Record<string, unknown>[];
}

/**
 * Response returned by backend for embed SDK.
 * React embedded SDK needs:
 * - token
 * - dashboard_uuid
 * - superset_domain
 */
export interface GuestTokenResponse {
  token: string;
  dashboard_uuid: string;
  superset_domain: string;
}

/**
 * Our internal allow-list dashboard record (stored in Django DB).
 */
export interface EmbeddedDashboard {
  id: number;
  name: string;

  // Numeric Superset dashboard id (optional; used for metadata endpoint only)
  superset_dashboard_id: number | null;

  // UUID used for Superset embedded SDK / guest token resources
  dashboard_uuid: string;

  // Browser-reachable Superset domain (e.g. http://localhost:8088)
  domain: string;

  allowed_roles: string[];
  created_at: string;
  updated_at: string;
}

class SupersetService {
  private api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
      "Content-Type": "application/json",
    },

    /**
     * If your Django auth uses cookies (SessionAuthentication),
     * you MUST enable withCredentials and configure CORS accordingly.
     * If you use JWT/Bearer tokens only, you can set this to false.
     */
    withCredentials: true,
  });

  constructor() {
    // Add request interceptor to include auth token if available (JWT/Bearer style)
    // Fixes Axios v1 + TypeScript header typing issues by using headers.set()
    this.api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
      const token = localStorage.getItem("authToken");
      if (token) {
        config.headers.set("Authorization", `Bearer ${token}`);
      }
      return config;
    });
  }

  /**
   * Generate a guest token for dashboard embedding.
   * POST /api/superset/guest-token/
   */
  async generateGuestToken(request: GuestTokenRequest): Promise<GuestTokenResponse> {
    const response = await this.api.post<GuestTokenResponse>("/api/superset/guest-token/", request);
    return response.data;
  }

  /**
   * Get all embedded dashboards (allow-list).
   * GET /api/superset/dashboards/
   */
  async getEmbeddedDashboards(): Promise<EmbeddedDashboard[]> {
    const response = await this.api.get<EmbeddedDashboard[]>("/api/superset/dashboards/");
    return response.data;
  }

  /**
   * Get a specific embedded dashboard record by internal DB id.
   * GET /api/superset/dashboards/:id/
   */
  async getEmbeddedDashboard(id: number): Promise<EmbeddedDashboard> {
    const response = await this.api.get<EmbeddedDashboard>(`/api/superset/dashboards/${id}/`);
    return response.data;
  }

  /**
   * Validate a guest token (optional debugging endpoint).
   * GET /api/superset/guest-token/:token/validate/
   */
  async validateGuestToken(
    token: string
  ): Promise<{ valid: boolean; token_info?: Record<string, unknown> }> {
    const safeToken = encodeURIComponent(token);
    const response = await this.api.get<{ valid: boolean; token_info?: Record<string, unknown> }>(
      `/api/superset/guest-token/${safeToken}/validate/`
    );
    return response.data;
  }

  /**
   * Get dashboard information from Superset using numeric dashboard id.
   * GET /api/superset/dashboard/:superset_dashboard_id/
   */
  async getDashboardInfo(supersetDashboardId: number): Promise<Record<string, unknown>> {
    const response = await this.api.get<Record<string, unknown>>(`/api/superset/dashboard/${supersetDashboardId}/`);
    return response.data;
  }

  /**
   * Create a new embedded dashboard record (admin only).
   */
  async createEmbeddedDashboard(
    dashboard: Omit<EmbeddedDashboard, "id" | "created_at" | "updated_at">
  ): Promise<EmbeddedDashboard> {
    const response = await this.api.post<EmbeddedDashboard>("/api/superset/dashboards/", dashboard);
    return response.data;
  }

  /**
   * Update an embedded dashboard record (admin only).
   */
  async updateEmbeddedDashboard(id: number, dashboard: Partial<EmbeddedDashboard>): Promise<EmbeddedDashboard> {
    const response = await this.api.put<EmbeddedDashboard>(`/api/superset/dashboards/${id}/`, dashboard);
    return response.data;
  }

  /**
   * Delete an embedded dashboard record (admin only).
   */
  async deleteEmbeddedDashboard(id: number): Promise<void> {
    await this.api.delete(`/api/superset/dashboards/${id}/`);
  }

  /**
   * Sync dashboards from Django settings into DB (admin only).
   * POST /api/superset/sync/
   */
  async syncEmbeddedDashboards(): Promise<{ message: string; count: number }> {
    const response = await this.api.post<{ message: string; count: number }>("/api/superset/sync/");
    return response.data;
  }
}

export default new SupersetService();
