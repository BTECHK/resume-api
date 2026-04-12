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
# SEC-04 base image pinning:
#   - Tags are used for local dev ergonomics; CI should rewrite to digest form
#     before build. To refresh digests:
#       docker pull node:20-alpine
#       docker inspect --format='{{index .RepoDigests 0}}' node:20-alpine
#       docker pull nginx:1.27-alpine
#       docker inspect --format='{{index .RepoDigests 0}}' nginx:1.27-alpine
#   - Bumping to nginx:1.28-alpine is API-compatible and does not require fixup changes

# -- Stage 1: build ---------------------------------------------
FROM node:20-alpine AS build

WORKDIR /app

# Copy package files first for better layer caching
COPY package.json package-lock.json ./
RUN npm ci

# Copy source and build
COPY . .

RUN npm run build

# -- Stage 2: serve ---------------------------------------------
FROM nginx:1.27-alpine AS runtime

# Copy our nginx.conf and config template
COPY nginx.conf /etc/nginx/nginx.conf
COPY config.json.template /etc/nginx/config.json.template

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

# At startup: envsubst renders config.json from env vars, then nginx starts
CMD ["/bin/sh", "-c", "envsubst < /etc/nginx/config.json.template > /usr/share/nginx/html/config.json && nginx -g 'daemon off;'"]
