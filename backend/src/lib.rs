pub mod adapters;
pub mod application;
pub mod bootstrap;
pub mod domain;

pub use adapters::inbound::http::{AppState, build_http_router};
pub use bootstrap::{AppConfig, ApplicationContainer, build_app, create_app_state};
