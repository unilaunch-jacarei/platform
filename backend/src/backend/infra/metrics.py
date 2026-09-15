from prometheus_client import Counter, Histogram

http_requests = Counter(
    "http_requests_total",
    "Total de requisições HTTP processadas",
    ("method", "route", "status_code"),
)
http_request_errors = Counter(
    "http_request_errors_total",
    "Total de respostas HTTP 4xx e 5xx",
    ("method", "route", "status_class"),
)
http_request_duration = Histogram(
    "http_request_duration_seconds",
    "Duração das requisições HTTP em segundos",
    ("method", "route"),
)
