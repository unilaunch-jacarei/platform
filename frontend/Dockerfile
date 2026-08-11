FROM oven/bun:1.3 AS builder

WORKDIR /app
COPY frontend/package.json frontend/bun.lock ./
RUN bun install --frozen-lockfile

COPY frontend .
RUN bun run check && bun run build

FROM node:24-alpine AS runtime

ARG APP_VERSION=unknown
LABEL org.opencontainers.image.version=$APP_VERSION

WORKDIR /app
ENV NODE_ENV=production
ENV HOST=0.0.0.0
ENV PORT=3000

COPY --from=builder /app/build ./build

EXPOSE 3000
USER bun
CMD ["node", "build"]
