from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .schemas import AnalyzeRequest, ExecuteRequest, BenchmarkRequest
from .static_analyzer import analyze
from .execution import execute_python
import statistics

RUNTIME_PACKAGES = [
    {"name": "numpy", "import_statement": "import numpy as np", "version": "2.2.6"},
    {"name": "pandas", "import_statement": "import pandas as pd", "version": "2.2.3"},
    {"name": "requests", "import_statement": "import requests", "version": "2.32.3"},
    {"name": "sympy", "import_statement": "import sympy", "version": "1.14.0"},
]


app = FastAPI(title="Venu Compiler", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://codecomplexity-analyzer.vercel.app",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok", "security": "development mode"}


@app.get("/api/packages")
def packages():
    return {"packages": RUNTIME_PACKAGES}


@app.post("/api/analyze/static")
def analyze_static(request: AnalyzeRequest):
    if request.language != "python":
        raise HTTPException(400, "Only Python is supported in phase 1.")
    return analyze(request.source)


@app.post("/api/execute")
def execute(request: ExecuteRequest):
    if request.language != "python":
        raise HTTPException(400, "Only Python is supported in phase 1.")
    return execute_python(request.source, request.input, request.timeout_ms)


@app.post("/api/analyze/hybrid")
def hybrid(request: ExecuteRequest):
    static = analyze(request.source)
    runtime = execute_python(request.source, request.input, request.timeout_ms)
    return {"static": static, "runtime": runtime}


@app.post("/api/benchmark")
def benchmark(request: BenchmarkRequest):
    samples = []
    for size in sorted(set(request.sizes)):
        timings = []
        for _ in range(request.repeats):
            generated = "n = " + str(size) + "\n" + request.source
            runtime = execute_python(generated, "", 5000)
            if runtime["status"] == "success":
                timings.append(runtime["executionTimeMs"])
        samples.append({
            "inputSize": size,
            "averageMs": round(statistics.mean(timings), 3) if timings else None,
            "minimumMs": round(min(timings), 3) if timings else None,
            "maximumMs": round(max(timings), 3) if timings else None,
            "medianMs": round(statistics.median(timings), 3) if timings else None,
            "samples": timings,
        })
    static = analyze(request.source)
    return {
        "empirical": samples,
        "static": static,
        "notice": "Empirical complexity estimate — based on benchmark measurements, not an exact proof.",
        "confidence": "Low" if len(samples) < 4 else "Medium",
    }
