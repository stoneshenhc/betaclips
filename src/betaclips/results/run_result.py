from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class RunResult:
    job_name: str
    success: bool
    rows: int | None
    cols: int | None
    error: str | None = None
    executed_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
