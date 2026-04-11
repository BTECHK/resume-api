# syntax=docker/dockerfile:1.7
#
# Multi-stage Dockerfile for the resume-chatbot frontend.
#
# Stage 1 (build):  node:20-alpine — installs deps, runs `vite build`
# Stage 2 (runtime): nginx:1.27-alpine — serves the static dist/ on :8080
#
# Non-root hardening (RESEARCH Pitfall #5):
#   - PID file at /tmp/nginx.pid (default /var/run/nginx.pid is not writable by nginx user)
#   - chown runtime-writable dirs to nginx:nginx
#   - USER nginx at the end (drop root)
#
# Image size target: <50MB total. nginx:1.27-alpine base ~24MB + Vite dist ~300-500KB.
#
# Build-time env vars: Vite inlines VITE_* vars at build time (RESEARCH Pitfall #4).
# To change them, REBUILD the image — restarting the container will not pick up new values.
#
# Phase 8 hardening notes:
#   - Pin both base images by digest (currently pinned by tag)
#   - Bumping to nginx:1.28-alpine is API-compatible and does not require fixup changes

# -- Stage 1: build ---------------------------------------------
FROM node:20-alpine AS build

WORKDIR /app

# Copy package files first for better layer caching
COPY package.json package-lock.json ./
RUN npm ci

# Copy source and build
COPY . .

# Build-time env vars are read from the build environment;
# Cloud Build / local docker build must pass them via --build-arg
ARG VITE_AI_SERVICE_URL
ARG VITE_CANDIDATE_NAME
ARG VITE_CANDIDATE_TITLE
ARG VITE_CANDIDATE_EMAIL
ENV VITE_AI_SERVICE_URL=${VITE_AI_SERVICE_URL}
ENV VITE_CANDIDATE_NAME=${VITE_CANDIDATE_NAME}
ENV VITE_CANDIDATE_TITLE=${VITE_CANDIDATE_TITLE}
ENV VITE_CANDIDATE_EMAIL=${VITE_CANDIDATE_EMAIL}

RUN npm run build

# -- Stage 2: serve ---------------------------------------------
FROM nginx:1.27-alpine AS runtime

# Copy our nginx.conf over the default
COPY nginx.conf /etc/nginx/nginx.conf

# Copy the built static files
COPY --from=build /app/dist /usr/share/nginx/html

# Non-root hardening (Pitfall #5):
# 1) PID file location fix (default /var/run/nginx.pid is not writable by nginx user)
# 2) Chown runtime-writable dirs to nginx user
# 3) Switch to non-root user
RUN touch /tmp/nginx.pid && \
    chown -R nginx:nginx /var/cache/nginx /var/log/nginx /tmp/nginx.pid /usr/share/nginx/html && \
    chmod -R g=u /var/cache/nginx /var/log/nginx /tmp/nginx.pid

USER nginx

EXPOSE 8080
STOPSIGNAL SIGQUIT

CMD ["nginx", "-g", "daemon off;"]
