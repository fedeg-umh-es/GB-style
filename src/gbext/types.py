from dataclasses import dataclass, field
from typing import Any

@dataclass
class Stats:
    total_time: float = 0.0
    accumulation_time: float = 0.0
    reduction_time: float = 0.0
    mul_count: int = 0
    red_count: int = 0
    branch_count: int = 0
    data_dependent_branch_count: int = 0
    memory_access_proxy: int = 0
    iteration_count: int = 0
    notes: list[str] = field(default_factory=list)

@dataclass
class Context:
    track_timing: bool = True
    track_branches: bool = False
    track_memory: bool = False
    stats: Stats = field(default_factory=Stats)
    meta: dict[str, Any] = field(default_factory=dict)
