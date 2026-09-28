/**
 * CivicPulse Domain Types
 *
 * TypeScript types matching the backend domain contract.
 * These are the frontend's typed representation of the API schema.
 * The frontend does NOT own business rules — the backend does.
 */

/** Complaint category — must match backend Category enum exactly. */
export type Category = 'water' | 'electricity' | 'sanitation' | 'roads' | 'streetlights' | 'other';

/** Complaint priority — must match backend Priority enum exactly. */
export type Priority = 'high' | 'normal' | 'low';

/** Complaint status — must match backend Status enum exactly. */
export type Status = 'open' | 'in_progress' | 'resolved' | 'rejected';

/** All valid category values for filters and validation. */
export const CATEGORIES: readonly Category[] = [
  'water', 'electricity', 'sanitation', 'roads', 'streetlights', 'other',
] as const;

/** All valid priority values for filters and validation. */
export const PRIORITIES: readonly Priority[] = ['high', 'normal', 'low'] as const;

/** All valid status values for filters. */
export const STATUSES: readonly Status[] = ['open', 'in_progress', 'resolved', 'rejected'] as const;

/** Request body for POST /api/complaints. */
export interface ComplaintCreateRequest {
  text: string;
  location: string;
  reporter_contact?: string;
}

/** Response for a single complaint. */
export interface Complaint {
  id: string;
  text: string;
  location: string;
  reporter_contact: string | null;
  category: Category;
  priority: Priority;
  status: Status;
  ai_summary: string | null;
  triaged_by: string;
  triage_latency_ms: number;
  created_at: string;
  updated_at: string;
}

/** Paginated complaint list response. */
export interface ComplaintListResponse {
  items: Complaint[];
  total: number;
  page: number;
  page_size: number;
}

/** Status update request body. */
export interface StatusUpdateRequest {
  status: Status;
}

/** Aggregate statistics response. */
export interface StatsResponse {
  by_category: Record<string, number>;
  by_priority: Record<string, number>;
}

/** Provider metadata response. */
export interface ProviderMetaResponse {
  active_provider: string;
  recent_outcomes: TriageOutcome[];
}

/** Individual triage outcome. */
export interface TriageOutcome {
  provider: string;
  latency_ms: number;
  fallback: boolean;
}

/** Field-level validation error from backend. */
export interface ValidationError {
  field: string;
  message: string;
}

/** HTTP 400 validation error response. */
export interface ValidationErrorResponse {
  errors: ValidationError[];
}
