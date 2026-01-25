import type {
  Product,
  ProductCreate,
  ProductUpdate,
  ProductListResponse,
  FeedbackItem,
  FeedbackListResponse,
  FeedbackStats,
  FeedbackFilterParams,
  FeedbackAnalyzeRequest,
  FeedbackAnalyzeResponse,
  FeedbackImportResponse,
  AudienceResearch,
  AudienceResearchRequest,
  AudienceResearchListResponse,
  Campaign,
  CampaignCreate,
  CampaignUpdate,
  CampaignListResponse,
  CampaignStats,
  ContentGenerateRequest,
  ContentGenerateResponse,
  TrackedLink,
  TrackedLinkCreate,
  TrackedLinkListResponse,
  TrackingStats,
  Insight,
  InsightListResponse,
  InsightActionRequest,
  FeedbackTheme,
  ThemeListResponse,
  ThemeClusterResponse,
  WeeklyReport,
  WeeklyReportListResponse,
  DeepAnalysis,
  DeepAnalysisRequest,
  DeepAnalysisListResponse,
  CreditsResponse,
} from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

class ApiError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    public data?: { error?: string; message?: string; details?: Record<string, unknown> }
  ) {
    super(data?.message || statusText);
    this.name = 'ApiError';
  }
}

async function request<T>(
  endpoint: string,
  options: RequestInit & { token?: string | null } = {}
): Promise<T> {
  const { token, ...fetchOptions } = options;

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(fetchOptions.headers || {}),
  };

  if (token) {
    (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...fetchOptions,
    headers,
  });

  if (!response.ok) {
    let data;
    try {
      data = await response.json();
    } catch {
      data = undefined;
    }
    throw new ApiError(response.status, response.statusText, data);
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return undefined as T;
  }

  return response.json();
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function buildQueryString(params: any): string {
  const searchParams = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== '') {
      searchParams.append(key, String(value));
    }
  }
  const queryString = searchParams.toString();
  return queryString ? `?${queryString}` : '';
}

export const api = {
  // Products
  products: {
    list: (token: string | null, params?: { limit?: number; offset?: number }) =>
      request<ProductListResponse>(`/products${buildQueryString(params || {})}`, { token }),

    get: (token: string | null, id: string) =>
      request<Product>(`/products/${id}`, { token }),

    create: (token: string | null, data: ProductCreate) =>
      request<Product>('/products', {
        token,
        method: 'POST',
        body: JSON.stringify(data),
      }),

    update: (token: string | null, id: string, data: ProductUpdate) =>
      request<Product>(`/products/${id}`, {
        token,
        method: 'PUT',
        body: JSON.stringify(data),
      }),

    delete: (token: string | null, id: string) =>
      request<void>(`/products/${id}`, {
        token,
        method: 'DELETE',
      }),
  },

  // Feedback
  feedback: {
    list: (token: string | null, params: FeedbackFilterParams) =>
      request<FeedbackListResponse>(`/feedback${buildQueryString(params)}`, { token }),

    get: (token: string | null, id: string) =>
      request<FeedbackItem>(`/feedback/${id}`, { token }),

    getStats: (token: string | null, productId: string, days?: number) =>
      request<FeedbackStats>(`/feedback/stats${buildQueryString({ product_id: productId, days })}`, { token }),

    analyze: (token: string | null, data: FeedbackAnalyzeRequest) =>
      request<FeedbackAnalyzeResponse>('/feedback/analyze', {
        token,
        method: 'POST',
        body: JSON.stringify(data),
      }),

    markActioned: (token: string | null, id: string) =>
      request<FeedbackItem>(`/feedback/${id}/action`, {
        token,
        method: 'POST',
      }),

    import: async (token: string | null, productId: string, file: File): Promise<FeedbackImportResponse> => {
      const formData = new FormData();
      formData.append('file', file);

      const headers: HeadersInit = {};
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`${API_BASE}/feedback/import?product_id=${productId}`, {
        method: 'POST',
        headers,
        body: formData,
      });

      if (!response.ok) {
        let data;
        try {
          data = await response.json();
        } catch {
          data = undefined;
        }
        throw new ApiError(response.status, response.statusText, data);
      }

      return response.json();
    },
  },

  // Audiences
  audiences: {
    list: (token: string | null, productId: string, params?: { limit?: number; offset?: number }) =>
      request<AudienceResearchListResponse>(
        `/audiences${buildQueryString({ product_id: productId, ...params })}`,
        { token }
      ),

    get: (token: string | null, id: string) =>
      request<AudienceResearch>(`/audiences/${id}`, { token }),

    research: (token: string | null, productId: string, data: AudienceResearchRequest) =>
      request<AudienceResearch>(`/audiences/research?product_id=${productId}`, {
        token,
        method: 'POST',
        body: JSON.stringify(data),
      }),
  },

  // Campaigns
  campaigns: {
    list: (token: string | null, params?: { product_id?: string; status?: string; limit?: number; offset?: number }) =>
      request<CampaignListResponse>(`/campaigns${buildQueryString(params || {})}`, { token }),

    get: (token: string | null, id: string) =>
      request<Campaign>(`/campaigns/${id}`, { token }),

    create: (token: string | null, data: CampaignCreate) =>
      request<Campaign>('/campaigns', {
        token,
        method: 'POST',
        body: JSON.stringify(data),
      }),

    update: (token: string | null, id: string, data: CampaignUpdate) =>
      request<Campaign>(`/campaigns/${id}`, {
        token,
        method: 'PUT',
        body: JSON.stringify(data),
      }),

    delete: (token: string | null, id: string) =>
      request<void>(`/campaigns/${id}`, {
        token,
        method: 'DELETE',
      }),

    getStats: (token: string | null, id: string) =>
      request<CampaignStats>(`/campaigns/${id}/stats`, { token }),

    generateContent: (token: string | null, id: string, data: ContentGenerateRequest) =>
      request<ContentGenerateResponse>(`/campaigns/${id}/generate`, {
        token,
        method: 'POST',
        body: JSON.stringify(data),
      }),
  },

  // Tracking
  tracking: {
    createLink: (token: string | null, data: TrackedLinkCreate) =>
      request<TrackedLink>('/tracking/links', {
        token,
        method: 'POST',
        body: JSON.stringify(data),
      }),

    listLinks: (token: string | null, params?: { campaign_id?: string; limit?: number; offset?: number }) =>
      request<TrackedLinkListResponse>(`/tracking/links${buildQueryString(params || {})}`, { token }),

    getStats: (token: string | null) =>
      request<TrackingStats>('/tracking/stats', { token }),
  },

  // Insights
  insights: {
    list: (token: string | null, params: { product_id: string; limit?: number; offset?: number; include_dismissed?: boolean; include_actioned?: boolean }) =>
      request<InsightListResponse>(`/insights${buildQueryString(params)}`, { token }),

    get: (token: string | null, id: string) =>
      request<Insight>(`/insights/${id}`, { token }),

    update: (token: string | null, id: string, data: InsightActionRequest) =>
      request<Insight>(`/insights/${id}`, {
        token,
        method: 'PATCH',
        body: JSON.stringify(data),
      }),

    // Themes
    getThemes: (token: string | null, productId: string, activeOnly?: boolean) =>
      request<ThemeListResponse>(
        `/insights/themes${buildQueryString({ product_id: productId, active_only: activeOnly })}`,
        { token }
      ),

    getTheme: (token: string | null, id: string) =>
      request<FeedbackTheme>(`/insights/themes/${id}`, { token }),

    triggerClustering: (token: string | null, productId: string, minFeedbackCount?: number) =>
      request<ThemeClusterResponse>(`/insights/cluster?product_id=${productId}`, {
        token,
        method: 'POST',
        body: JSON.stringify({ min_feedback_count: minFeedbackCount }),
      }),

    // Weekly Reports
    listReports: (token: string | null, productId: string, params?: { limit?: number; offset?: number }) =>
      request<WeeklyReportListResponse>(
        `/insights/reports${buildQueryString({ product_id: productId, ...params })}`,
        { token }
      ),

    getReport: (token: string | null, id: string) =>
      request<WeeklyReport>(`/insights/reports/${id}`, { token }),

    triggerReportGeneration: (token: string | null, productId: string) =>
      request<ThemeClusterResponse>(`/insights/reports/generate?product_id=${productId}`, {
        token,
        method: 'POST',
      }),

    // Deep Analysis
    getCredits: (token: string | null) =>
      request<CreditsResponse>('/insights/credits', { token }),

    listDeepAnalyses: (token: string | null, productId: string, params?: { limit?: number; offset?: number }) =>
      request<DeepAnalysisListResponse>(
        `/insights/analyze${buildQueryString({ product_id: productId, ...params })}`,
        { token }
      ),

    getDeepAnalysis: (token: string | null, id: string) =>
      request<DeepAnalysis>(`/insights/analyze/${id}`, { token }),

    triggerDeepAnalysis: (token: string | null, productId: string, data: DeepAnalysisRequest) =>
      request<DeepAnalysis>(`/insights/analyze?product_id=${productId}`, {
        token,
        method: 'POST',
        body: JSON.stringify(data),
      }),
  },
};

export { ApiError };
export default api;
