# ═══════════════════════════════════════════════════════════════════════════════
# CipherFlow Frontend — Multi-Stage Production Dockerfile
# ═══════════════════════════════════════════════════════════════════════════════
# Stage 1: Install dependencies
# Stage 2: Build the Next.js application
# Stage 3: Run with minimal Node.js runtime
# Result: ~150MB image with standalone output
# ═══════════════════════════════════════════════════════════════════════════════

# ── Stage 1: Dependencies ────────────────────────────────────────────────────
FROM node:20-alpine AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app
COPY package.json ./
RUN npm install --frozen-lockfile 2>/dev/null || npm install

# ── Stage 2: Build ───────────────────────────────────────────────────────────
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
ENV NEXT_TELEMETRY_DISABLED=1

RUN npm run build

# ── Stage 3: Runtime ─────────────────────────────────────────────────────────
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Security: run as non-root with no shell
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 --shell /bin/false nextjs

# Security: remove unnecessary system packages
RUN apk --no-cache del apk-tools

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Security: make app files read-only
RUN chmod -R 555 /app

USER nextjs

EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]

# ── Labels ───────────────────────────────────────────────────────────────────
LABEL maintainer="Ashish Khatri <1060ashish@gmail.com>"
LABEL org.opencontainers.image.source="https://github.com/asisqt/cipherflow"
LABEL org.opencontainers.image.description="CipherFlow dashboard — Next.js frontend"
LABEL org.opencontainers.image.version="2.0.0"
