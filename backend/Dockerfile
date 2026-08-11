FROM rust:1.97-bookworm AS builder

WORKDIR /app
COPY backend/Cargo.toml backend/Cargo.lock ./backend/

WORKDIR /app/backend
ENV SQLX_OFFLINE=true
RUN mkdir src \
    && printf 'fn main() {}\n' > src/main.rs \
    && cargo build --locked --release \
    && rm -rf src

COPY backend/.sqlx ./.sqlx
COPY backend/migrations ./migrations
COPY backend/src ./src
RUN cargo build --locked --release

FROM debian:bookworm-slim AS runtime

ARG APP_VERSION=unknown
LABEL org.opencontainers.image.version=$APP_VERSION

RUN apt-get update \
    && apt-get install --no-install-recommends -y ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/backend/target/release/backend /usr/local/bin/backend

ENV BIND_ADDR=0.0.0.0:3000
EXPOSE 3000
USER 10001:10001
ENTRYPOINT ["/usr/local/bin/backend"]
