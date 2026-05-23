from dataclasses import dataclass, field


@dataclass
class RetryConfig:
    max_retries: int = 0
    backoff_factor: float = 1.0
    retry_on_status: tuple[int, ...] = (502, 503, 504)
    # Only idempotent methods by default; add "POST"/"PATCH" only if the endpoint is idempotency-safe.
    allowed_methods: tuple[str, ...] = ("HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE")


@dataclass
class ClientConfig:
    base_url: str
    timeout: int = 30
    verify_ssl: bool = False
    default_headers: dict[str, str] = field(
        default_factory=lambda: {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
    )
    retry: RetryConfig = field(default_factory=RetryConfig)
