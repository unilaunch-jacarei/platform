use crate::AppState;
use axum::{
    body::Body,
    extract::State,
    http::{Request, StatusCode},
    middleware::Next,
    response::{IntoResponse, Response},
};
use hmac::{Hmac, KeyInit, Mac};
use sha2::Sha256;
use std::time::{SystemTime, UNIX_EPOCH};

type HmacSha256 = Hmac<Sha256>;

fn verify_signature(
    path: &str,
    user_id: &str,
    timestamp: i64,
    signature: &[u8],
    secret: &[u8],
    now: i64,
) -> bool {
    if (now - timestamp).abs() > 30 {
        return false;
    }
    let payload = format!("{}:{}:{}", timestamp, path, user_id);
    let Ok(mut mac) = HmacSha256::new_from_slice(secret) else {
        return false;
    };
    mac.update(payload.as_bytes());
    mac.verify_slice(signature).is_ok()
}

/// Valida a identidade do BFF e injeta o `user_id` autenticado na request.
pub async fn verify_internal_request(
    State(state): State<AppState>,
    request: Request<Body>,
    next: Next,
) -> Response {
    let unauthorized = || StatusCode::UNAUTHORIZED.into_response();
    let Some(user_id) = request
        .headers()
        .get("x-user-id")
        .and_then(|v| v.to_str().ok())
        .map(str::to_owned)
    else {
        return unauthorized();
    };
    let Some(timestamp) = request
        .headers()
        .get("x-timestamp")
        .and_then(|v| v.to_str().ok())
        .and_then(|v| v.parse::<i64>().ok())
    else {
        return unauthorized();
    };
    let Some(signature) = request
        .headers()
        .get("x-signature")
        .and_then(|v| v.to_str().ok())
        .and_then(|v| hex::decode(v).ok())
    else {
        return unauthorized();
    };
    let Ok(now) = SystemTime::now().duration_since(UNIX_EPOCH) else {
        return unauthorized();
    };
    let now = now.as_secs() as i64;
    if !verify_signature(
        request.uri().path(),
        &user_id,
        timestamp,
        &signature,
        state.internal_secret.as_bytes(),
        now,
    ) {
        return unauthorized();
    }

    let mut request = request;
    request.extensions_mut().insert(user_id);
    next.run(request).await
}

#[cfg(test)]
mod tests {
    use super::*;

    fn signature(path: &str, user_id: &str, timestamp: i64, secret: &[u8]) -> Vec<u8> {
        let mut mac = HmacSha256::new_from_slice(secret).unwrap();
        mac.update(format!("{}:{}:{}", timestamp, path, user_id).as_bytes());
        mac.finalize().into_bytes().to_vec()
    }

    #[test]
    fn accepts_valid_signature_and_clock_boundaries() {
        let secret = b"test-secret";
        let sig = signature("/api/v1/usuarios/1", "user-1", 1_000, secret);
        assert!(verify_signature(
            "/api/v1/usuarios/1",
            "user-1",
            1_000,
            &sig,
            secret,
            1_030
        ));
        assert!(verify_signature(
            "/api/v1/usuarios/1",
            "user-1",
            1_000,
            &sig,
            secret,
            970
        ));
    }

    #[test]
    fn rejects_expired_future_and_invalid_signatures() {
        let secret = b"test-secret";
        let sig = signature("/api/v1/usuarios/1", "user-1", 1_000, secret);
        assert!(!verify_signature(
            "/api/v1/usuarios/1",
            "user-1",
            1_000,
            &sig,
            secret,
            1_031
        ));
        assert!(!verify_signature(
            "/api/v1/usuarios/1",
            "user-1",
            1_000,
            &sig,
            secret,
            969
        ));
        assert!(!verify_signature(
            "/api/v1/usuarios/2",
            "user-1",
            1_000,
            &sig,
            secret,
            1_000
        ));
        assert!(!verify_signature(
            "/api/v1/usuarios/1",
            "user-2",
            1_000,
            &sig,
            secret,
            1_000
        ));
        assert!(!verify_signature(
            "/api/v1/usuarios/1",
            "user-1",
            1_000,
            &sig,
            b"wrong",
            1_000
        ));
        assert!(!verify_signature(
            "/api/v1/usuarios/1",
            "user-1",
            1_000,
            &[],
            secret,
            1_000
        ));
    }
}
