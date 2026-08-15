from dataclasses import dataclass

@dataclass
class RunResult:
    name: str
    status: str
    rows: int
    cols: int
    error: str | None = None
