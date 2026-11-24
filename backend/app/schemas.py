from pydantic import BaseModel, Field
from typing import Literal


class AnalyzeRequest(BaseModel):
    language: Literal["python"] = "python"
    source: str = Field(min_length=1, max_length=100_000)


class ExecuteRequest(AnalyzeRequest):
    input: str = ""
    timeout_ms: int = Field(default=3000, ge=100, le=10000)


class BenchmarkRequest(AnalyzeRequest):
    sizes: list[int] = Field(default=[100, 500, 1000, 5000, 10000])
    repeats: int = Field(default=3, ge=1, le=10)
