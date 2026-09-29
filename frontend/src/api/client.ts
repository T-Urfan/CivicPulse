/**
 * CivicPulse API Client
 *
 * Typed HTTP client for the CivicPulse backend API.
 * Uses relative /api paths so no environment-specific URL is baked in.
 * In dev, Vite proxies /api to the backend.
 * In production, nginx or Ingress handles the routing.
 */

import type {
  Complaint,
  ComplaintCreateRequest,
  ComplaintListResponse,
  ProviderMetaResponse,
  StatsResponse,
  StatusUpdateRequest,
  ValidationErrorResponse,
} from './types';

/** API error with structured error details from the backend. */
export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly statusText: string,
    public readonly body?: ValidationErrorResponse | Record<string, unknown>,
    public readonly retryAfter?: number,
  ) {
    super(`API Error ${status}: ${statusText}`);
    this.name = 'ApiError';
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let body: ValidationErrorResponse | Record<string, unknown> | undefined;
    try {
      body = await response.json();
    } catch {
      // Response may not be JSON
    }
    
    let retryAfter: number | undefined;
    const retryHeader = response.headers.get('Retry-After');
    if (retryHeader) {
      retryAfter = parseInt(retryHeader, 10);
    }
    
    throw new ApiError(response.status, response.statusText, body, retryAfter);
  }
  return response.json() as Promise<T>;
}

/** Submit a new complaint. */
export async function createComplaint(data: ComplaintCreateRequest): Promise<Complaint> {
  const response = await fetch('/api/complaints', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return handleResponse<Complaint>(response);
}

/** Get a single complaint by ID. */
export async function getComplaint(id: string): Promise<Complaint> {
  const response = await fetch(`/api/complaints/${id}`);
  return handleResponse<Complaint>(response);
}

/** List complaints with optional filters and pagination. */
export async function listComplaints(params: {
  page?: number;
  page_size?: number;
  category?: string;
  priority?: string;
  status?: string;
} = {}): Promise<ComplaintListResponse> {
  const searchParams = new URLSearchParams();
  if (params.page) searchParams.set('page', String(params.page));
  if (params.page_size) searchParams.set('page_size', String(params.page_size));
  if (params.category) searchParams.set('category', params.category);
  if (params.priority) searchParams.set('priority', params.priority);
  if (params.status) searchParams.set('status', params.status);

  const query = searchParams.toString();
  const url = query ? `/api/complaints?${query}` : '/api/complaints';
  const response = await fetch(url);
  return handleResponse<ComplaintListResponse>(response);
}

/** Update complaint status. */
export async function updateComplaintStatus(
  id: string,
  data: StatusUpdateRequest,
): Promise<Complaint> {
  const response = await fetch(`/api/complaints/${id}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return handleResponse<Complaint>(response);
}

/** Get aggregate statistics. Returns both the data and the X-Cache header value. */
export async function getStats(): Promise<{ data: StatsResponse; cacheState: string }> {
  const response = await fetch('/api/stats');
  const data = await handleResponse<StatsResponse>(response);
  const cacheState = response.headers.get('X-Cache') ?? 'UNKNOWN';
  return { data, cacheState };
}

/** Get provider metadata. */
export async function getProviderMeta(): Promise<ProviderMetaResponse> {
  const response = await fetch('/api/meta/providers');
  return handleResponse<ProviderMetaResponse>(response);
}
