/**
 * TypeScript types for GEO Application
 */

export interface User {
  id: string
  email: string
  first_name?: string
  last_name?: string
  role: 'super_admin' | 'client'
  is_active: boolean
  created_at: string
  subscription?: Subscription
}

export interface Subscription {
  id: string
  plan_type: 'free' | 'pro' | 'business'
  status: 'active' | 'cancelled' | 'expired'
  monthly_analyses_limit: number
  analyses_used: number
  price_monthly: number
  start_date: string
  end_date?: string
}

export interface Website {
  id: string
  url: string
  domain: string
  language_detected?: string
  is_bilingual: boolean
  is_quebec_brand: boolean
  business_type?: string
  last_crawled_at?: string
}

export interface Analysis {
  id: string
  website_id: string
  user_id: string
  status: 'pending' | 'crawling' | 'analyzing' | 'completed' | 'failed'
  plan_type: string
  global_score?: number
  score_structure?: number
  score_machine_readability?: number
  score_eeat?: number
  score_educational_content?: number
  score_thematic_organization?: number
  score_ai_optimization?: number
  score_semantic_richness?: number
  score_domain_authority?: number
  score_freshness?: number
  score_user_intent?: number
  pages_crawled?: number
  total_questions_generated?: number
  llm_tests_performed?: number
  competitors_found?: number
  error_message?: string
  started_at: string
  completed_at?: string
}

export interface Competitor {
  id: string
  competitor_domain: string
  competitor_url: string
  discovery_method: string
  relevance_score: number
  global_score?: number
  gap_global?: number
}

export interface LLMTestResult {
  id: string
  llm_provider: 'claude' | 'chatgpt' | 'perplexity' | 'gemini'
  query_text: string
  response_text: string
  brand_mentioned: boolean
  brand_position?: number
  competitors_mentioned: string[]
}

export interface TechnicalRecommendation {
  id: string
  recommendation_type: string
  page_url: string
  priority: 'critical' | 'high' | 'medium' | 'low'
  code_snippet: string
  implementation_notes: string
  estimated_impact: number
}

export interface OptimizedContent {
  id: string
  page_url: string
  optimized_title: string
  optimized_meta_description: string
  optimized_h1: string
  optimized_content: string
  optimized_faq: { question: string; answer: string }[]
}
