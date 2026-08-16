from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class RunResult:
    name: str
    status: str
    rows: int
    cols: int
    error: str | None = None
    executed_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
