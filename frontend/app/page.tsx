'use client'

import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Shield, Zap, Lock, CheckCircle2, AlertTriangle,
  Eye, EyeOff, ChevronRight, Hash, FileKey, ArrowRight,
  Activity, Terminal, Cpu, Server,
} from 'lucide-react'
import {
  login, processData, checkHealth, clearToken, getToken,
  PRESETS, type ProcessResponse, type HealthResponse,
} from '@/lib/api'

// ── Pipeline Stage Config ───────────────────────────────────────────────────

const STAGES = [
  { key: 'validation',    label: 'Validating',    icon: CheckCircle2, color: '#22c55e' },
  { key: 'normalization', label: 'Normalizing',   icon: Zap,          color: '#3b82f6' },
  { key: 'redaction',     label: 'Redacting',     icon: EyeOff,       color: '#f59e0b' },
  { key: 'checksum',      label: 'Checksumming',  icon: Hash,         color: '#8b5cf6' },
  { key: 'encryption',    label: 'Encrypting',    icon: Lock,         color: '#ec4899' },
]

// ── Main Page Component ─────────────────────────────────────────────────────

export default function Home() {
  const [view, setView] = useState<'landing' | 'auth' | 'dashboard'>('landing')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [authError, setAuthError] = useState('')
  const [authLoading, setAuthLoading] = useState(false)

  const [jsonInput, setJsonInput] = useState(JSON.stringify(PRESETS[0].data, null, 2))
  const [recordId, setRecordId] = useState(PRESETS[0].id)
  const [encrypt, setEncrypt] = useState(false)
  const [processing, setProcessing] = useState(false)
  const [activeStage, setActiveStage] = useState(-1)
  const [result, setResult] = useState<ProcessResponse | null>(null)
  const [error, setError] = useState('')

  const [health, setHealth] = useState<HealthResponse | null>(null)

  // ── Health Polling ──────────────────────────────────────────────────────
  useEffect(() => {
    const poll = () => checkHealth().then(setHealth).catch(() => setHealth(null))
    poll()
    const id = setInterval(poll, 15000)
    return () => clearInterval(id)
  }, [])

  // ── Auth Handler ────────────────────────────────────────────────────────
  const handleLogin = async () => {
    setAuthError('')
    setAuthLoading(true)
    try {
      await login(username, password)
      setView('dashboard')
    } catch (e: any) {
      setAuthError(e.message || 'Login failed')
    } finally {
      setAuthLoading(false)
    }
  }

  // ── Process Handler with Stage Animation ────────────────────────────────
  const handleProcess = useCallback(async () => {
    setError('')
    setResult(null)
    setProcessing(true)
    setActiveStage(0)

    try {
      const data = JSON.parse(jsonInput)
      const stagesToAnimate = encrypt ? 5 : 4

      // Animate stages sequentially
      for (let i = 0; i < stagesToAnimate; i++) {
        setActiveStage(i)
        await new Promise(r => setTimeout(r, 350))
      }

      const res = await processData(recordId, data, encrypt)
      setResult(res)
      setActiveStage(stagesToAnimate)
    } catch (e: any) {
      setError(e.message || 'Processing failed')
      setActiveStage(-1)
    } finally {
      setProcessing(false)
    }
  }, [jsonInput, recordId, encrypt])

  // ── Preset Loader ───────────────────────────────────────────────────────
  const loadPreset = (index: number) => {
    const p = PRESETS[index]
    setRecordId(p.id)
    setJsonInput(JSON.stringify(p.data, null, 2))
    setResult(null)
    setActiveStage(-1)
    setError('')
  }

  // ── Render ──────────────────────────────────────────────────────────────
  return (
    <div className="min-h-screen flex flex-col">

      {/* ━━ LANDING ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */}
      <AnimatePresence mode="wait">
        {view === 'landing' && (
          <motion.div
            key="landing"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0, y: -20 }}
            className="flex-1 flex flex-col items-center justify-center px-6"
          >
            {/* Logo */}
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.1 }}
              className="mb-8 relative"
            >
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-cipher-500 to-cipher-700 flex items-center justify-center">
                <Shield className="w-8 h-8 text-white" />
              </div>
              <div className="absolute -inset-4 bg-cipher-500/10 rounded-3xl blur-2xl -z-10" />
            </motion.div>

            {/* Title */}
            <motion.h1
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.2 }}
              className="text-5xl md:text-6xl font-bold tracking-tight text-center"
            >
              Cipher<span className="text-cipher-400">Flow</span>
            </motion.h1>

            <motion.p
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.3 }}
              className="mt-4 text-lg text-zinc-400 text-center max-w-lg"
            >
              Secure data processing pipeline. Validate, normalize, redact,
              and encrypt sensitive payloads through a five-stage API.
            </motion.p>

            {/* Feature pills */}
            <motion.div
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.4 }}
              className="mt-8 flex flex-wrap justify-center gap-3"
            >
              {['JWT Auth', 'Fernet Encryption', 'PII Redaction', 'SHA-256 Checksums', 'Kubernetes'].map((f) => (
                <span key={f} className="px-3 py-1.5 text-xs font-medium text-zinc-300 bg-zinc-800/60 border border-zinc-700/50 rounded-full">
                  {f}
                </span>
              ))}
            </motion.div>

            {/* CTA */}
            <motion.button
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.5 }}
              onClick={() => setView('auth')}
              className="mt-10 group flex items-center gap-2 px-6 py-3 bg-cipher-600 hover:bg-cipher-500 text-white font-medium rounded-xl transition-all"
            >
              Try it live
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </motion.button>

            {/* Tech stack */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.7 }}
              className="mt-16 flex items-center gap-6 text-xs text-zinc-600"
            >
              <span className="flex items-center gap-1.5"><Cpu className="w-3.5 h-3.5" /> FastAPI</span>
              <span className="flex items-center gap-1.5"><Server className="w-3.5 h-3.5" /> Kubernetes</span>
              <span className="flex items-center gap-1.5"><Terminal className="w-3.5 h-3.5" /> Terraform</span>
              <span className="flex items-center gap-1.5"><Activity className="w-3.5 h-3.5" /> GitHub Actions</span>
            </motion.div>
          </motion.div>
        )}

        {/* ━━ AUTH PANEL ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */}
        {view === 'auth' && (
          <motion.div
            key="auth"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="flex-1 flex items-center justify-center px-6"
          >
            <div className="w-full max-w-sm">
              <button
                onClick={() => setView('landing')}
                className="mb-8 text-sm text-zinc-500 hover:text-zinc-300 transition-colors"
              >
                ← Back
              </button>

              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 rounded-xl bg-cipher-600/20 flex items-center justify-center">
                  <Lock className="w-5 h-5 text-cipher-400" />
                </div>
                <div>
                  <h2 className="text-xl font-semibold">Authenticate</h2>
                  <p className="text-sm text-zinc-500">Sign in to access the pipeline</p>
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-xs font-medium text-zinc-400 mb-1.5">Username</label>
                  <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="admin"
                    className="w-full px-4 py-2.5 bg-zinc-900 border border-zinc-800 rounded-lg text-sm focus:border-cipher-500 focus:outline-none transition-colors"
                    onKeyDown={(e) => e.key === 'Enter' && handleLogin()}
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-zinc-400 mb-1.5">Password</label>
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full px-4 py-2.5 bg-zinc-900 border border-zinc-800 rounded-lg text-sm focus:border-cipher-500 focus:outline-none transition-colors"
                    onKeyDown={(e) => e.key === 'Enter' && handleLogin()}
                  />
                </div>

                {authError && (
                  <motion.div
                    initial={{ opacity: 0, y: -8 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex items-center gap-2 text-sm text-red-400"
                  >
                    <AlertTriangle className="w-4 h-4" />
                    {authError}
                  </motion.div>
                )}

                <button
                  onClick={handleLogin}
                  disabled={authLoading || !username || !password}
                  className="w-full py-2.5 bg-cipher-600 hover:bg-cipher-500 disabled:opacity-40 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-all text-sm"
                >
                  {authLoading ? 'Authenticating...' : 'Sign in'}
                </button>
              </div>

              <p className="mt-6 text-xs text-zinc-600 text-center">
                Demo: admin / cipherflow-secret
              </p>
            </div>
          </motion.div>
        )}

        {/* ━━ DASHBOARD ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */}
        {view === 'dashboard' && (
          <motion.div
            key="dashboard"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex-1 flex flex-col"
          >
            {/* Top bar */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-zinc-800/60">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-cipher-600/20 flex items-center justify-center">
                  <Shield className="w-4 h-4 text-cipher-400" />
                </div>
                <span className="font-semibold text-sm">CipherFlow</span>
              </div>
              <button
                onClick={() => { clearToken(); setView('landing'); setResult(null); setActiveStage(-1) }}
                className="text-xs text-zinc-500 hover:text-zinc-300 transition-colors"
              >
                Sign out
              </button>
            </div>

            {/* Pipeline Animation Bar */}
            <div className="px-6 py-5 border-b border-zinc-800/40">
              <div className="flex items-center justify-center gap-2 md:gap-4">
                {STAGES.map((stage, i) => {
                  const isActive = activeStage === i
                  const isDone = activeStage > i
                  const isEncryptStage = stage.key === 'encryption'
                  const shouldShow = !isEncryptStage || encrypt

                  if (!shouldShow) return null

                  const Icon = stage.icon
                  return (
                    <div key={stage.key} className="flex items-center gap-2 md:gap-4">
                      {i > 0 && (
                        <ChevronRight className={`w-3.5 h-3.5 transition-colors duration-300 ${isDone ? 'text-zinc-400' : 'text-zinc-700'}`} />
                      )}
                      <motion.div
                        animate={isActive ? {
                          scale: [1, 1.08, 1],
                          transition: { duration: 0.35 },
                        } : {}}
                        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-300 ${
                          isActive
                            ? 'bg-zinc-800 text-white stage-active'
                            : isDone
                              ? 'text-zinc-300'
                              : 'text-zinc-600'
                        }`}
                        style={isActive ? { borderColor: stage.color, borderWidth: 1 } : {}}
                      >
                        <Icon className="w-3.5 h-3.5" style={isActive || isDone ? { color: stage.color } : {}} />
                        <span className="hidden md:inline">{stage.label}</span>
                      </motion.div>
                    </div>
                  )
                })}

                {activeStage >= (encrypt ? 5 : 4) && (
                  <motion.div
                    initial={{ scale: 0, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    className="flex items-center gap-1.5 px-3 py-1.5 bg-green-500/10 border border-green-500/30 rounded-lg text-xs font-medium text-green-400"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    Complete
                  </motion.div>
                )}
              </div>
            </div>

            {/* Split Panes */}
            <div className="flex-1 flex flex-col md:flex-row">

              {/* ── Left: Input ─────────────────────────────────────────── */}
              <div className="flex-1 flex flex-col border-r border-zinc-800/40">
                <div className="px-5 py-3 border-b border-zinc-800/40 flex items-center justify-between">
                  <span className="text-xs font-medium text-zinc-400">Input payload</span>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-zinc-500">Encrypt</span>
                    <button
                      onClick={() => setEncrypt(!encrypt)}
                      className={`w-9 h-5 rounded-full transition-colors relative ${encrypt ? 'bg-cipher-600' : 'bg-zinc-700'}`}
                    >
                      <motion.div
                        animate={{ x: encrypt ? 16 : 2 }}
                        transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                        className="w-3.5 h-3.5 bg-white rounded-full absolute top-[3px]"
                      />
                    </button>
                  </div>
                </div>

                {/* Presets */}
                <div className="px-5 py-3 flex gap-2 border-b border-zinc-800/40">
                  {PRESETS.map((p, i) => (
                    <button
                      key={p.name}
                      onClick={() => loadPreset(i)}
                      className="flex items-center gap-1.5 px-3 py-1.5 bg-zinc-800/50 hover:bg-zinc-800 border border-zinc-700/50 rounded-lg text-xs text-zinc-300 transition-colors"
                    >
                      <span>{p.icon}</span>
                      {p.name}
                    </button>
                  ))}
                </div>

                {/* Record ID */}
                <div className="px-5 py-3 border-b border-zinc-800/40">
                  <label className="text-xs text-zinc-500 mb-1 block">Record ID</label>
                  <input
                    value={recordId}
                    onChange={(e) => setRecordId(e.target.value)}
                    className="w-full px-3 py-1.5 bg-zinc-900/50 border border-zinc-800 rounded text-xs font-mono focus:border-cipher-500 focus:outline-none"
                  />
                </div>

                {/* JSON Editor */}
                <div className="flex-1 p-5">
                  <textarea
                    value={jsonInput}
                    onChange={(e) => setJsonInput(e.target.value)}
                    className="json-input w-full h-full min-h-[300px] bg-zinc-900/30 border border-zinc-800/60 rounded-lg p-4 resize-none focus:border-cipher-500 focus:outline-none text-zinc-200"
                    spellCheck={false}
                  />
                </div>

                {/* Process Button */}
                <div className="px-5 py-4 border-t border-zinc-800/40">
                  <button
                    onClick={handleProcess}
                    disabled={processing}
                    className="w-full py-3 bg-cipher-600 hover:bg-cipher-500 disabled:opacity-50 text-white font-medium rounded-xl transition-all flex items-center justify-center gap-2 text-sm"
                  >
                    {processing ? (
                      <>
                        <motion.div
                          animate={{ rotate: 360 }}
                          transition={{ repeat: Infinity, duration: 1, ease: 'linear' }}
                        >
                          <Cpu className="w-4 h-4" />
                        </motion.div>
                        Processing...
                      </>
                    ) : (
                      <>
                        <Zap className="w-4 h-4" />
                        Process{encrypt ? ' & encrypt' : ''}
                      </>
                    )}
                  </button>
                </div>
              </div>

              {/* ── Right: Output ────────────────────────────────────────── */}
              <div className="flex-1 flex flex-col">
                <div className="px-5 py-3 border-b border-zinc-800/40">
                  <span className="text-xs font-medium text-zinc-400">Processed output</span>
                </div>

                <div className="flex-1 p-5 overflow-y-auto">
                  <AnimatePresence mode="wait">
                    {error && (
                      <motion.div
                        initial={{ opacity: 0, y: 8 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0 }}
                        className="p-4 bg-red-500/10 border border-red-500/20 rounded-lg text-sm text-red-400"
                      >
                        <div className="flex items-center gap-2 mb-1 font-medium">
                          <AlertTriangle className="w-4 h-4" />
                          Error
                        </div>
                        {error}
                      </motion.div>
                    )}

                    {result && (
                      <motion.div
                        initial={{ opacity: 0, y: 12 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0 }}
                        className="space-y-4"
                      >
                        {/* Status header */}
                        <div className="flex items-center gap-3">
                          <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                            result.status === 'success' ? 'bg-green-500/10' : 'bg-red-500/10'
                          }`}>
                            {result.status === 'success'
                              ? <CheckCircle2 className="w-4 h-4 text-green-400" />
                              : <AlertTriangle className="w-4 h-4 text-red-400" />
                            }
                          </div>
                          <div>
                            <p className="text-sm font-medium">{result.record_id}</p>
                            <p className="text-xs text-zinc-500">{result.processed_at}</p>
                          </div>
                          {result.is_encrypted && (
                            <span className="ml-auto flex items-center gap-1 px-2 py-1 bg-pink-500/10 border border-pink-500/20 rounded text-xs text-pink-400">
                              <FileKey className="w-3 h-3" />
                              Encrypted
                            </span>
                          )}
                        </div>

                        {/* Pipeline timing */}
                        <div className="p-3 bg-zinc-900/40 border border-zinc-800/60 rounded-lg">
                          <p className="text-xs text-zinc-500 mb-2">Pipeline stages</p>
                          <div className="space-y-1.5">
                            {result.pipeline.map((stage) => {
                              const cfg = STAGES.find(s => s.key === stage.name)
                              return (
                                <div key={stage.name} className="flex items-center justify-between text-xs">
                                  <span className="text-zinc-300 capitalize">{stage.name}</span>
                                  <span className="text-zinc-500 font-mono">{stage.duration_ms.toFixed(2)}ms</span>
                                </div>
                              )
                            })}
                          </div>
                        </div>

                        {/* Checksum */}
                        <div className="p-3 bg-zinc-900/40 border border-zinc-800/60 rounded-lg">
                          <p className="text-xs text-zinc-500 mb-1">SHA-256 checksum</p>
                          <p className="text-xs font-mono text-cipher-400 break-all">{result.checksum}</p>
                        </div>

                        {/* Data output */}
                        {result.processed_data && (
                          <div className="p-3 bg-zinc-900/40 border border-zinc-800/60 rounded-lg">
                            <p className="text-xs text-zinc-500 mb-2">Processed data</p>
                            <pre className="json-input text-xs text-zinc-200 whitespace-pre-wrap">
                              {JSON.stringify(result.processed_data, null, 2)}
                            </pre>
                          </div>
                        )}

                        {result.encrypted_blob && (
                          <div className="p-3 bg-zinc-900/40 border border-zinc-800/60 rounded-lg">
                            <p className="text-xs text-zinc-500 mb-2">Encrypted blob (Fernet)</p>
                            <p className="text-xs font-mono text-pink-400 break-all leading-relaxed">
                              {result.encrypted_blob}
                            </p>
                          </div>
                        )}

                        {/* Warnings */}
                        {result.warnings.length > 0 && (
                          <div className="p-3 bg-amber-500/10 border border-amber-500/20 rounded-lg">
                            <p className="text-xs text-amber-400 mb-1 font-medium">Warnings</p>
                            {result.warnings.map((w, i) => (
                              <p key={i} className="text-xs text-amber-300/70">{w}</p>
                            ))}
                          </div>
                        )}
                      </motion.div>
                    )}

                    {!result && !error && (
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="h-full flex items-center justify-center text-zinc-700 text-sm"
                      >
                        <div className="text-center">
                          <Eye className="w-8 h-8 mx-auto mb-3 opacity-30" />
                          <p>Processed output appears here</p>
                          <p className="text-xs mt-1 text-zinc-800">Select a preset and click Process</p>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              </div>
            </div>

            {/* ━━ HEALTH BAR ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */}
            <div className="px-6 py-2.5 border-t border-zinc-800/40 flex items-center justify-between text-xs text-zinc-500">
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-1.5">
                  <div className={`w-1.5 h-1.5 rounded-full ${health?.status === 'ok' ? 'bg-green-400 health-dot' : 'bg-red-400'}`} />
                  <span>{health?.status === 'ok' ? 'API healthy' : 'API unreachable'}</span>
                </div>
                {health && (
                  <>
                    <span>v{health.version}</span>
                    <span>Uptime: {Math.floor(health.uptime_seconds / 60)}m</span>
                  </>
                )}
              </div>
              <span className="text-zinc-700">CipherFlow 2.0</span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
