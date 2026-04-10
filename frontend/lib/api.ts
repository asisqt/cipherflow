/**
 * CipherFlow API Client
 * ======================
 * Typed HTTP client for all CipherFlow backend endpoints.
 * Handles JWT storage, request headers, and error formatting.
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const API_BASE = `${API_URL}/api/v1`

// ── Types ───────────────────────────────────────────────────────────────────

export interface AuthResponse {
  access_token: string
  token_type: string
  expires_in: number
}

export interface PipelineStage {
  name: string
  status: string
  duration_ms: number
}

export interface ProcessResponse {
  status: string
  record_id: string
  processed_data: Record<string, any> | null
  encrypted_blob: string | null
  is_encrypted: boolean
  checksum: string
  processed_at: string
  warnings: string[]
  pipeline: PipelineStage[]
}

export interface HealthResponse {
  status: string
  service: string
  version: string
  uptime_seconds: number
  build: string
  timestamp: string
}

// ── Token Management ────────────────────────────────────────────────────────

let _token: string | null = null

export function setToken(token: string) { _token = token }
export function getToken(): string | null { return _token }
export function clearToken() { _token = null }

function authHeaders(): Record<string, string> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (_token) headers['Authorization'] = `Bearer ${_token}`
  return headers
}

// ── API Methods ─────────────────────────────────────────────────────────────

export async function login(username: string, password: string): Promise<AuthResponse> {
  const res = await fetch(`${API_BASE}/auth/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Authentication failed' }))
    throw new Error(err.detail || 'Authentication failed')
  }
  const data: AuthResponse = await res.json()
  setToken(data.access_token)
  return data
}

export async function processData(
  id: string,
  data: Record<string, any>,
  encrypt: boolean = false,
): Promise<ProcessResponse> {
  const endpoint = encrypt ? '/process/encrypted' : '/process'
  const res = await fetch(`${API_BASE}${endpoint}`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify({ id, data }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Processing failed' }))
    throw new Error(typeof err.detail === 'string' ? err.detail : JSON.stringify(err.detail))
  }
  return res.json()
}

export async function checkHealth(): Promise<HealthResponse> {
  const res = await fetch(`${API_BASE}/health`)
  if (!res.ok) throw new Error('Health check failed')
  return res.json()
}

// ── Demo Presets ────────────────────────────────────────────────────────────

export const PRESETS = [
  {
    name: 'Financial payload',
    icon: '₿',
    id: 'txn-2024-0847',
    data: {
      name: '  Ashish Khatri  ',
      email: 'ashish@cipherflow.dev',
      credit_card: '4111-1111-1111-1111',
      cvv: '847',
      amount: 24999.50,
      currency: 'INR',
    },
  },
  {
    name: 'Healthcare record',
    icon: '🏥',
    id: 'patient-00412',
    data: {
      name: '  PRIYA SHARMA  ',
      email: 'priya.sharma@hospital.org',
      ssn: '987-65-4321',
      diagnosis: 'Type 2 Diabetes',
      blood_group: 'O+',
      pin: '4829',
    },
  },
  {
    name: 'User registration',
    icon: '👤',
    id: 'usr-reg-1109',
    data: {
      name: '  Rahul Verma  ',
      email: 'rahul@startup.io',
      password: 'SuperSecret@2024',
      token: 'sk_live_abc123def456',
      role: 'developer',
      company: 'TechCorp India',
    },
  },
]
