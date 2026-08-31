use crate::application::auth::ports::{RateLimitOperation, RateLimiterPort};
use async_trait::async_trait;
use std::{
    collections::HashMap,
    net::IpAddr,
    time::{Duration, Instant},
};
use tokio::sync::Mutex;

#[derive(Debug)]
pub struct RateLimitWindow {
    pub started_at: Instant,
    pub count: u32,
}

pub struct MemoryRateLimiter {
    records: Mutex<HashMap<(IpAddr, RateLimitOperation), RateLimitWindow>>,
}

impl MemoryRateLimiter {
    pub fn new() -> Self {
        Self {
            records: Mutex::new(HashMap::new()),
        }
    }
}

impl Default for MemoryRateLimiter {
    fn default() -> Self {
        Self::new()
    }
}

#[async_trait]
impl RateLimiterPort for MemoryRateLimiter {
    async fn is_allowed(
        &self,
        ip: IpAddr,
        operation: RateLimitOperation,
        window: Duration,
        max_attempts: u32,
    ) -> bool {
        let now = Instant::now();
        let mut records = self.records.lock().await;
        let key = (ip, operation);

        let record = records.entry(key).or_insert(RateLimitWindow {
            started_at: now,
            count: 0,
        });

        if now.duration_since(record.started_at) >= window {
            record.started_at = now;
            record.count = 0;
        }

        if record.count >= max_attempts {
            return false;
        }

        record.count += 1;
        true
    }

    async fn reset(&self, ip: IpAddr, operation: RateLimitOperation) {
        self.records.lock().await.remove(&(ip, operation));
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use tokio::time::{Duration as TokioDuration, sleep};

    fn local_ip() -> IpAddr {
        "127.0.0.1".parse().unwrap()
    }

    #[tokio::test]
    async fn limits_attempts_by_ip_and_operation() {
        let limiter = MemoryRateLimiter::new();
        let ip = local_ip();
        let window = Duration::from_secs(60);

        assert!(
            limiter
                .is_allowed(ip, RateLimitOperation::Login, window, 2)
                .await
        );
        assert!(
            limiter
                .is_allowed(ip, RateLimitOperation::Login, window, 2)
                .await
        );
        assert!(
            !limiter
                .is_allowed(ip, RateLimitOperation::Login, window, 2)
                .await
        );

        assert!(
            limiter
                .is_allowed(ip, RateLimitOperation::ResetPassword, window, 2)
                .await
        );
    }

    #[tokio::test]
    async fn reset_and_window_expiration_allow_new_attempts() {
        let limiter = MemoryRateLimiter::new();
        let ip = local_ip();

        assert!(
            limiter
                .is_allowed(ip, RateLimitOperation::Login, Duration::from_secs(60), 1)
                .await
        );
        assert!(
            !limiter
                .is_allowed(ip, RateLimitOperation::Login, Duration::from_secs(60), 1)
                .await
        );

        limiter.reset(ip, RateLimitOperation::Login).await;
        assert!(
            limiter
                .is_allowed(ip, RateLimitOperation::Login, Duration::from_secs(60), 1)
                .await
        );

        assert!(
            limiter
                .is_allowed(
                    ip,
                    RateLimitOperation::Register,
                    Duration::from_millis(1),
                    1
                )
                .await
        );
        assert!(
            !limiter
                .is_allowed(
                    ip,
                    RateLimitOperation::Register,
                    Duration::from_millis(1),
                    1
                )
                .await
        );
        sleep(TokioDuration::from_millis(2)).await;
        assert!(
            limiter
                .is_allowed(
                    ip,
                    RateLimitOperation::Register,
                    Duration::from_millis(1),
                    1
                )
                .await
        );
    }
}
