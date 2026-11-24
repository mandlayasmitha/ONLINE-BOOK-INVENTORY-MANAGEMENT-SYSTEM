# Venu Compiler Architecture

## Components

1. Monaco editor sends source, input, language, and benchmark options to FastAPI.
2. Static analyzer parses Python source with `ast.parse` and applies loop, recursion, allocation, and sorting rules.
3. Execution adapter runs Python in a temporary directory. Development mode is explicitly warned as unsafe.
4. Benchmark endpoint repeats execution across input sizes and returns average, median, minimum, maximum, and raw timings.
5. React dashboard combines static findings with runtime output and charts.

## Database entities

- `users`: id, email, password_hash, profile fields
- `code_submissions`: id, user_id, language, source, input
- `analysis_results`: id, submission_id, time estimate, space estimate, confidence, findings
- `benchmark_runs`: id, submission_id, input_sizes, measurements
- `saved_programs`: id, user_id, title, language, source
- `quiz_attempts`: id, user_id, question_id, selected_answer, correct

This scaffold includes PostgreSQL configuration but persistence adapters and JWT handlers should be enabled before a multi-user deployment.

## Complexity conventions

The static estimate is a rule-based explanation, not a mathematical proof. Runtime measurements are empirical and do not prove Big-O. Input memory is reported separately from auxiliary memory, and recursion stack memory is reported separately.
