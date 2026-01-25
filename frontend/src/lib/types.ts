// Enums matching backend schemas
export type Platform = 'reddit' | 'twitter' | 'hackernews' | 'github' | 'email' | 'widget' | 'manual';
export type Sentiment = 'positive' | 'negative' | 'neutral' | 'mixed';
export type FeedbackCategory = 'bug' | 'feature_request' | 'praise' | 'complaint' | 'question' | 'churn_risk' | 'competitor_mention';
export type Urgency = 'low' | 'medium' | 'high' | 'critical';
export type PostStyle = 'helpful' | 'story' | 'question' | 'insight';
export type SubscriptionTier = 'indie' | 'pro' | 'agency';
export type CampaignStatus = 'draft' | 'active' | 'completed' | 'archived';
export type InsightType = 'marketing_opportunity' | 'churn_risk' | 'feature_demand' | 'competitor_insight' | 'sentiment_shift' | 'trending_topic' | 'action_required';
export type DeepAnalysisType = 'churn_analysis' | 'competitor_intelligence' | 'content_strategy';
export type DeepAnalysisStatus = 'pending' | 'processing' | 'completed' | 'failed';

// Organization
export interface Organization {
  id: string;
  name: string;
  subscription_tier: SubscriptionTier;
  created_at: string;
  updated_at: string;
}

// User
export interface User {
  id: string;
  email: string;
  name: string;
  clerk_id: string;
  organization_id: string;
  created_at: string;
  updated_at: string;
  organization?: Organization | null;
}

// Product
export interface Product {
  id: string;
  organization_id: string;
  name: string;
  description: string;
  url?: string | null;
  keywords: string[];
  competitors: string[];
  created_at: string;
  updated_at: string;
}

export interface ProductCreate {
  name: string;
  description: string;
  url?: string | null;
  keywords?: string[];
  competitors?: string[];
}

export interface ProductUpdate {
  name?: string | null;
  description?: string | null;
  url?: string | null;
  keywords?: string[] | null;
  competitors?: string[] | null;
}

export interface ProductListResponse {
  items: Product[];
  total: number;
}

// Feedback
export interface FeedbackItem {
  id: string;
  product_id: string;
  text: string;
  source: string;
  source_url?: string | null;
  author?: string | null;
  author_id?: string | null;
  sentiment: string;
  emotion?: string | null;
  category: string;
  subcategory?: string | null;
  urgency: string;
  product_area?: string | null;
  key_phrases: string[];
  churn_risk: number;
  suggested_action?: string | null;
  is_actioned: boolean;
  actioned_at?: string | null;
  collected_at: string;
  created_at: string;
  updated_at: string;
}

export interface FeedbackListResponse {
  items: FeedbackItem[];
  total: number;
}

export interface FeedbackFilterParams {
  product_id: string;
  source?: Platform;
  sentiment?: Sentiment;
  category?: FeedbackCategory;
  urgency?: Urgency;
  is_actioned?: boolean;
  start_date?: string;
  end_date?: string;
  search?: string;
  limit?: number;
  offset?: number;
  sort_by?: 'created_at' | 'sentiment' | 'urgency' | 'churn_risk';
  sort_order?: 'asc' | 'desc';
}

export interface SentimentTrend {
  date: string;
  score: number;
  count: number;
}

export interface FeedbackStats {
  product_id: string;
  period_days: number;
  total_count: number;
  sentiment_counts: Record<string, number>;
  category_counts: Record<string, number>;
  source_counts: Record<string, number>;
  urgency_counts: Record<string, number>;
  avg_churn_risk: number;
  high_churn_count: number;
  top_phrases: Array<{ phrase: string; count: number }>;
  sentiment_trend: SentimentTrend[];
  actioned_count: number;
  actioned_rate: number;
}

export interface FeedbackAnalyzeRequest {
  text: string;
  source?: Platform;
  author?: string | null;
  context?: Record<string, unknown>;
}

export interface FeedbackAnalyzeResponse {
  sentiment: string;
  emotion?: string | null;
  category: string;
  subcategory?: string | null;
  urgency: string;
  product_area?: string | null;
  key_phrases: string[];
  churn_risk: number;
  suggested_action?: string | null;
}

export interface FeedbackImportResponse {
  imported: number;
  failed: number;
  errors: string[];
}

// Audience Research
export interface AudienceSource {
  id: string;
  product_id: string;
  platform: Platform;
  name: string;
  url: string;
  relevance_score: number;
  monthly_active?: number | null;
  recent_relevant_posts: number;
  reasoning: string;
  discovered_at: string;
  last_checked: string;
}

export interface AudienceResearchRequest {
  product_description: string;
  product_url?: string | null;
  focus?: 'b2b' | 'b2c' | 'developer' | null;
}

export interface AudienceResearch {
  id: string;
  product_id: string;
  sources: AudienceSource[];
  keywords: string[];
  competitors_mentioned: string[];
  confidence: 'low' | 'medium' | 'high';
  created_at: string;
}

export interface AudienceResearchListResponse {
  items: AudienceResearch[];
  total: number;
}

// Campaigns
export interface GeneratedPost {
  id: string;
  campaign_id: string;
  platform: string;
  target_community: string;
  style: string;
  title?: string | null;
  body: string;
  cta_subtle?: string | null;
  estimated_engagement?: string | null;
  is_posted: boolean;
  posted_at?: string | null;
  post_url?: string | null;
  created_at: string;
}

export interface TrackedLink {
  id: string;
  campaign_id: string;
  destination_url: string;
  short_code: string;
  short_url: string;
  utm_url: string;
  utm_source: string;
  utm_medium: string;
  utm_campaign: string;
  utm_content?: string | null;
  utm_term?: string | null;
  clicks: number;
  conversions: number;
  conversion_rate: number;
  created_at: string;
}

export interface Campaign {
  id: string;
  product_id: string;
  name: string;
  description?: string | null;
  status: CampaignStatus;
  target_subreddits: string[];
  total_clicks: number;
  total_conversions: number;
  conversion_rate: number;
  posts: GeneratedPost[];
  links: TrackedLink[];
  created_at: string;
  updated_at: string;
}

export interface CampaignCreate {
  product_id: string;
  name: string;
  description?: string | null;
  target_subreddits?: string[];
}

export interface CampaignUpdate {
  name?: string | null;
  description?: string | null;
  status?: CampaignStatus | null;
  target_subreddits?: string[] | null;
}

export interface CampaignListResponse {
  items: Campaign[];
  total: number;
}

export interface CampaignStats {
  campaign_id: string;
  campaign_name: string;
  status: CampaignStatus;
  total_posts: number;
  total_links: number;
  total_clicks: number;
  total_conversions: number;
  conversion_rate: number;
  clicks_by_source: Record<string, number>;
  conversions_by_source: Record<string, number>;
  top_performing_links: TrackedLink[];
  recent_clicks: number;
  recent_conversions: number;
}

export interface ContentGenerateRequest {
  subreddit: string;
  topic_hint?: string | null;
  include_rules?: boolean;
}

export interface ContentGenerateResponse {
  campaign_id: string;
  subreddit: string;
  subreddit_rules?: string[] | null;
  posts: GeneratedPost[];
}

export interface TrackedLinkCreate {
  campaign_id: string;
  destination_url: string;
  utm_source: string;
  utm_medium?: string;
  utm_content?: string | null;
  utm_term?: string | null;
}

export interface TrackedLinkListResponse {
  items: TrackedLink[];
  total: number;
}

// Insights
export interface FeedbackTheme {
  id: string;
  product_id: string;
  name: string;
  description: string;
  feedback_count: number;
  sentiment_breakdown: Record<string, number>;
  urgency: string;
  sample_feedback_ids: string[];
  keywords: string[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ThemeListResponse {
  themes: FeedbackTheme[];
  total: number;
  last_clustered_at?: string | null;
}

export interface ThemeClusterResponse {
  task_id: string;
  status: string;
  message: string;
}

export interface WeeklyReportSummary {
  id: string;
  product_id: string;
  week_start: string;
  week_end: string;
  new_mentions: number;
  sentiment_score: number;
  sentiment_change: number;
  email_sent: boolean;
  created_at: string;
}

export interface WeeklyReport {
  id: string;
  product_id: string;
  week_start: string;
  week_end: string;
  posts_published: number;
  total_clicks: number;
  total_conversions: number;
  conversion_rate: number;
  best_performing_post?: string | null;
  new_mentions: number;
  sentiment_score: number;
  sentiment_change: number;
  top_complaints: Array<{ text: string; count: number }>;
  top_praise: Array<{ text: string; count: number }>;
  executive_summary?: string | null;
  marketing_analysis?: Record<string, unknown> | null;
  sentiment_analysis?: Record<string, unknown> | null;
  recommended_actions: Array<{ priority: string; action: string; reason: string }>;
  next_week_focus?: { topics: string[]; subreddits: string[]; trending?: string | null } | null;
  email_sent: boolean;
  email_sent_at?: string | null;
  created_at: string;
}

export interface WeeklyReportListResponse {
  reports: WeeklyReportSummary[];
  total: number;
}

export interface Insight {
  id: string;
  product_id: string;
  type: string;
  title: string;
  description: string;
  priority: string;
  evidence: string[];
  suggested_action?: string | null;
  confidence: number;
  source: string;
  is_actioned: boolean;
  actioned_at?: string | null;
  is_dismissed: boolean;
  created_at: string;
  updated_at: string;
}

export interface InsightListResponse {
  insights: Insight[];
  total: number;
}

export interface InsightActionRequest {
  is_actioned?: boolean;
  is_dismissed?: boolean;
}

export interface DeepAnalysisRequest {
  analysis_type: DeepAnalysisType;
  parameters?: Record<string, unknown>;
}

export interface DeepAnalysis {
  id: string;
  product_id: string;
  organization_id: string;
  analysis_type: string;
  status: string;
  results?: Record<string, unknown> | null;
  summary?: string | null;
  recommendations: Array<{ action: string; priority: string; reason: string }>;
  data_points_analyzed: number;
  error_message?: string | null;
  started_at?: string | null;
  completed_at?: string | null;
  created_at: string;
  updated_at: string;
}

export interface DeepAnalysisListResponse {
  analyses: DeepAnalysis[];
  total: number;
}

export interface CreditsResponse {
  tier: string;
  credits_remaining: number;
  credits_total: number;
  is_unlimited: boolean;
  reset_at?: string | null;
}

// Tracking
export interface TrackingStats {
  total_links: number;
  total_clicks: number;
  total_conversions: number;
  overall_conversion_rate: number;
  clicks_today: number;
  conversions_today: number;
  top_campaigns: Array<{ campaign_id: string; campaign_name: string; clicks: number }>;
}

// Common responses
export interface HealthResponse {
  status: string;
  version?: string;
}

export interface ErrorResponse {
  error: string;
  message: string;
  details?: Record<string, unknown>;
}
