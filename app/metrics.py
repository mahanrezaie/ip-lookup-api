from prometheus_client import Counter, Histogram

HTTP_REQUESTS_TOTAL = Counter(
    "ip_lookup_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "ip_lookup_http_request_duration_seconds",
    "Request duration in seconds",
    ["endpoint"]
)
